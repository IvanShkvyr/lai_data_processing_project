from typing import List

import numpy as np
import pandas as pd
import rasterio

from csv_processing import (
    save_data_to_csv,
    create_stat_lai_by_clusters,
    create_stat_lai_by_day_of_year,
    create_lai_modification_csv,
)
from data_processing import (process_lai_data,
                             copy_data_to_template,
                             extract_date_from_filename,
                             modification_lai_datas)
from decorators import measure_time
from file_management import remove_directory_if_needed
from plotting import (
    plot_lai_by_landuse_and_elevation,
    plot_lai_by_landuse_and_elevation_for_year,
    plot_lai_by_landuse_and_elevation_for_year_with_q1_q3_med_min_max
)
from raster_processing import read_raster


DEFAULT_CSV_MODIFICATION_FILENAME = "lai_modification.csv"


def run_calculate_and_save_mean_lai_by_period(
    lai_folder_path: str,
    land_use_path: str,
    dem_file_path: str,
    elevation_bins: List[int],
    is_clusters: bool = True,
    land_use_classes_of_interest: List[int] | None = None,
    aoi_boundary_file: str | None = None,
    should_remove_temp: bool = True,
) -> None:
    """

    TODO: Chenge
    Process LAI data files, calculate mean LAI by period, and save the results
    to a CSV file.

    Parameters:
        lai_folder_path (str): Path to the folder containing LAI data files.
        land_use_path (str): Path to the land use raster file.
        dem_file_path (str): Path to the digital elevation model (DEM) file.
        elevation_bins (List[int]): Elevation bins for classification.
        land_use_classes_of_interest (Optional[List[int]]): List of land use
         classes to include in the analysis. If None, all classes are included.
        aoi_boundary_file (Optional[str]): Path to a boundary file defining the
          area of interest. If None, the entire area is analyzed.
        should_remove_temp (bool): Whether to remove temporary files and
          directories created during processing. Defaults to True.

    Returns:
        None: The results are saved to a CSV file.
    """
    # Process LAI data files and extract relevant information
    data_frame, list_of_data_for_modifying = process_lai_data(
        lai_folder_path,
        land_use_path,
        dem_file_path,
        elevation_bins,
        land_use_classes_of_interest,
        aoi_boundary_file,
    )

    if is_clusters:
        # Save the mean LAI values by period to a CSV file
        create_stat_lai_by_clusters(data_frame)
    else:
        save_data_to_csv(data_frame)

    # Call the function to remove the directory if `should_remove_temp` is True
    remove_directory_if_needed(should_remove_temp)


def run_calculate_and_save_mean_lai_by_day_of_year(
    lai_folder_path: str,
    land_use_path: str,
    dem_file_path: str,
    elevation_bins: List[int],
    land_use_classes_of_interest: List[int] | None = None,
    aoi_boundary_file: str | None = None,
    should_remove_temp: bool = True,
) -> None:
    """
    Process LAI data files, calculate mean LAI by day of year, and save the
    results to a CSV file.

    Parameters:
        lai_folder_path (str): Path to the folder containing LAI data files.
        land_use_path (str): Path to the land use raster file.
        dem_file_path (str): Path to the digital elevation model (DEM) file.
        elevation_bins (List[int]): Elevation bins for classification.
        land_use_classes_of_interest (Optional[List[int]]): List of land use
         classes to include in the analysis. If None, all classes are included.
        aoi_boundary_file (Optional[str]): Path to a boundary file defining the
          area of interest.If None, the entire area is analyzed.
        should_remove_temp (bool): Whether to remove temporary files and
          directories created during processing. Defaults to True.

    Returns:
        None: The results are saved to a CSV file.
    """
    # Process LAI data files and extract relevant information
    data_frame, list_of_data_for_modifying = process_lai_data(
        lai_folder_path,
        land_use_path,
        dem_file_path,
        elevation_bins,
        land_use_classes_of_interest,
        aoi_boundary_file,
    )

    # Save the mean LAI values by day of year to a CSV file
    create_stat_lai_by_day_of_year(data_frame)

    # Call the function to remove the directory if `should_remove_temp` is True
    remove_directory_if_needed(should_remove_temp)


