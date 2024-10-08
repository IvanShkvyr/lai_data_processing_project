from collections import namedtuple
from datetime import datetime, timedelta
from pathlib import Path
import pickle
from typing import List, Tuple, Union

import numpy as np
import pandas as pd
import rasterio
from rasterio.warp import reproject, Resampling

from decorators import measure_time
from file_management import grab_raw_lai_data_files, ensure_directory_exists
from raster_processing import (
    read_raster,
    create_template_raster,
    convert_hdr_to_tif,
    save_lai_to_raster,
    cut_land_use_file_path,
    DEFAULT_TEMP_DIR,
    DEFAULT_TEMP_RASTER_NAME
)
from statistics_processing import calculate_mean_and_boxplot_lai

# Define a named tuple for the results of the
# process_lai_files_and_extract_data function
LAIRecord = namedtuple(
    "LAIRecord",
    [
        "Date",
        "Landuse",
        "Elevation_class",
        "Average_LAI",
        "Min",
        "Q1",
        "Median",
        "Q3",
        "Max",
        "Lower_Whisker",
        "Upper_Whisker",
    ],
)

DEFAULT_TEMP_LAI_DIR ="temp\\temp_lai_unifited"
DEFAULT_TEMP_LANDUSE_NAME = "unifited_landuse"
DEFAULT_MODIFY_LAI_FOLDER = "results\\modify_lai"
DEFAULT_UNMODIFY_FOLDER = "results\\unmodify_data"


def copy_data_to_template(
    template_raster: Path,
    source_file: Path,
    output_folder: str = DEFAULT_TEMP_DIR,
    filename: str | None = None,
) -> Path:
    """
    Resamples data from source_file to match the extent and resolution of
    template_raster, and copies non-zero values to output_file.

    Parameters:
        template_raster ( Path): Path to the template raster file used for the
          extent and resolution.
        source_file (Path): Path to the input raster file containing data to be
          resampled.
        output_folder (str): Path to the folder where the output file will
          be saved.
        filename (str, optional): Name of the output file. If not provided,
          '_unifited' will be appended to the template file's name.

    Returns:
         Path: Path to the output raster file.
    """

    from file_management import ensure_directory_exists
    # Define the Path object for the output folder
    output_folder_path = ensure_directory_exists(output_folder)

    # Determine the output filename
    if filename is None:
        # Extract the base name without extension and add the suffix
        base_name = Path(source_file).stem
        filename = f"{base_name}_unifited.tif"
    else:
        # Ensure the filename has a .tif extension
        filename = f"{filename}.tif"

    # Define the full path to the output file
    unifited_file = output_folder_path / filename

    with rasterio.open(template_raster) as dst_zeros:
        # Open the raster with zero values (dst_zeros)
        dst_crs = dst_zeros.crs
        dst_transform = dst_zeros.transform
        dst_shape = dst_zeros.shape

        # Open the raster with data (source_file)
        with rasterio.open(source_file) as src:
            src_crs = src.crs
            src_transform = src.transform

            # Create a new raster ('unifited_file') matching the template
            #  raster ('dst_zeros')
            with rasterio.open(
                unifited_file,
                "w",
                driver="GTiff",
                height=dst_shape[0],
                width=dst_shape[1],
                count=src.count,
                dtype=src.dtypes[0],
                crs=dst_crs,
                transform=dst_transform,
            ) as data_resampled:

                # Resample data using nearest neighbor interpolation
                for i in range(1, src.count + 1):
                    reproject(
                        source=rasterio.band(src, i),
                        destination=rasterio.band(data_resampled, i),
                        src_transform=src_transform,
                        src_crs=src_crs,
                        dst_transform=dst_transform,
                        dst_crs=dst_crs,
                        resampling=Resampling.nearest,
                    )

        # Copy resampled data to the output raster
        with rasterio.open(unifited_file, "r+") as dst_out:
            with rasterio.open(unifited_file) as data_resampled:
                for i in range(1, data_resampled.count + 1):
                    band_data = data_resampled.read(i)
                    dst_band_data = dst_zeros.read(i)

                    # Copy non-zero values from resampled raster
                    # to output raster
                    dst_band_data[band_data != 0] = band_data[band_data != 0]
                    dst_out.write(dst_band_data, i)

    return unifited_file


