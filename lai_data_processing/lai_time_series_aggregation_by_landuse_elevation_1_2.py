"""
LAI Data Processing Module

This module provides functions for processing Leaf Area Index (LAI) data files,
including conversion, resampling, classification, and analysis. The main
functionalities include:

1. Ensuring directory existence.
2. Listing raw LAI data files.
3. Converting HDR format raster files to TIFF format.
4. Creating template rasters filled with zeros based on an existing raster.
5. Resampling and copying data from source rasters to template rasters.
6. Creating elevation zones based on provided thresholds.
7. Reading raster data into numpy arrays.
8. Classifying elevation based on provided bins.
9. Processing LAI files to extract data by elevation and land use classes.
10. Creating and filtering pandas DataFrames based on land use classes of
    interest.
11. Calculating and saving mean LAI by periods and by day of the year.
12. Plotting LAI data by land use and elevation classes.

Example usage:

    lai_folder_path = 'data/Vegetation'
    land_use_file_path = 'data/Land_Use/CLC_Thaya_snap_2_model_extend.tif'
    dem_file_path = 'data/DTM/SRTM.tif'
    elevation_bins = [450, 750]
    land_use_classes_of_interest = [100, 211, 311]

    run_all_lai_analysis(
                         lai_folder_path,
                         land_use_file_path,
                         dem_file_path,
                         elevation_bins,
                         land_use_classes_of_interest
                         )

Modules and libraries used:
- datetime
- pathlib
- matplotlib.pyplot
- numpy
- pandas
- rasterio
- rasterio.warp

Author: Ivan Shkvyr
Date: 2024-07-25
"""


from datetime import datetime, timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio
from rasterio.warp import reproject, Resampling