def run_plot_lai_by_landuse_and_elevation(
    lai_folder_path: str,
    land_use_path: str,
    dem_file_path: str,
    elevation_bins: List[int],
    land_use_classes_of_interest: List[int] | None = None,
    aoi_boundary_file: str | None = None,
    should_remove_temp: bool = True,
) -> None:
    """
    Process LAI data files and generate plots of LAI by land use and elevation
    class.

    Parameters:
        lai_folder_path (str): Path to the folder containing LAI data files.
        land_use_path (str): Path to the land use raster file.
        dem_file_path (str): Path to the digital elevation model (DEM) file.
        elevation_bins (List[int]): Elevation bins for classification.
        land_use_classes_of_interest (Optional[List[int]]): List of land use
         classes to include in the analysis. If None, all classes are included.
        aoi_boundary_file (Optional[str]): Path to a boundary file defining the
          area of interest. If None, the entire area is analyzed.
        should_remove_temp (bool): Whether to remove temporary files and
          directories created during processing. Defaults to True.

    Returns:
        None: The plots are saved as PNG files.
    """
    # Process LAI data files and extract relevant information
    data_frame, list_of_data_for_modifying = process_lai_data(
        lai_folder_path,
        land_use_path,
        dem_file_path,
        elevation_bins,
        land_use_classes_of_interest,
        aoi_boundary_file,
    )

    # Plot LAI values by land use and elevation class
    plot_lai_by_landuse_and_elevation(data_frame)

    # Call the function to remove the directory if `should_remove_temp` is True
    remove_directory_if_needed(should_remove_temp)


def run_plot_lai_by_landuse_and_elevation_for_year(
    lai_folder_path: str,
    land_use_path: str,
    dem_file_path: str,
    elevation_bins: List[int],
    display_datas: List[str],
    year: int,
    land_use_classes_of_interest: List[int] | None = None,
    aoi_boundary_file: str | None = None,
    should_remove_temp: bool = True,
) -> None:
    """
    Process LAI data files and generate plots of LAI by land use and elevation
    class for a specific year.

    Parameters:
        lai_folder_path (str): Path to the folder containing LAI data files.
        land_use_path (str): Path to the land use raster file.
        dem_file_path (str): Path to the digital elevation model (DEM) file.
        elevation_bins (List[int]): Elevation bins for classification.
        display_datas (List[str]): List of statistics to display in the plots
                                   (e.g., "Q1", "Mean_LAI", "Q3").
        year (int): The year for which the LAI data should be plotted.
        land_use_classes_of_interest (Optional[List[int]]): List of land use
                                   classes to include in the analysis. Defaults
                                   to None, which includes all classes.
        aoi_boundary_file (Optional[str]): Path to the area of interest (AOI)
                                   boundary file. Defaults to None.
        should_remove_temp (bool): Flag indicating whether to remove temporary
                                   files and directories after processing.
                                   Defaults to True.

    Returns:
        None: The plots are saved as PNG files.
    """

    # Process LAI data files and extract relevant information
    data_frame, list_of_data_for_modifying = process_lai_data(
        lai_folder_path,
        land_use_path,
        dem_file_path,
        elevation_bins,
        land_use_classes_of_interest,
        aoi_boundary_file,
    )

    # Plot LAI values by land use and elevation class
    plot_lai_by_landuse_and_elevation_for_year(data_frame, display_datas, year)

    # Call the function to remove the directory if `should_remove_temp` is True
    remove_directory_if_needed(should_remove_temp)


# @measure_time
def run_plot_lai_by_landuse_and_elevation_for_year_with_q1_q3_med_min_max(
    lai_folder_path: str,
    land_use_path: str,
    dem_file_path: str,
    elevation_bins: List[int],
    year: int,
    land_use_classes_of_interest: List[int] | None = None,
    aoi_boundary_file: str | None = None,
    should_remove_temp: bool = True,
) -> None:
    """
    Process LAI data files and generate plots of LAI by land use and elevation
    class for a specific year asynchronously.

    Parameters:
        lai_folder_path (str): Path to the folder containing LAI data files.
        land_use_path (str): Path to the land use raster file.
        dem_file_path (str): Path to the digital elevation model (DEM) file.
        elevation_bins (List[int]): Elevation bins for classification.
        year (int): The year for which the LAI data should be plotted.
        land_use_classes_of_interest (Optional[List[int]]): List of land use
                                   classes to include in the analysis. Defaults
                                   to None, which includes all classes.
        aoi_boundary_file (Optional[str]): Path to the area of interest (AOI)
                                   boundary file. Defaults to None.
        should_remove_temp (bool): Flag indicating whether to remove temporary
                                   files and directories after processing.
                                   Defaults to True.

    Returns:
        None: The plots are saved as PNG files.
    """

    # Process LAI data files and extract relevant information
    data_frame, unified_lai_list, unified_dem = process_lai_data(
        lai_folder_path,
        land_use_path,
        dem_file_path,
        elevation_bins,
        land_use_classes_of_interest,
        aoi_boundary_file,
    )

    # Plot LAI values by land use and elevation class
    plot_lai_by_landuse_and_elevation_for_year_with_q1_q3_med_min_max(
        data_frame,
        year
        )

    # Call the function to remove the directory if `should_remove_temp` is True
    remove_directory_if_needed(should_remove_temp)