def classify_elevation(
    unified_dem: Path,
    elevation_bins: List[int] = None
) -> Tuple[np.ndarray, List[str]]:
    """
    Classify elevation data into different zones based on provided elevation
    thresholds. If no thresholds are provided, they will be automatically
    generated in multiples of 100.

    Parameters:
        unified_dem (Path): Path to the raster file containing the elevation
          data.
        elevation_bins (List[int]): List of elevation thresholds for
         classification. Elevation values will be categorized into bins defined
         by these thresholds. If None, thresholds will be generated in
         multiples of 100 based on the data range.

    Returns:
       numpy.ndarray: An array with the same shape as the input elevation data,
            where each value represents the elevation zone according to the
            provided thresholds.
       List[str]: A list of labels for the elevation zones, describing the
            range of each zone.
    """

    # Read the elevation data from the raster file
    unified_dem_data = read_raster(unified_dem)
    
    # Determine min and max elevation values
    min_elevation = np.min(unified_dem_data)
    max_elevation = np.max(unified_dem_data)
    
    # Automatically generate bins if elevation_bins is None
    if elevation_bins is None:
        min_bin = (int(np.floor(min_elevation / 100)) + 1) * 100
        max_bin = (int(np.ceil(max_elevation / 100))) * 100
        elevation_bins = list(range(min_bin, max_bin, 100))

    # Classify elevation data into bins
    elevation_classes = (
        np.digitize(unified_dem_data, bins=elevation_bins, right=True) + 1
    )

    # Generate labels for each elevation zone
    elevation_labels = (
        [f"less_than_{elevation_bins[0]}"]
        + [
            f"{elevation_bins[i-1]}-{elevation_bins[i]}"
            for i in range(1, len(elevation_bins))
        ]
        + [f"greater_than_{elevation_bins[-1]}"]
    )

    return elevation_classes, elevation_labels, elevation_bins


def extract_date_from_filename(filename: Path) -> datetime:
    """
    Extract date from a filename assuming the pattern
    '<prefix>_<YYYYDDD>_suffix'.

    Parameters:
        filename (Path): Path object representing the LAI file name.

    Returns:
        datetime: The date extracted from the filename.
    """
    # Extract the date string (YYYYDDD) from the filename
    date_str = filename.stem.split("_")[1]

    # Extract the year and day of year from the date string
    year = int(date_str[:4])
    day_of_year = int(date_str[4:7])

    # Calculate the date based on the year and day of year
    date = datetime(year, 1, 1) + timedelta(days=day_of_year - 1)

    return date


def process_lai_files_and_extract_data(
    unified_lai_list: List[Path],
    land_use_file_path: str,
    elevation_classes: np.ndarray,
    elevation_labels: List[str],
) -> List[LAIRecord]:
    """
    Process LAI (Leaf Area Index) raster files and extract mean LAI value based
    on land use and elevation classes.

    This function reads LAI raster files, extracts date information from
    filenames, and computes the mean LAI values and boxplot statistics for
    different land use and elevation classes. The results are compiled into a
    list of records containing the date, land use class, elevation class, mean
    LAI value, and boxplot statistics.

    Parameters:
        unified_lai_list (list of Path): A list of Path objects pointing to the
          LAI raster files that have been resampled to a uniform template.
        land_use_file_path (str or Path): Path to the land use raster file used
          to classify land use types.
        elevation_classes (numpy.ndarray): A 2D array representing elevation
          classes, where each pixel value indicates the elevation class of that
          location.
        elevation_labels (list of str): A list of labels describing each
          elevation class.

    Returns:
    List[LAIRecord]: A list of records, where each record is a list containing:
                - Date (datetime): The date extracted from the LAI file name.
                - Landuse (int): The land use class.
                - Elevation_class (str): The label of the elevation class.
                - average_LAI (float): The mean LAI value for the corresponding
                  land use and elevation class.
                - Min (float): Minimum LAI value.
                - Q1 (float): First quartile.
                - Median (float): Median (second quartile).
                - Q3 (float): Third quartile.
                - Max (float): Maximum LAI value.
                - Lower Whisker (float): Lower whisker value.
                - Upper Whisker (float): Upper whisker value.
                - Outliers (list): List of outlier values.

    Notes:
        - The date is extracted from the LAI file name, assuming the file name
          follows the pattern '<prefix>_<YYYYDDD>_suffix'. where YYYY is the
          year and DDD is the day of the year.
        - The function assumes that the land use and elevation rasters have the
          same spatial resolution and extent as the LAI rasters.
    """
    # Read the land use data from the specified raster file
    landuse = read_raster(Path(land_use_file_path))
    # Get unique land use classes present in the raster
    unique_landuse_classes = np.unique(landuse)

    data = []
    for lai_file in unified_lai_list:
        # Extract date information from the LAI file name
        date = extract_date_from_filename(lai_file)

        # Read LAI data from the current file
        lai_data = read_raster(lai_file)

        # Loop through each unique land use class
        for landuse_class in unique_landuse_classes:
            # Loop through each elevation class
            for elev_class in range(1, len(elevation_labels) + 1):
                # Calculate mean LAI and boxplot statistics for the current
                # land use and elevation class
                stats = calculate_mean_and_boxplot_lai(
                    lai_data, landuse,
                    elevation_classes,
                    landuse_class, elev_class
                )
                if stats is not None:
                    data.append(
                        [
                            date,
                            landuse_class,
                            elevation_labels[elev_class - 1],
                            stats["Mean_LAI"],
                            stats["Min"],
                            stats["Q1"],
                            stats["Median"],
                            stats["Q3"],
                            stats["Max"],
                            stats["Lower Whisker"],
                            stats["Upper Whisker"],
                        ]
                    )

    return data


