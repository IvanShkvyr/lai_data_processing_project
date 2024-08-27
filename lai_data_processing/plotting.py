from typing import List

import matplotlib.pyplot as plt
import pandas as pd

from file_management import ensure_directory_exists


DEFAULT_DISPLAY_DATA = "Mean_LAI"
DEFAULT_PLOT_OUTPUT_DIR = "results\\png"


def plot_lai_by_landuse_and_elevation(
    data_frame: pd.DataFrame,
    display_data: str = DEFAULT_DISPLAY_DATA,
    results_folder_png: str = DEFAULT_PLOT_OUTPUT_DIR,
) -> None:
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
        display_data (str): Column name to be displayed in the plot, default is
          "Mean_LAI".
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
        plt.title(
            f"LAI for Landuse {landuse_class} and "
            f"Elevation {elevation_class} ({display_data})"
        )
        plt.xlabel("Day of Year")
        plt.ylabel("LAI")
        plt.legend()

        # Ensure the results folder exists
        results_folder_png_path = ensure_directory_exists(results_folder_png)

        # Define the path for saving the plot
        plot_file_path = (
            results_folder_png_path / f"lai_plot_landuse_{landuse_class}_"
            f"elevation_{elevation_class}.png"
        )

        # Save the plot as a PNG file
        plt.savefig(plot_file_path)
        plt.close()


def plot_lai_by_landuse_and_elevation_for_year(
    data_frame: pd.DataFrame,
    display_datas: List[str] | None = None,
    year: int | None = None,
    results_folder_png: str = DEFAULT_PLOT_OUTPUT_DIR,
) -> None:
    """
    Generates and saves plots of Leaf Area Index (LAI) data by land use and
    elevation class for a specified year.

    This function creates line plots showing the variation of LAI over the day
    of the year for each combination of land use and elevation class. Each plot
    represents data for a specific land use class and elevation zone,
    displaying the statistical measures specified in `display_datas` for the
    given year.

    Parameters:
        data_frame (pd.DataFrame): A DataFrame containing LAI data with columns
            'Date', 'Landuse', 'Elevation_class', and various statistical
            measures.
            The 'Date' column should be in datetime format.
        display_datas (list of str): A list of column names to be plotted.
            Defaults to ['Q1', 'Q3'].
        year (int): The year for which the data should be plotted.
        results_folder_png (str): The path to the folder where the PNG plot
          files will be saved. Defaults to 'results/png'.

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
                label=display_data,
            )

        # Set plot titles and labels
        plt.title(
            f"LAI for Landuse {landuse_class} and "
            f"Elevation {elevation_class} ({year})"
        )
        plt.xlabel("Day of Year")
        plt.ylabel("Value")
        plt.legend()

        # Define the path for saving the plot
        plot_file_path = (
            results_folder_png_path / f"lai_plot_landuse_{landuse_class}_"
            f"elevation_{elevation_class}_{year}.png"
        )

        # Save the plot as a PNG file
        plt.savefig(plot_file_path)
        plt.close()
