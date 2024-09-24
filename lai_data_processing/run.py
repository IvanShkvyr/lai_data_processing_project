import asyncio
import time

from main import (
                  run_all_lai_analysis,
                  run_calculate_and_save_mean_lai_by_day_of_year,
                  run_calculate_and_save_mean_lai_by_period,
                  run_plot_lai_by_landuse_and_elevation,
                  run_plot_lai_by_landuse_and_elevation_for_year,
                  run_plot_lai_by_landuse_and_elevation_for_year_with_q1_q3_med_min_max
                  )
from plotting import plot_comparison_of_two_lai_datasets



# Path to the folder with LAI data
# outer_lai_folder_path = "D:\\CzechGlobe\\Task\\task_3_20240715_(Hidro_team_LAI_TimeSeries_Aggregation)\\data\Vegetation"
outer_lai_folder_path = "D:\\CzechGlobe\\Task\\task_3_20240715_(Hidro_team_LAI_TimeSeries_Aggregation)\\data\\Vegetation_2008"

# Path to the boundary file of the area of interest
# outer_aoi_boundary_file = "D:\\CzechGlobe\\Task\\task_3_20240715_(Hidro_team_LAI_TimeSeries_Aggregation)\\data\\border\\DYJ_500_hranice.shp"
outer_aoi_boundary_file = "D:\\CzechGlobe\\Task\\task_3_20240715_(Hidro_team_LAI_TimeSeries_Aggregation)\\data\\border\\povodi_Zelivky_32633.shp"

# Path to the land use file +++
outer_land_use_path = "D:\\CzechGlobe\\Task\\task_3_20240715_(Hidro_team_LAI_TimeSeries_Aggregation)\\data\\Land_Use\\CLC_Thaya_snap_2_model_extend.tif"

# Path to the digital elevation model file
outer_dem_file_path = "D:\\CzechGlobe\\Task\\task_3_20240715_(Hidro_team_LAI_TimeSeries_Aggregation)\\data\\DTM\\SRTM.tif"

# Setting boundaries for elevation classes
outer_elevation_bins = [400, 500, 600, 700, 800]

# Setting land use classes
outer_land_use_classes_of_interest = [311, 312, 313]

# Setting value:
# "Mean_LAI"
# "Min"
# "Q1"
# "Median"
# "Q3"
# "Max"
# "Lower Whisker"
# "Upper Whisker"

outer_display_datas = [
"Mean_LAI",
"Q1",
"Median",
"Q3",
]

outer_year = 2008

is_should_remove_temp = True

start_time = time.time()

# TODO: change names
df_1 = "D:\\CzechGlobe\\Task\\task_3_20240715_(Hidro_team_LAI_TimeSeries_Aggregation)\\results_done\\results_daily_csv\\lai_data_2008_311_700-800.csv"
df_2 = "D:\\CzechGlobe\\Task\\task_3_20240715_(Hidro_team_LAI_TimeSeries_Aggregation)\\results_done\\results_daily_csv\\lai_data_2008_312_700-800.csv"



"""
Creates CSV files for each cluster (land use / elevation / year).
Each file contains daily LAI statistical data for each day of the year.
The data is saved at: results\results_daily_csv\lai_data_2008_311_700-800.csv.
The filename includes the year of the data (2008), the land use class (311),
and the elevation range (700-800).
"""
# run_calculate_and_save_mean_lai_by_period(
#     lai_folder_path=outer_lai_folder_path,
#     land_use_path=outer_land_use_path,
#     dem_file_path=outer_dem_file_path,
#     elevation_bins=outer_elevation_bins,
#     land_use_classes_of_interest=outer_land_use_classes_of_interest,
#     aoi_boundary_file=outer_aoi_boundary_file,
#     should_remove_temp=is_should_remove_temp,
#     )


"""
Creates a single CSV file.
The file contains daily LAI statistical data averaged over all the processed
years. For example, a single day (01-03) will contain the average LAI values
for this cluster over several years.
The data is saved at: results\mean_characteristic_year.csv.
"""
# run_calculate_and_save_mean_lai_by_day_of_year(
#     lai_folder_path=outer_lai_folder_path,
#     land_use_path=outer_land_use_path,
#     dem_file_path=outer_dem_file_path,
#     elevation_bins=outer_elevation_bins,
#     land_use_classes_of_interest=None,
#     aoi_boundary_file=outer_aoi_boundary_file,
#     should_remove_temp=is_should_remove_temp,
# )


"""
Creates PNG files for each cluster (land use / elevation).
The file contains a chart where each line represents the average LAI values for
a specific year.
The data is saved at: results\png.
"""
# run_plot_lai_by_landuse_and_elevation(
#     lai_folder_path=outer_lai_folder_path,
#     land_use_path=outer_land_use_path,
#     dem_file_path=outer_dem_file_path,
#     elevation_bins=outer_elevation_bins,
#     land_use_classes_of_interest=None,
#     aoi_boundary_file=outer_aoi_boundary_file,
#     should_remove_temp=is_should_remove_temp,
# )


"""
Creates PNG files for each cluster (land use / elevation).
The file contains a chart for a specific year where each line represents
different LAI statistical values (can be customized using the attribute
outer_display_datas).
The data is saved at: results\png.
"""
# run_plot_lai_by_landuse_and_elevation_for_year(
#     lai_folder_path=outer_lai_folder_path,
#     land_use_path=outer_land_use_path,
#     dem_file_path=outer_dem_file_path,
#     elevation_bins=outer_elevation_bins,
#     display_datas=outer_display_datas,
#     year=outer_year,
#     land_use_classes_of_interest=None,
#     aoi_boundary_file=outer_aoi_boundary_file,
#     should_remove_temp=is_should_remove_temp
# )


"""
This function runs the first three functions simultaneously.
"""
# run_all_lai_analysis(
#     lai_folder_path=outer_lai_folder_path,
#     land_use_path=outer_land_use_path,
#     dem_file_path=outer_dem_file_path,
#     elevation_bins=outer_elevation_bins,
#     land_use_classes_of_interest=outer_land_use_classes_of_interest,
#     aoi_boundary_file=outer_aoi_boundary_file,
#     should_remove_temp=is_should_remove_temp
# )



"""
Creates PNG files for each cluster (land use / elevation / year).
The file contains a chart for a specific year showing the min, Q1, mean, Q3,
and max LAI values.
The data is saved at: results\png.
"""
# run_plot_lai_by_landuse_and_elevation_for_year_with_q1_q3_med_min_max(
#     lai_folder_path=outer_lai_folder_path,
#     land_use_path=outer_land_use_path,
#     dem_file_path=outer_dem_file_path,
#     elevation_bins=outer_elevation_bins,
#     year=outer_year,
#     land_use_classes_of_interest=outer_land_use_classes_of_interest,
#     aoi_boundary_file=outer_aoi_boundary_file,
#     should_remove_temp=is_should_remove_temp
# )


"""
TODO: Create docstring
"""
plot_comparison_of_two_lai_datasets(
    data_frame_first_path = df_1,
    data_frame_second_path = df_2,
)





end_time = time.time()
execution_time = end_time - start_time
print(f"Execution time of {execution_time:.4f} seconds")


