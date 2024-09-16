from main import (
                  run_all_lai_analysis,
                  run_calculate_and_save_mean_lai_by_day_of_year,
                  run_calculate_and_save_mean_lai_by_period,
                  run_plot_lai_by_landuse_and_elevation,
                  run_plot_lai_by_landuse_and_elevation_for_year,
                  run_plot_lai_by_landuse_and_elevation_for_year_with_q1_q3_med_min_max
                  )



# Path to the folder with LAI data
outer_lai_folder_path = "D:\\CzechGlobe\\Task\\task_3_20240715_(Hidro_team_LAI_TimeSeries_Aggregation)\\data\Vegetation"

# Path to the boundary file of the area of interest
outer_aoi_boundary_file = "D:\\CzechGlobe\\Task\\task_3_20240715_(Hidro_team_LAI_TimeSeries_Aggregation)\\data\\border\\DYJ_500_hranice.shp"

# Path to the land use file +++
outer_land_use_path = "D:\\CzechGlobe\\Task\\task_3_20240715_(Hidro_team_LAI_TimeSeries_Aggregation)\\data\\Land_Use\\CLC_Thaya_snap_2_model_extend.tif"

# Path to the digital elevation model file
outer_dem_file_path = "D:\\CzechGlobe\\Task\\task_3_20240715_(Hidro_team_LAI_TimeSeries_Aggregation)\\data\\DTM\\SRTM.tif"

# Setting boundaries for elevation classes
outer_elevation_bins = [450]

# Setting land use classes
outer_land_use_classes_of_interest = [312, 311]

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

outer_display_datas = [
"Mean_LAI",
"Q1",
"Median",
"Q3",
]

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

# run_all_lai_analysis(
#     lai_folder_path=outer_lai_folder_path,
#     land_use_path=outer_land_use_path,
#     dem_file_path=outer_dem_file_path,
#     elevation_bins=outer_elevation_bins,
#     land_use_classes_of_interest=outer_land_use_classes_of_interest,
#     aoi_boundary_file=outer_aoi_boundary_file,
#     should_remove_temp=True
# )

run_plot_lai_by_landuse_and_elevation_for_year_with_q1_q3_med_min_max(
    lai_folder_path=outer_lai_folder_path,
    land_use_path=outer_land_use_path,
    dem_file_path=outer_dem_file_path,
    elevation_bins=outer_elevation_bins,
    year=outer_year,
    land_use_classes_of_interest=None,
    aoi_boundary_file=outer_aoi_boundary_file,
    should_remove_temp=True
)