def run_all_lai_analysis(
    lai_folder_path: str,
    land_use_path: str,
    dem_file_path: str,
    elevation_bins: List[int],
    land_use_classes_of_interest: List[int] | None = None,
    aoi_boundary_file: str | None = None,
    should_remove_temp: bool = True,
) -> None:
    """
    Perform a comprehensive analysis of LAI data including processing, saving
    mean LAI by period, saving mean LAI by day of year, and plotting LAI by
    land use and elevation class.

    Parameters:
        lai_folder_path (str): Path to the folder containing LAI data files.
        land_use_path (str): Path to the land use raster file.
        dem_file_path (str): Path to the digital elevation model (DEM) file.
        elevation_bins (List[int]): Elevation bins for classification.
        land_use_classes_of_interest (Optional[List[int]]): List of land use
         classes to include in the analysis. If None, all classes are included.
        aoi_boundary_file (Optional[str]): Path to a boundary file defining the
          area of interest. If None, the entire area is analyzed.
        should_remove_temp (bool): Whether to remove temporary files and
          directories created during processing. Defaults to True.

    Returns:
        None: The results are saved to CSV files and plots are generated.
    """
    # Process LAI data files and extract relevant information
    data_frame, list_of_data_for_modifying = process_lai_data(
        lai_folder_path,
        land_use_path,
        dem_file_path,
        elevation_bins,
        land_use_classes_of_interest,
        aoi_boundary_file,
    )

    # Save mean LAI values by period to a CSV file
    save_data_to_csv(data_frame)

    # Save mean LAI values by day of year to a CSV file
    create_stat_lai_by_day_of_year(data_frame)

    # Save mean LAI values by clusters to a CSV file
    create_stat_lai_by_clusters(data_frame)

    # Generate plots of LAI by land use and elevation class
    plot_lai_by_landuse_and_elevation(data_frame)

    # Call the function to remove the directory if `should_remove_temp` is True
    remove_directory_if_needed(should_remove_temp)


def run_lai_modification(
    lai_folder_path: str,
    land_use_path: str,
    dem_file_path: str,
    elevation_bins: List[int],
    current_landuse_class: int,
    target_landuse_class: int,
    aoi_boundary_file: str | None = None,
    should_remove_temp: bool = True,
    ) -> None:
    """
    Process LAI data files, apply modifications based on land use and elevation
    characteristics, and save the modified LAI data to a new raster file.

    Parameters:
        lai_folder_path (str): Path to the folder containing LAI data files.
        land_use_path (str): Path to the land use raster file.
        dem_file_path (str): Path to the digital elevation model (DEM) file.
        elevation_bins (List[int]): Elevation bins for classification.
        current_landuse_class (int): The current land use class in the data 
                                     that needs to be adjusted.
        target_landuse_class (int): The target land use class for modification.
        aoi_boundary_file (Optional[str]): Path to the area of interest (AOI)
                                     boundary file. Defaults to None.
        should_remove_temp (bool): Flag indicating whether to remove temporary 
                                   files and directories after processing.
                                   Defaults to True.

    Returns:
        None: The modified LAI data is saved as a new raster file.
    """
    land_use_classes_of_interest = [
        current_landuse_class,
        target_landuse_class
    ]

    # Process LAI data files and extract relevant information
    data_frame, list_of_data_for_modifying = process_lai_data(
        lai_folder_path,
        land_use_path,
        dem_file_path,
        elevation_bins,
        land_use_classes_of_interest,
        aoi_boundary_file,
    )

    # Create a CSV file that contains information for modifying LAI values
    csv_for_modification = create_lai_modification_csv(
        data_frame,
        current_landuse_class,
        target_landuse_class
    )

    

    # Apply the modifications to the LAI data
    updated_csv_for_modification = modification_lai_datas(
                            list_of_data_for_modifying,
                            csv_for_modification,
                            elevation_bins,
                            land_use_path
                            )
    
    save_data_to_csv(updated_csv_for_modification, DEFAULT_CSV_MODIFICATION_FILENAME)

    # Call the function to remove the directory if `should_remove_temp` is True
    remove_directory_if_needed(should_remove_temp)