def filter_lai_data_by_landuse(
    data: List[LAIRecord],
    land_use_classes_of_interest: List[int] | None = None
) -> pd.DataFrame:
    """
    Creates a DataFrame from the provided LAI data and filters it based on
    specified land use classes.

    This function constructs a pandas DataFrame from the input data, which
    should include columns for date, land use, elevation class, and average LAI
    values. It then filters the DataFrame to include only the rows where the
    land use class is in the list of land use classes of interest.

    Parameters:
        data (List[LAIRecord]): The raw data to be converted into a DataFrame.
                             Each entry should be a list containing date, land
                             use class, elevation class, and average LAI value.
        land_use_classes_of_interest (Optional[List[int]]): A list of land use
                             classes that should be included in the filtered
                             DataFrame.
                             Defaults to None, which means all classes except 0
                             will be included.

    Returns:
        pd.DataFrame: A filtered DataFrame containing only rows with land use
         classes specified in land_use_classes_of_interest.

    Notes:
        - The DataFrame columns are named as 'Date', 'Landuse',
          'Elevation_class', and 'average_LAI'.
    """
    # Create a DataFrame from the provided data with specified columns
    df_full = pd.DataFrame(
        data,
        columns=[
            "Date",
            "Landuse",
            "Elevation_class",
            "Mean_LAI",
            "Min",
            "Q1",
            "Median",
            "Q3",
            "Max",
            "Lower Whisker",
            "Upper Whisker",
        ],
    )

    # Convert the 'Landuse' column to integer type
    df_full["Landuse"] = df_full["Landuse"].astype(int)

    # If land_use_classes_of_interest is None, filter out only land use class 0
    if land_use_classes_of_interest is None:
        data_frame = df_full[df_full["Landuse"] != 0].copy()
    else:
        # Filter the DataFrame to include only rows where 'Landuse' is in the
        # specified list
        data_frame = df_full[
            df_full["Landuse"].isin(land_use_classes_of_interest)
        ].copy()

    return data_frame


