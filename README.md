# LAI data processing

A tool for processing LAI data and calculating statistical parameters based on land use classes and elevation bins.

## Table of Contents

1. [Description](#description)
2. [Requirements](#requirements)
3. [Installation](#installation)
4. [Usage Examples](#usage-examples)
5. [Project Structure](#project-structure)
6. [License](#license)
7. [Contact](#contact)

## Description

This project is designed for processing LAI (Leaf Area Index) data to determine statistical characteristics of the index across different land uses and elevation values.

The project accepts raw LAI data, which is then converted into a more accessible format. Using land use and elevation data, it calculates various statistical indicators. Users can define specific areas of interest by clipping the data according to shapefile boundaries.

Depending on the needs, the results can include:
- CSV files containing daily statistical data for each provided date
- CSV files with daily statistics aggregated by day of the year
- PNG files with graphs showing average LAI values for each studied year
- PNG files with graphs displaying statistical values of LAI for specific years

## Requirements

- List of software and packages required to run the project:
  - Python 3.9+
  - geopandas
  - numpy
  - pandas
  - rasterio
  - matplotlib

## Installation

Instructions for setting up the project. Example:

1. Clone the repository:
    ```bash
    git clone https://github.com/IvanShkvyr/lai_data_processing_project
    ```
2. Navigate to the project directory:
    ```bash
    cd lai_data_processing_project
    ```
3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage Examples

Examples of code or commands that show how to use the project.

```python
# Usage example
from main import (
                  run_all_lai_analysis,
                  run_calculate_and_save_mean_lai_by_day_of_year,
                  run_calculate_and_save_mean_lai_by_period,
                  run_plot_lai_by_landuse_and_elevation,
                  run_plot_lai_by_landuse_and_elevation_for_year
                  )

# Path to the folder with LAI data
outer_lai_folder_path = "your_path"

# Path to the boundary file of the area of interest
outer_aoi_boundary_file = "your_path"

# Path to the land use file +++
outer_land_use_path = "your_path"

# Path to the digital elevation model file
outer_dem_file_path = "your_path"

# Setting boundaries for elevation classes
outer_elevation_bins = [450]

# Setting land use classes
outer_land_use_classes_of_interest = [311, 312]

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

outer_year = 2001

should_remove_temp = True

run_calculate_and_save_mean_lai_by_period(
    lai_folder_path=outer_lai_folder_path,
    land_use_path=outer_land_use_path,
    dem_file_path=outer_dem_file_path,
    elevation_bins=outer_elevation_bins,
    land_use_classes_of_interest=outer_land_use_classes_of_interest,
    aoi_boundary_file=outer_aoi_boundary_file,
    should_remove_temp=True,
    )

run_calculate_and_save_mean_lai_by_day_of_year(
    lai_folder_path=outer_lai_folder_path,
    land_use_path=outer_land_use_path,
    dem_file_path=outer_dem_file_path,
    elevation_bins=outer_elevation_bins,
    land_use_classes_of_interest=None,
    aoi_boundary_file=outer_aoi_boundary_file,
    should_remove_temp=True,
)

run_plot_lai_by_landuse_and_elevation(
    lai_folder_path=outer_lai_folder_path,
    land_use_path=outer_land_use_path,
    dem_file_path=outer_dem_file_path,
    elevation_bins=outer_elevation_bins,
    land_use_classes_of_interest=None,
    aoi_boundary_file=outer_aoi_boundary_file,
    should_remove_temp=True,
)

run_plot_lai_by_landuse_and_elevation_for_year(
    lai_folder_path=outer_lai_folder_path,
    land_use_path=outer_land_use_path,
    dem_file_path=outer_dem_file_path,
    elevation_bins=outer_elevation_bins,
    display_datas=outer_display_datas,
    year=outer_year,
    land_use_classes_of_interest=None,
    aoi_boundary_file=outer_aoi_boundary_file,
    should_remove_temp=True
)

run_all_lai_analysis(
    lai_folder_path=outer_lai_folder_path,
    land_use_path=outer_land_use_path,
    dem_file_path=outer_dem_file_path,
    elevation_bins=outer_elevation_bins,
    land_use_classes_of_interest=outer_land_use_classes_of_interest,
    aoi_boundary_file=outer_aoi_boundary_file,
    should_remove_temp=True
)

```

## Project Structure 

lai_data_processing_project/  
│  
├── lai_data_processing/           # Main module  
│   ├── __init__.py  
│   ├── csv_processing.pyy  
│   ├── data_processing.py  
│   ├── file_management.py  
│   ├── main.py  
│   ├── plotting.py  
│   ├── raster_processing.py  
│   ├── run.py  
│   └── statistics_processing.py  
│  
├── LICENSE               # Licence file 
├── README.md             # Description file (this file)  
├── requirements.txt      # List of dependencies  
└── setup.py              # Installation script  

## License
Information about the license under which the project is distributed (e.g., MIT, Apache 2.0).

## Contact
If you have any questions or suggestions, you can contact me at:

Name: Ivan Shkvyr (GIS spetialist in CzeckGlobe)
Email: shkvyr.i@czechglobe.cz