def ensure_directory_exists(directory_path):
    """
    Ensure that the specified exists. If not, create it.

    Parameters:
        directory_path (str or Path): The path to the folder to check or create.

    Returns:
        Path: The Path object of the ensured directory.
    """
    path = Path(directory_path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    return path


def grab_raw_lai_data_files(path: Path):
    """
     Get a list of raw LAI data files without extensions in the specified folder

    This function returns a list of files (without extensions) representing raw
    LAI data found in the specified folder.

    Parameters:
        path (Path): The path to the folder to scan.

    Returns:
        List[Path]: A list of Path objects representing raw LAI data files
                    without extensions in the folder.
    """

    files_without_extension = []

    for element in path.iterdir():
        if element.is_file() and element.suffix == "":
            files_without_extension.append(element)

    return files_without_extension


def convert_hdr_to_tif(
                        data_file_path,
                        temp_lai_folder_path="temp\\temp_lai_processing",
                        driver="ENVI"
                      ):
    """
    Convert a HDR format raster file to TIFF format and save it in a specified
    temporary folder.

    Parameters:
        data_file_path (str or Path): Path to the HDR format raster file.
        temp_lai_folder_path (str, optional): Path to the temporary folder where
                the TIFF file will be saved.
                Defaults to 'temp\\temp_lai_processing'.
        driver (str, optional): Rasterio driver to open the HDR file.
                Defaults is 'ENVI'.

    Returns:
        Path: Full path to the converted TIF file saved in the temporary folder.

    Notes:
        - The function reads data from the HDR file, updates its profile for
          TIF format, and saves it in the specified temporary folder.
        - If the specified temporary folder does not exist, it will be created
          before saving the TIFF file.
    """
    # Define the Path object for the temporary folder
    temp_lai_folder_path = ensure_directory_exists(temp_lai_folder_path)

    # Read data from HDR file
    with rasterio.open(data_file_path, "r", driver=driver) as src:
        data = src.read(1)  # Читання першого (і єдиного) шару
        profile = src.profile  # Копіювання профілю даних

        # Replace values less than 0 with NaN
        data[data < 0] = np.nan

    # Update profile for saving in GTiff format
    profile.update(
                    driver="GTiff",
                    dtype=rasterio.float32,
                    count=1,
                    nodata=np.nan,
                    compress="lzw"
                  )

    # Formulate path to TIFF file based on HDR file name in the temporary folder
    tiff_file_name = f"{Path(data_file_path).stem}.tif"
    out_tif_file = temp_lai_folder_path / tiff_file_name

    # Save data in TIFF format
    with rasterio.open(out_tif_file, "w", **profile) as dst:
        dst.write(data.astype(rasterio.float32), 1)

    return out_tif_file


def create_template_raster(
                            base_raster,
                            output_folder="temp",
                            filename="template_raster.tif"
                          ):
    """
    Create a template raster file based on another raster, filled with zeros.

    Parameters:
        base_raster (str): Path to the base raster file from which metadata will
          be read.
        output_folder (str): Path to the output folder where the template raster
          file will be created.
        filename (str): Name of the output template raster file to be created.

    Returns:
        str: Path to the created template raster file.

    Notes:
        - This function reads the metadata (profile) from the base raster,
          removes unnecessary parameters, updates the profile for saving in
          GTiff format, and creates a new raster file filled with zeros.
        - The output raster file will have the same dimensions and coordinate
          system as the base raster, but all pixel values will be set to 0.
    """

    # Define the Path object for the output folder
    output_folder_path = ensure_directory_exists(output_folder)

    # Formulate the path to the output file
    template_raster_path = output_folder_path / filename

    # Open the base raster and read its profile
    with rasterio.open(base_raster, "r") as src:
        profile = src.profile

        # Remove nodata parameter if it exists (not needed for an empty file)
        profile.pop("nodata", None)

        # Update profile for saving in GTiff format
        profile.update(
                        driver="GTiff",
                        dtype=rasterio.float32,
                        count=1,
                        compress="lzw"
                       )

        # Create a new TIFF file with all pixels set to 0
        with rasterio.open(template_raster_path, "w", **profile) as dst:
            # Create an array filled with zeros
            zeros_array = np.zeros((src.height, src.width), dtype=np.float32)

            # Write the zeros array to the output file
            dst.write(zeros_array, 1)

    return template_raster_path


def copy_data_to_template(
                            template_raster,
                            source_file,
                            output_folder="temp",
                            filename=None
                         ):
    """
    Resamples data from source_file to match the extent and resolution of
    template_raster, and copies non-zero values to output_file.

    Parameters:
        template_raster (str): Path to the template raster file used for the
          extent and resolution.
        source_file (str): Path to the input raster file containing data to be
          resampled.
        output_folder (str): Path to the folder where the output file will
          be saved.
        filename (str, optional): Name of the output file. If not provided,
          '_unifited' will be appended to the template file's name.

    Returns:
        str: Path to the output raster file.
    """
    # Define the Path object for the output folder
    output_folder_path = ensure_directory_exists(output_folder)

    # Determine the output filename
    if filename is None:
        # Extract the base name without extension and add the suffix
        base_name = Path(source_file).stem
        filename = f"{base_name}_unifited.tif"
    else:
        filename = f"{filename}.tif"  # Ensure the filename has a .tif extension

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


def create_elevation_zones(dem_file, thresholds):
    """
    Creates elevation zones based on the provided thresholds.

    Parameters:
        dem_file (str): Path to the DEM (Digital Elevation Model) file.
        thresholds (list of int): List of elevation thresholds for zoning.
        For example, [450] will create zones for elevations >450 and <450 meters

    Returns:
        numpy.ndarray: An array with the same shape as the input DEM, where
          each value represents the elevation zone according to the provided
          thresholds.
    """
    # Open the DEM file using rasterio
    with rasterio.open(dem_file) as dem_src:
        # Read the elevation data from the DEM file
        dem_data = dem_src.read(1)

    # Create elevation zones based on the thresholds
    elevation_zones = np.digitize(dem_data, bins=thresholds)

    return elevation_zones


def read_raster(raster_path):
    """
    Reads the first band of a raster file and returns it as a numpy array.

    Parameters:
        raster_path (str or Path): The path to the raster file to be read.

    Returns:
        numpy.ndarray: The first band of the raster file as a 2D array.
    """
    with rasterio.open(raster_path) as src:
        return src.read(1)


def classify_elevation(unified_dem, elevation_bins):
    """
    Classify elevation data into different zones based on provided elevation
    thresholds.

    Parameters:
        unified_dem (str): Path to the raster file containing the elevation
          data.
        elevation_bins (list of int): List of elevation thresholds for
          classification. Elevation values will be categorized into bins defined
          by these thresholds.

    Returns:
        numpy.ndarray: An array with the same shape as the input elevation data,
            where each value represents the elevation zone according to the
            provided thresholds.
        list of str: A list of labels for the elevation zones, describing the
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


def _extract_date_from_filename(filename):
    """
    Extract date from a filename assuming the pattern
    '<prefix>_<YYYYDDD>_suffix'.
    
    Parameters:
        filename (Path): Path object representing the LAI file name.
        
    Returns:
        datetime: The date extracted from the filename.
    """
    date_str = filename.stem.split("_")[1]
    year = int(date_str[:4])
    day_of_year = int(date_str[4:7])
    date = datetime(year, 1, 1) + timedelta(days=day_of_year - 1)
    return date


def _calculate_boxplot_stats(lai_data):
    """
    Calculate boxplot statistics for given LAI data.
    
    Parameters:
        lai_data (numpy.ndarray): Array containing LAI values.
        
    Returns:
        dict: A dictionary containing boxplot statistics.
    """
    Q1 = np.percentile(lai_data, 25)
    Q2 = np.percentile(lai_data, 50)
    Q3 = np.percentile(lai_data, 75)
    IQR = Q3 - Q1
    lower_whisker = Q1 - 1.5 * IQR
    upper_whisker = Q3 + 1.5 * IQR
    min_val = np.min(lai_data)
    max_val = np.max(lai_data)
    
    return {
        "Min": min_val,
        "Q1": Q1,
        "Median": Q2,
        "Q3": Q3,
        "Max": max_val,
        "Lower Whisker": lower_whisker,
        "Upper Whisker": upper_whisker,
    }


def _calculate_mean_and_boxplot_lai(lai_data, landuse_data, elevation_data, landuse_class, elev_class):
    """
    Calculate the mean LAI value and boxplot statistics for a given land use and elevation class.
    
    Parameters:
        lai_data (numpy.ndarray): Array containing LAI values.
        landuse_data (numpy.ndarray): Array containing land use classifications.
        elevation_data (numpy.ndarray): Array containing elevation classes.
        landuse_class (int): The land use class to filter.
        elev_class (int): The elevation class to filter.
    
    Returns:
        dict or None: A dictionary containing the mean LAI value and boxplot statistics,
                      or None if no pixels match the criteria.
    """
    mask = (landuse_data == landuse_class) & (elevation_data == elev_class)
    if np.any(mask):
        filtered_lai_data = lai_data[mask]
        mean_lai = np.mean(filtered_lai_data)
        boxplot_stats = _calculate_boxplot_stats(filtered_lai_data)
        return {
            "Mean_LAI": mean_lai,
            **boxplot_stats
        }
    return None


def _process_lai_files_and_extract_data(
                                        unified_lai_list,
                                        land_use_file_path,
                                        elevation_classes,
                                        elevation_labels
                                       ):
    """
    Process LAI (Leaf Area Index) raster files and extract mean LAI values based
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
        list of lists: A list of records, where each record is a list containing:
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
    unique_landuse_classes = np.unique(landuse)  # Get unique land use classes present in the raster

    data = []
    for lai_file in unified_lai_list:
        # Extract date information from the LAI file name
        date = _extract_date_from_filename(lai_file)

        # Read LAI data from the current file
        lai_data = read_raster(lai_file)

        # Loop through each unique land use class
        for landuse_class in unique_landuse_classes:
            # Loop through each elevation class
            for elev_class in range(1, len(elevation_labels) + 1):
                # Calculate mean LAI and boxplot statistics for the current land use and elevation class
                stats = _calculate_mean_and_boxplot_lai(lai_data, landuse, elevation_classes, landuse_class, elev_class)
                if stats is not None:
                    data.append([
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
                    ])

    return data


def _filter_lai_data_by_landuse(data, land_use_classes_of_interest):
    """
    Creates a DataFrame from the provided LAI data and filters it based on
    specified land use classes.

    This function constructs a pandas DataFrame from the input data, which
    should include columns for date, land use, elevation class, and average LAI
    values. It then filters the DataFrame to include only the rows where the
    land use class is in the list of land use classes of interest.

    Parameters:
        data (list of lists): The raw data to be converted into a DataFrame.
                             Each entry should be a list containing date, land
                             use class, elevation class, and average LAI value.
        land_use_classes_of_interest (list of int): A list of land use classes
                             that should be included in the filtered DataFrame.

    Returns:
        pd.DataFrame: A filtered DataFrame containing only rows with land use
         classes specified in land_use_classes_of_interest.

    Notes:
        - The DataFrame columns are named as 'Date', 'Landuse',
          'Elevation_class', and 'average_LAI'.
    """
    # Create a DataFrame from the provided data with specified columns
    df_full = pd.DataFrame(
        data, columns=[
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
                      ]
    )

    # Convert the 'Landuse' column to integer type
    df_full["Landuse"] = df_full["Landuse"].astype(int)

    # Filter the DataFrame to include only rows where 'Landuse' is in the
    # specified list
    data_frame = (
                df_full[df_full["Landuse"].isin(land_use_classes_of_interest)]
                .copy()
                 )

    return data_frame


def _process_lai_data(
                        lai_folder_path,
                        land_use_file_path,
                        dem_file_path,
                        elevation_bins,
                        land_use_classes_of_interest,
                     ):
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

    # Create a template raster based on the land use raster
    template_raster = create_template_raster(Path(land_use_file_path))

    # Resample the DEM raster to match the extent and resolution of the template
    # raster
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
    data = _process_lai_files_and_extract_data(
                                                unified_lai_list,
                                                land_use_file_path,
                                                elevation_classes,
                                                elevation_labels
                                              )

    # Filter the extracted LAI data to include only the land use classes of
    # interest
    return _filter_lai_data_by_landuse(data, land_use_classes_of_interest)


def _save_mean_lai_by_period_to_csv(
                                    dataframe,
                                    results_folder="results",
                                    filename="daily_lai.csv"
                                   ):
    """
    Save the mean LAI values by period from a DataFrame to a CSV file.

    This function takes a DataFrame containing mean LAI values and saves it as a
    CSV file in the specified results folder. The DataFrame should have been
    processed to include mean LAI values for different periods, such as days of
    the year.

    Parameters:
        dataframe (pd.DataFrame): The DataFrame containing the mean LAI values
            to be saved.
        results_folder (str, optional): Path to the folder where the CSV file
            will be saved. Defaults to 'results'.
        filename (str, optional): Name of the CSV file to be created. Defaults
            to 'daily_lai.csv'.

    Returns:
        None

    Notes:
        - The function ensures that the results folder exists before attempting
          to save the file.
        - The CSV file will be created with the specified filename in the given
          folder.
    """
    # Ensure the results folder exists
    directory_path = ensure_directory_exists(results_folder)

    # Formulate the full path to the output CSV file
    daily_lai_path = directory_path / filename

    # Save the DataFrame to a CSV file
    dataframe.to_csv(daily_lai_path, index=False)


def _save_mean_lai_by_day_of_year_to_csv(data_frame, results_folder="results"):
    """
    Calculates the mean LAI values for each day of the year, grouped by land use
    and elevation class, and saves the results to a CSV file.

    Parameters:
        data_frame (pd.DataFrame): The input DataFrame containing columns 'Date'
             ,'Landuse', 'Elevation_class', and 'average_LAI'. The 'Date' column
              should be in datetime format.
        results_folder (str): The path to the folder where the results CSV file
              will be saved. Defaults to 'results'.

    Returns:
        None

    Notes:
        - The 'Day_of_Year' column is added to the DataFrame in the format
          'MM-DD' to represent each day of the year.
    """
    # Ensure the results folder exists
    ensure_directory_exists(results_folder)

    # Define the path for the output CSV file
    mean_characteristic_year_path = (
        Path(results_folder) / "mean_characteristic_year.csv"
    )

    # Convert the 'Date' column to datetime format if not already
    data_frame["Date"] = pd.to_datetime(
        data_frame["Date"]
    )  # Ensure the 'Date' column is in datetime format

    # Extract the day of the year in 'MM-DD' format
    data_frame["Day_of_Year"] = data_frame["Date"].dt.strftime("%m-%d")

    # Group by 'Day_of_Year', 'Landuse', and 'Elevation_class' and calculate the
    # mean LAI
    mean_lai_by_day = (
        data_frame.groupby(["Day_of_Year", "Landuse", "Elevation_class"])
        .agg({
            "Mean_LAI": "mean",
            "Min": "mean",
            "Q1": "mean",
            "Median": "mean",
            "Q3": "mean",
            "Max": "mean",
            "Lower Whisker": "mean",
            "Upper Whisker": "mean"
        })
        .reset_index()
    )

    # Save the DataFrame with mean LAI values to a CSV file
    mean_lai_by_day.to_csv(mean_characteristic_year_path, index=False)


def _plot_lai_by_landuse_and_elevation(
                                       data_frame,
                                       display_data="Mean_LAI",
                                       results_folder_png="results\\png"
                                       ):
    """
    Generates and saves plots of Leaf Area Index (LAI) data by land use and
    elevation class.

    This function creates line plots showing the variation of LAI over the day
    of the year for each combination of land use and elevation class. Each plot
    represents data for a specific land use class and elevation zone, with
    separate lines for different years.

    Parameters:
        df (pd.DataFrame): A DataFrame containing LAI data with columns 'Date',
          'Landuse', 'Elevation_class', and 'average_LAI'. The 'Date' column
           should be in datetime format.
        results_folder_png (str): The path to the folder where the PNG plot
           files will be saved. The default is 'results/png'.

    Returns:
        None

    Notes:
        - The function creates one plot for each combination of land use class
          and elevation class.
        - The resulting plots are saved as PNG files in the specified folder,
          with filenames indicating the land use and elevation classes.
    """
    # Iterate over each combination of land use and elevation class
    for (landuse_class, elevation_class), group_data in data_frame.groupby(
        ["Landuse", "Elevation_class"]
    ):
        plt.figure(figsize=(10, 6))

        # Plot LAI for each year
        for year, year_data in group_data.groupby(data_frame["Date"].dt.year):
            plt.plot(
                year_data["Date"].dt.dayofyear,
                year_data[display_data],
                label=f"Year {year}",
            )

        # Set plot titles and labels
        plt.title(f"LAI for Landuse {landuse_class} and "
                  f"Elevation {elevation_class} ({display_data})")
        plt.xlabel("Day of Year")
        plt.ylabel("LAI")
        plt.legend()

        # Ensure the results folder exists
        results_folder_png_path = ensure_directory_exists(results_folder_png)

        # Define the path for saving the plot
        plot_file_path = (
            results_folder_png_path
            / f"lai_plot_landuse_{landuse_class}_" \
              f"elevation_{elevation_class}.png"
        )

        # Save the plot as a PNG file
        plt.savefig(plot_file_path)
        plt.close()


def _plot_lai_by_landuse_and_elevation_for_year(
                                                data_frame,
                                                display_datas=None,
                                                year=None,
                                                results_folder_png="results/png"
                                                ):
    """
    Generates and saves plots of Leaf Area Index (LAI) data by land use and
    elevation class for a specified year.

    This function creates line plots showing the variation of LAI over the day
    of the year for each combination of land use and elevation class. Each plot
    represents data for a specific land use class and elevation zone, displaying
    the statistical measures specified in `display_datas` for the given year.

    Parameters:
        data_frame (pd.DataFrame): A DataFrame containing LAI data with columns
            'Date', 'Landuse', 'Elevation_class', and various statistical measures.
            The 'Date' column should be in datetime format.
        display_datas (list of str): A list of column names to be plotted. 
            Defaults to ['Q1', 'Q3'].
        year (int): The year for which the data should be plotted.
        results_folder_png (str): The path to the folder where the PNG plot files
            will be saved. Defaults to 'results/png'.

    Returns:
        None

    Notes:
        - The function creates one plot for each combination of land use class
          and elevation class, showing only the data for the specified year.
        - The resulting plots are saved as PNG files in the specified folder,
          with filenames indicating the land use, elevation classes, and year.
    """
    if display_datas is None:
        display_datas = ["Q1", "Q3"]

    # Filter the DataFrame for the specified year
    year_data = data_frame[data_frame["Date"].dt.year == year]

    # Ensure the results folder exists
    results_folder_png_path = ensure_directory_exists(results_folder_png)

    # Iterate over each combination of land use and elevation class
    for (landuse_class, elevation_class), group_data in year_data.groupby(
        ["Landuse", "Elevation_class"]
    ):
        plt.figure(figsize=(10, 6))

        # Plot the specified statistical measures
        for display_data in display_datas:
            plt.plot(
                group_data["Date"].dt.dayofyear,
                group_data[display_data],
                label=display_data
            )

        # Set plot titles and labels
        plt.title(f"LAI for Landuse {landuse_class} and "
                  f"Elevation {elevation_class} ({year})")
        plt.xlabel("Day of Year")
        plt.ylabel("Value")
        plt.legend()

        # Define the path for saving the plot
        plot_file_path = (
            results_folder_png_path
            / f"lai_plot_landuse_{landuse_class}_" \
              f"elevation_{elevation_class}_{year}.png"
        )

        # Save the plot as a PNG file
        plt.savefig(plot_file_path)
        plt.close()



def run_calculate_and_save_mean_lai_by_period(
                                                lai_folder_path,
                                                land_use_file_path,
                                                dem_file_path,
                                                elevation_bins,
                                                land_use_classes_of_interest,
                                             ):
    """
    Process LAI data files, calculate mean LAI by period, and save the results
    to a CSV file.

    Parameters:
        lai_folder_path (str): Path to the folder containing LAI data files.
        land_use_file_path (str): Path to the land use raster file.
        dem_file_path (str): Path to the digital elevation model (DEM) file.
        elevation_bins (list of int): Elevation bins for classification.
        land_use_classes_of_interest (list of int): List of land use classes to
        include in the analysis.

    Returns:
        None: The results are saved to a CSV file.
    """
    # Process LAI data files and extract relevant information
    data_frame = _process_lai_data(
                                    lai_folder_path,
                                    land_use_file_path,
                                    dem_file_path,
                                    elevation_bins,
                                    land_use_classes_of_interest,
                                  )

    # Save the mean LAI values by period to a CSV file
    _save_mean_lai_by_period_to_csv(data_frame)


def run_calculate_and_save_mean_lai_by_day_of_year(
                                                lai_folder_path,
                                                land_use_file_path,
                                                dem_file_path,
                                                elevation_bins,
                                                land_use_classes_of_interest,
                                                  ):
    """
    Process LAI data files, calculate mean LAI by day of year, and save the
    results to a CSV file.

    Parameters:
        lai_folder_path (str): Path to the folder containing LAI data files.
        land_use_file_path (str): Path to the land use raster file.
        dem_file_path (str): Path to the digital elevation model (DEM) file.
        elevation_bins (list of int): Elevation bins for classification.
        land_use_classes_of_interest (list of int): List of land use classes to
        include in the analysis.

    Returns:
        None: The results are saved to a CSV file.
    """
    # Process LAI data files and extract relevant information
    data_frame = _process_lai_data(
                                    lai_folder_path,
                                    land_use_file_path,
                                    dem_file_path,
                                    elevation_bins,
                                    land_use_classes_of_interest,
                                  )

    # Save the mean LAI values by day of year to a CSV file
    _save_mean_lai_by_day_of_year_to_csv(data_frame)


def run_plot_lai_by_landuse_and_elevation(
                                            lai_folder_path,
                                            land_use_file_path,
                                            dem_file_path,
                                            elevation_bins,
                                            land_use_classes_of_interest,
                                            display_data,
                                         ):
    """
    Process LAI data files and generate plots of LAI by land use and elevation
    class.

    Parameters:
        lai_folder_path (str): Path to the folder containing LAI data files.
        land_use_file_path (str): Path to the land use raster file.
        dem_file_path (str): Path to the digital elevation model (DEM) file.
        elevation_bins (list of int): Elevation bins for classification.
        land_use_classes_of_interest (list of int): List of land use classes to
        include in the analysis.

    Returns:
        None: The plots are saved as PNG files.
    """
    # Process LAI data files and extract relevant information
    data_frame = _process_lai_data(
                                    lai_folder_path,
                                    land_use_file_path,
                                    dem_file_path,
                                    elevation_bins,
                                    land_use_classes_of_interest,
                                  )

    # Plot LAI values by land use and elevation class
    _plot_lai_by_landuse_and_elevation(data_frame, display_data)


def run_plot_lai_by_landuse_and_elevation_for_year(
                                            lai_folder_path,
                                            land_use_path,
                                            dem_file_path,
                                            elevation_bins,
                                            land_use_classes_of_interest,
                                            display_datas,
                                            year,
                                                   ):
    """
    
    """
    # Process LAI data files and extract relevant information
    data_frame = _process_lai_data(
                                    lai_folder_path,
                                    land_use_path,
                                    dem_file_path,
                                    elevation_bins,
                                    land_use_classes_of_interest,
                                  )

    # Plot LAI values by land use and elevation class
    _plot_lai_by_landuse_and_elevation_for_year(data_frame, display_datas, year)




def run_all_lai_analysis(
                        lai_folder_path,
                        land_use_file_path,
                        dem_file_path,
                        elevation_bins,
                        land_use_classes_of_interest,
                        ):
    """
    Perform a comprehensive analysis of LAI data including processing, saving
    mean LAI by period, saving mean LAI by day of year, and plotting LAI by
    land use and elevation class.

    Parameters:
        lai_folder_path (str): Path to the folder containing LAI data files.
        land_use_file_path (str): Path to the land use raster file.
        dem_file_path (str): Path to the digital elevation model (DEM) file.
        elevation_bins (list of int): Elevation bins for classification.
        land_use_classes_of_interest (list of int): List of land use classes
        to include in the analysis.

    Returns:
        None: The results are saved to CSV files and plots are generated.
    """
    # Process LAI data files and extract relevant information
    data_frame = _process_lai_data(
                                    lai_folder_path,
                                    land_use_file_path,
                                    dem_file_path,
                                    elevation_bins,
                                    land_use_classes_of_interest,
                                  )

    # Save mean LAI values by period to a CSV file
    _save_mean_lai_by_period_to_csv(data_frame)

    # Save mean LAI values by day of year to a CSV file
    _save_mean_lai_by_day_of_year_to_csv(data_frame)

    # Generate plots of LAI by land use and elevation class
    _plot_lai_by_landuse_and_elevation(data_frame)


if "__main__" == __name__:

    # Example usage

    # Path to the folder with LAI data
    outer_lai_folder_path = "data\\Vegetation"

    # Path to the boundary file of the area of interest
    # outer_aoi_boundary_file  = 'DYJ_500_hranice.shp'

    # Path to the land use file +++
    outer_land_use_path = "data\\Land_Use\\CLC_Thaya_snap_2_model_extend.tif"

    # Path to the digital elevation model file
    outer_dem_file_path = "data\\DTM\\SRTM.tif"

    # Setting boundaries for elevation classes
    outer_elevation_bins = [450]

    # Setting land use classes
    outer_land_use_classes_of_interest = [211, 311]

    # Setting value
                        # "Mean_LAI"
                        # "Min"
                        # "Q1"
                        # "Median"
                        # "Q3"
                        # "Max"
                        # "Lower Whisker"
                        # "Upper Whisker"
    outer_display_data = "Q1"

    outer_display_datas = ["Q1","Mean_LAI", "Q3"]

    outer_year = 2001




    # run_calculate_and_save_mean_lai_by_period(
    #     outer_lai_folder_path,
    #     outer_land_use_path,
    #     outer_dem_file_path,
    #     outer_elevation_bins,
    #     outer_land_use_classes_of_interest,
    # )

    # run_calculate_and_save_mean_lai_by_day_of_year(
    #     outer_lai_folder_path,
    #     outer_land_use_path,
    #     outer_dem_file_path,
    #     outer_elevation_bins,
    #     outer_land_use_classes_of_interest,
    # )

    # run_plot_lai_by_landuse_and_elevation(
    #     outer_lai_folder_path,
    #     outer_land_use_path,
    #     outer_dem_file_path,
    #     outer_elevation_bins,
    #     outer_land_use_classes_of_interest,
    #     outer_display_data
    # )


    run_plot_lai_by_landuse_and_elevation_for_year(
        outer_lai_folder_path,
        outer_land_use_path,
        outer_dem_file_path,
        outer_elevation_bins,
        outer_land_use_classes_of_interest,
        outer_display_datas,
        outer_year,
    )


    # run_all_lai_analysis(
    #     outer_lai_folder_path,
    #     outer_land_use_path,
    #     outer_dem_file_path,
    #     outer_elevation_bins,
    #     outer_land_use_classes_of_interest,
    # )