# @measure_time
def process_lai_data( 
    lai_folder_path: str,
    land_use_file_path: str,
    dem_file_path: str,
    elevation_bins: List[int],
    land_use_classes_of_interest: List[int] | None = None,
    aoi_boundary_file: str | None = None,
    ) -> Tuple[pd.DataFrame, List[Union[List[str], np.ndarray, List[str]]]]:
    """
    Process LAI (Leaf Area Index) data and prepare it for analysis. This
    function handles reading, converting, resampling, and classifying LAI data
    along with land use and elevation data.

    The workflow includes:
    - Converting raw LAI files from HDR format to TIFF.
    - Resampling the digital elevation model (DEM) and LAI data to match a
      template raster derived from land use data.
    - Classifying elevation zones based on provided elevation bins.
    - Extracting and filtering data based on land use and elevation classes.

    Parameters:
        lai_folder_path (str or Path): Path to the folder containing raw LAI
          data files in HDR format.
        land_use_file_path (str or Path): Path to the land use raster file,
          which is used to create the template raster for resampling.
        dem_file_path (str or Path): Path to the digital elevation model (DEM)
          file that will be resampled to match the template raster.
        elevation_bins (list of int): Threshold values for classifying
          elevation zones.
        land_use_classes_of_interest (list of int, optional): List of specific
          land use classes to filter in the final extracted data. If None, all
          land use classes will be included.
        aoi_boundary_file (str or Path, optional): Path to the shapefile
          representing the area of interest (AOI). If provided, the land use
          raster will be cropped to this boundary.

    Returns:
        pd.DataFrame: A DataFrame containing the processed LAI data, filtered
          by land use classes of interest.
        list: A list containing:
          - unified_lai_list (List[str]): Paths to the resampled LAI files.
          - unified_dem (str): Path to the resampled DEM file.
          - elevation_labels (List[str]): List of elevation class labels.
    """
    # Obtain a list of raw LAI files from the specified folder
    files_in_lai_folder = grab_raw_lai_data_files(Path(lai_folder_path))

    # Convert raw LAI files from HDR to TIFF format
    converted_tiff_files_paths = [
        # await convert_hdr_to_tif for file_lai in files_in_lai_folder
        convert_hdr_to_tif(file_lai) for file_lai in files_in_lai_folder
    ]

    # If aoi_boundary_file is not None, cut land_use_file_path using
    #  aoi_boundary_file
    if aoi_boundary_file is not None:
        land_use_file_path = cut_land_use_file_path(
            land_use_file_path, aoi_boundary_file
        )

    # Create a template raster based on the land use raster
    template_raster = create_template_raster(Path(land_use_file_path))

    # Resample the DEM raster to match the extent and resolution of the
    # template raster
    unified_dem = copy_data_to_template(
        template_raster,
        dem_file_path,
        )

    # Resample the converted LAI rasters to match the template raster   
    unified_lai_list = []
    for converted_tiff_file in converted_tiff_files_paths:
        unified_lai_list.append(
            copy_data_to_template(
                template_raster,
                converted_tiff_file,
                output_folder=DEFAULT_TEMP_LAI_DIR,
            )
        )

    # Classify the elevation data based on the specified elevation bins
    elevation_classes, elevation_labels, new_elev_bins = classify_elevation(
        unified_dem, elevation_bins
    )

    # Process the LAI files and extract relevant data based on land use and
    # elevation classes
    data = process_lai_files_and_extract_data(
        unified_lai_list,
        land_use_file_path,
        elevation_classes,
        elevation_labels
    )

    # Filter the extracted LAI data to include only the land use classes of
    # interest
    result_data_frame = filter_lai_data_by_landuse(
                                                data,
                                                land_use_classes_of_interest
                                                )
    
    list_of_data_for_modifying = [
                                unified_lai_list,
                                unified_dem,
                                ]
    
    return result_data_frame, list_of_data_for_modifying


def adjust_lai(
    lai_array: np.ndarray,
    landuse_array: np.ndarray,
    elevation_array: np.ndarray,
    df: pd.DataFrame,
    elevation_list: List[str],
    lai_file_name: str
    ) -> Tuple[np.ndarray, np.ndarray]:
    """
    Adjusts LAI values based on land use and elevation classes specified in a
    CSV file, applying changes only if the new values fall within the range
    between Q1 and Q3. Unchanged values (not passing the Q1-Q3 condition)
    are recorded in a separate raster.

    This function modifies the LAI values in the given array by applying a 
    scaling factor (DIFF) for specific land use and elevation classes. 
    The adjustments are determined by filtering a DataFrame containing 
    the necessary information for a specific date extracted from the LAI file
    name.

    Parameters:
        lai_array (np.ndarray): Array of LAI values to be adjusted.
        landuse_array (np.ndarray): Array representing land use classes.
        elevation_array (np.ndarray): Array representing elevation classes.
        df (pd.DataFrame): DataFrame containing adjustment factors and class
          information.
        elevation_list (List[str]): List of elevation class labels
          corresponding to raster classes.
        lai_file_name (str): Name of the LAI file used to extract the date
          for filtering.

    Returns:
        Tuple[np.ndarray, np.ndarray]: The adjusted LAI array after applying 
          the specified modifications within the Q1-Q3 range, and a raster 
          with the unchanged values that did not pass the Q1-Q3 condition.
    """

    # Create an empty raster to store unchanged values
    unchanged_array = np.full_like(lai_array, np.nan)
    
    # Extract the date from the LAI file name
    lai_date = extract_date_from_filename(lai_file_name)
    
    # Filter the DataFrame for the relevant date
    df_filtered = df[df['Date'] == lai_date.strftime('%Y-%m-%d')]

    # Iterate through each filtered row in the DataFrame
    for index, row in df_filtered.iterrows():
        landuse_current = row['Landuse_current']

        # Raster indexing starts from 1
        elev_class_index = elevation_list.index(row['Elevation_class']) + 1  
        diff = row['DIFF']
        q1_target = row["Q1_target"]
        q3_target = row["Q3_target"]

        # Find the cells where land use and elevation match the conditions
        condition = (
            landuse_array == landuse_current
        ) & (
            elevation_array == elev_class_index
        )

        # Modify the corresponding values in the LAI array
        new_values = lai_array[condition] * diff

        # Apply the change only if the new value falls between Q1 and Q3
        valid_condition = (new_values >= q1_target) & (new_values <= q3_target)

        # Store unchanged values in the empty raster
        unchanged_array[condition] = np.where(
            ~valid_condition,
            lai_array[condition],
            np.nan
            )

        # Update the LAI array with valid changes
        lai_array[condition] = np.where(
            valid_condition,
            new_values,
            lai_array[condition]
            )

        # Calculate the total number of pixels in this condition (Sum_of_pix)
        sum_of_pix = np.sum(condition)
        
        # Calculate the number of unchanged pixels (Count_unchanged_pix)
        count_unchanged_pix = np.sum(~valid_condition)

        # Update the DataFrame with the results
        df.at[index, 'Sum_of_pix'] = sum_of_pix
        df.at[index, 'Count_unchanged_pix'] = count_unchanged_pix

    return lai_array, unchanged_array


