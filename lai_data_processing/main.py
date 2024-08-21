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
                                            lai_folder_path,
                                            land_use_path,
                                            dem_file_path,
                                            elevation_bins,
                                            land_use_classes_of_interest=None,
                                            aoi_boundary_file=None,
                                            should_remove_temp=True,
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
                                            lai_folder_path,
                                            land_use_path,
                                            dem_file_path,
                                            elevation_bins,
                                            land_use_classes_of_interest=None,
                                            aoi_boundary_file=None,
                                            should_remove_temp=True,
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
                                            lai_folder_path,
                                            land_use_path,
                                            dem_file_path,
                                            elevation_bins,
                                            land_use_classes_of_interest=None,
                                            aoi_boundary_file=None,
                                            should_remove_temp=True,
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
                                            lai_folder_path,
                                            land_use_path,
                                            dem_file_path,
                                            elevation_bins,
                                            display_datas,
                                            year,
                                            land_use_classes_of_interest=None,
                                            aoi_boundary_file=None,
                                            should_remove_temp=True,
                                                   ):
    """

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
    plot_lai_by_landuse_and_elevation_for_year(
                                                data_frame,
                                                display_datas,
                                                year
                                               )

    # Call the function to remove the directory if `should_remove_temp` is True
    remove_directory_if_needed(should_remove_temp)


def run_all_lai_analysis(
                        lai_folder_path,
                        land_use_path,
                        dem_file_path,
                        elevation_bins,
                        land_use_classes_of_interest=None,
                        aoi_boundary_file=None,
                        should_remove_temp=True,
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




if "__main__" == __name__:

    # Example usage

    # Path to the folder with LAI data
    outer_lai_folder_path = "data\\Vegetation"

    # Path to the boundary file of the area of interest
    outer_aoi_boundary_file = 'data\\border\\DYJ_500_hranice.shp'

    # Path to the land use file +++
    outer_land_use_path = "data\\Land_Use\\CLC_Thaya_snap_2_model_extend.tif"

    # Path to the digital elevation model file
    outer_dem_file_path = "data\\DTM\\SRTM.tif"

    # Setting boundaries for elevation classes
    outer_elevation_bins = [450]

    # Setting land use classes
    outer_land_use_classes_of_interest = [211, 311]

    # Setting value:
    # "Mean_LAI"
    # "Min"
    # "Q1"
    # "Median"
    # "Q3"
    # "Max"
    # "Lower Whisker"
    # "Upper Whisker"
    outer_display_data = "Q1"

    outer_display_datas = ["Q1", "Mean_LAI", "Q3",]

    outer_year = 2001

    should_remove_temp = True

    # run_calculate_and_save_mean_lai_by_period(
    #     lai_folder_path=outer_lai_folder_path,
    #     land_use_path=outer_land_use_path,
    #     dem_file_path=outer_dem_file_path,
    #     elevation_bins=outer_elevation_bins,
    #     land_use_classes_of_interest=outer_land_use_classes_of_interest,
    #     aoi_boundary_file=outer_aoi_boundary_file,
    #     should_remove_temp=True,
    #     )

    # run_calculate_and_save_mean_lai_by_day_of_year(
    #     lai_folder_path=outer_lai_folder_path,
    #     land_use_path=outer_land_use_path,
    #     dem_file_path=outer_dem_file_path,
    #     elevation_bins=outer_elevation_bins,
    #     land_use_classes_of_interest=None,
    #     aoi_boundary_file=outer_aoi_boundary_file,
    #     should_remove_temp=True,
    # )

    # run_plot_lai_by_landuse_and_elevation(
    #     lai_folder_path=outer_lai_folder_path,
    #     land_use_path=outer_land_use_path,
    #     dem_file_path=outer_dem_file_path,
    #     elevation_bins=outer_elevation_bins,
    #     land_use_classes_of_interest=None,
    #     aoi_boundary_file=outer_aoi_boundary_file,
    #     should_remove_temp=True,
    # )

    # run_plot_lai_by_landuse_and_elevation_for_year(
    #     lai_folder_path=outer_lai_folder_path,
    #     land_use_path=outer_land_use_path,
    #     dem_file_path=outer_dem_file_path,
    #     elevation_bins=outer_elevation_bins,
    #     display_datas=outer_display_datas,
    #     year=outer_year,
    #     land_use_classes_of_interest=None,
    #     aoi_boundary_file=outer_aoi_boundary_file,
    #     should_remove_temp=True
    # )

    run_all_lai_analysis(
        lai_folder_path=outer_lai_folder_path,
        land_use_path=outer_land_use_path,
        dem_file_path=outer_dem_file_path,
        elevation_bins=outer_elevation_bins,
        land_use_classes_of_interest=None,
        aoi_boundary_file=outer_aoi_boundary_file,
        should_remove_temp=False
    )
