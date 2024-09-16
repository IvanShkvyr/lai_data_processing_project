from typing import List

from csv_processing import (
    save_mean_lai_by_day_of_year_to_csv,
    save_mean_lai_by_period_to_csv,
)
from data_processing import process_lai_data
from file_management import remove_directory_if_needed
from plotting import (
    plot_lai_by_landuse_and_elevation,
    plot_lai_by_landuse_and_elevation_for_year,
)


def run_calculate_and_save_mean_lai_by_period(
    lai_folder_path: str,
    land_use_path: str,
    dem_file_path: str,
    elevation_bins: List[int],
    land_use_classes_of_interest: List[int] | None = None,
    aoi_boundary_file: str | None = None,
    should_remove_temp: bool = True,
) -> None:
    """
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
    data_frame = process_lai_data(
        lai_folder_path,
        land_use_path,
        dem_file_path,
        elevation_bins,
        land_use_classes_of_interest,
        aoi_boundary_file,
    )

    # Save the mean LAI values by period to a CSV file
    save_mean_lai_by_period_to_csv(data_frame)

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
    data_frame = process_lai_data(
        lai_folder_path,
        land_use_path,
        dem_file_path,
        elevation_bins,
        land_use_classes_of_interest,
        aoi_boundary_file,
    )

    # Save the mean LAI values by day of year to a CSV file
    save_mean_lai_by_day_of_year_to_csv(data_frame)

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
    data_frame = process_lai_data(
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
    data_frame = process_lai_data(
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
    data_frame = process_lai_data(
        lai_folder_path,
        land_use_path,
        dem_file_path,
        elevation_bins,
        land_use_classes_of_interest,
        aoi_boundary_file,
    )

    # Save mean LAI values by period to a CSV file
    save_mean_lai_by_period_to_csv(data_frame)

    # Save mean LAI values by day of year to a CSV file
    save_mean_lai_by_day_of_year_to_csv(data_frame)

    # Generate plots of LAI by land use and elevation class
    plot_lai_by_landuse_and_elevation(data_frame)

    # Call the function to remove the directory if `should_remove_temp` is True
    remove_directory_if_needed(should_remove_temp)