def modification_lai_datas(
    list_of_data_for_modifying: List[Union[List[Path], Path, List[str]]],
    csv_for_modification: pd.DataFrame,
    elevation_bins: List[int]| None,
    land_use_path: Path
        ) -> None:
    """
    Modify LAI (Leaf Area Index) data based on land use and elevation classes.

    This function takes LAI data, applies modifications according to elevation
    and land use classes from a CSV file, and saves the adjusted LAI data as 
    new raster files.

    Workflow:
    - Classify elevation data into specified elevation bins.
    - Read land use and elevation raster data.
    - Adjust LAI values based on matching land use and elevation classes.
    - Save the modified LAI raster files.

    Parameters:
        list_of_data_for_modifying (list): A list containing:
          - [0]: List of Paths to LAI raster files to be modified.
          - [1]: Path to the elevation raster file.
        csv_for_modification (pd.DataFrame): DataFrame containing the CSV 
          file with LAI adjustment factors based on land use and elevation 
          classes.
        elevation_bins (list of int,optional): Threshold values for classifying 
          elevation zones.
        land_use_path (Path): Path to the land use raster file that will be
          resampled to match the template raster.

    Returns:
        None: The function modifies the LAI rasters and saves the modified 
          rasters to a specified directory.
    """

    elevation_classes, elevation_labels, new_elev_bins = classify_elevation( ##################################################################
        list_of_data_for_modifying[1], elevation_bins
    )

    # Use the template raster to resample the land use file
    template_raster = DEFAULT_TEMP_DIR + "\\" + DEFAULT_TEMP_RASTER_NAME

    # Resample the land use data to match the template raster
    unifited_landuse_path = copy_data_to_template(
        template_raster=template_raster,
        source_file=land_use_path,
        output_folder=DEFAULT_TEMP_DIR,
        filename=DEFAULT_TEMP_LANDUSE_NAME,
    )

    # Read the resampled land use raster
    unified_landuse = read_raster(unifited_landuse_path)

    # Define the output folder path for modified and unmodified LAI files
    output_folder_path_lai = ensure_directory_exists(DEFAULT_MODIFY_LAI_FOLDER)
    output_path_unchanged = ensure_directory_exists(DEFAULT_UNMODIFY_FOLDER)

    # Loop through each LAI file to apply modifications
    for lai_file_path in list_of_data_for_modifying[0]:

        # Read the LAI raster data
        lai_data = read_raster(lai_file_path)

        # Call the adjust_lai function with the corresponding LAI filename
        lai_adjusted, unchanged_array= adjust_lai(
            lai_data,
            unified_landuse,
            elevation_classes,
            csv_for_modification,
            elevation_labels,
            lai_file_path
        )

        # Extract the filename without the extension
        filename_raw = lai_file_path.stem
        # Split the filename and extract the first two parts
        part1 = filename_raw.split('_')[0]
        part2 = filename_raw.split('_')[1]
        part_of_name = part1 + '_' + part2

        # Construct the output path for the modified and unmodified LAI file
        output_path_for_lai = output_folder_path_lai.joinpath(
            f"modify_{part_of_name}.tif"
            )
        output_path_unchanged_lai = output_path_unchanged.joinpath(
            f"unmodify_{part_of_name}.tif"
            )

        # Save the adjusted LAI data and unmodified data to a new raster file
        save_lai_to_raster(
            lai_adjusted,
            template_raster,
            output_path_for_lai
            )
        save_lai_to_raster(
            unchanged_array,
            template_raster,
            output_path_unchanged_lai,
            )
    
    return csv_for_modification
