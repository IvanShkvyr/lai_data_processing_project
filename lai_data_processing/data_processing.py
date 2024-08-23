from collections import namedtuple
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Tuple

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.mask import mask
from rasterio.warp import reproject, Resampling

from file_management import ensure_directory_exists, grab_raw_lai_data_files
from raster_processing import (
    read_raster,
    create_template_raster,
    convert_hdr_to_tif,
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


def copy_data_to_template(
    template_raster: Path,
    source_file: Path,
    output_folder: str = "temp",
    filename: Optional[str] = None,
) -> Path:
    """
    Resamples data from source_file to match the extent and resolution of
    template_raster, and copies non-zero values to output_file.

    Parameters:
        template_raster ( Path): Path to the template raster file used for the
          extent and resolution.
        source_file ( Path): Path to the input raster file containing data to be
          resampled.
        output_folder (str): Path to the folder where the output file will
          be saved.
        filename (str, optional): Name of the output file. If not provided,
          '_unifited' will be appended to the template file's name.

    Returns:
         Path: Path to the output raster file.
    """

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
    elevation_bins: List[int],
) -> Tuple[np.ndarray, List[str]]:
    """
    Classify elevation data into different zones based on provided elevation
    thresholds.

    Parameters:
        unified_dem (Path): Path to the raster file containing the elevation
          data.
        elevation_bins (List[int]): List of elevation thresholds for
         classification. Elevation values will be categorized into bins defined
         by these thresholds.

    Returns:
       numpy.ndarray: An array with the same shape as the input elevation data,
            where each value represents the elevation zone according to the
            provided thresholds.
       List[str]: A list of labels for the elevation zones, describing the
            range of each zone.
    """

    # Read the elevation data from the raster file
    unified_dem_data = read_raster(unified_dem)

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

    return elevation_classes, elevation_labels


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
    land_use_classes_of_interest: Optional[List[int]] = None
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


def cut_land_use_file_path(
    file_path: str,
    aoi_path: str,
    output_folder: str = "temp",
) -> str:
    """
    Crops a land use raster file to the boundaries defined by an area of
    interest (AOI) shapefile.

    This function reads the AOI shapefile to obtain the boundaries, then uses
    these boundaries to crop the provided land use raster file. The cropped
    raster is saved to the specified output folder, and the path to the newly
    created raster file is returned.

    Parameters:
       file_path (str): The path to the land use raster file that needs
        to be cropped.
       aoi_path (str): The path to the shapefile defining the area of
       interest (AOI) used for cropping.
       output_folder (str, optional): The folder where the cropped raster file
        will be saved. Defaults to "temp".

    Returns:
        str: The path to the cropped raster file.

    Notes:
        - The output raster file will be saved in GeoTIFF format.
    """
    # Loading the area of interest boundaries
    aoi_file = gpd.read_file(aoi_path)

    with rasterio.open(file_path) as src:
        raster_crs = src.crs

        # Reproject AOI if necessary
        if aoi_file.crs != raster_crs:
            aoi_file = aoi_file.to_crs(raster_crs)

        geoms = aoi_file.geometry.values
        out_image, out_transform = mask(src, geoms, crop=True)
        out_meta = src.meta.copy()
        out_meta.update(
            {
                "driver": "GTiff",
                "height": out_image.shape[1],
                "width": out_image.shape[2],
                "transform": out_transform,
            }
        )

    # Get the file name without the extension
    name_file = Path(file_path).name
    out_raster = f"{output_folder}/{name_file}"

    # Write the cropped image
    with rasterio.open(out_raster, "w", **out_meta) as dest:
        dest.write(out_image)

    return out_raster


def process_lai_data(
    lai_folder_path: str,
    land_use_file_path: str,
    dem_file_path: str,
    elevation_bins: List[int],
    land_use_classes_of_interest: Optional[List[int]] = None,
    aoi_boundary_file: Optional[str] = None,
) -> pd.DataFrame:
    """
    Main function to process LAI (Leaf Area Index) data. This function handles
    the complete workflow from reading and converting raw LAI files, creating a
    template raster, resampling DEM and LAI data, classifying elevation zones,
    and extracting relevant data based on land use and elevation classes.

    Parameters:
        lai_folder_path (str or Path): Path to the folder containing raw LAI
          data files (e.g., HDR format).
        land_use_file_path (str or Path): Path to the land use raster file used
          for creating a template raster.
        dem_file_path (str or Path): Path to the digital elevation model (DEM)
          file to be resampled.
        elevation_bins (list of int): List of elevation thresholds used to
          classify elevation zones.
        land_use_classes_of_interest (list of int): List of land use classes to
          filter in the final data.
        aoi_boundary_file (str or Path, optional): Path to the shapefile
          defining the area of interest (AOI) used to crop the land use raster.
           Defaults to None.


    Returns:
       pd.DataFrame: A DataFrame containing the extracted LAI data, filtered by
          land use classes of interest.

    Notes:
        - This function converts raw LAI files from HDR to TIFF format, creates
         a template raster based on land use data, resamples DEM and LAI
         rasters to match the template, and classifies elevation zones based on
         provided thresholds.
        - The resulting data is processed to compute average LAI values for
         different land use and elevation classes and is then filtered based on
         specified land use classes.
    """
    # Obtain a list of raw LAI files from the specified folder
    files_in_lai_folder = grab_raw_lai_data_files(Path(lai_folder_path))

    # Convert raw LAI files from HDR to TIFF format
    converted_tiff_files_paths = [
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
    unified_dem = copy_data_to_template(template_raster, dem_file_path)

    # Resample the converted LAI rasters to match the template raster
    unified_lai_list = []
    for converted_tiff_file in converted_tiff_files_paths:
        unified_lai_list.append(
            copy_data_to_template(
                template_raster,
                converted_tiff_file,
                output_folder="temp\\temp_lai_unifited",
            )
        )

    # Classify the elevation data based on the specified elevation bins
    elevation_classes, elevation_labels = classify_elevation(
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

    return filter_lai_data_by_landuse(data, land_use_classes_of_interest)
