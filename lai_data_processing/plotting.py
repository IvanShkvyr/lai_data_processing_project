from typing import List

import matplotlib.pyplot as plt
import pandas as pd

from decorators import measure_time
from file_management import (
                            ensure_directory_exists,
                            extract_data_from_csv_filename
                            )


DEFAULT_DISPLAY_DATA = "Mean_LAI"
DEFAULT_PLOT_OUTPUT_DIR = "results\\png"
DEFAULT_PLOT_COMPARE_OUTPUT_DIR = "results\\png_compare" 
DEFAULT_DISPLAY_DATAS = ["Min", "Q1", "Median", "Q3", "Max",]
DEFAULT_COLOR_SCHEME = {
    "diagram1": {
                    "color_min_max": "black",
                    "color_q1_q3": "lightgreen",
                    "color_median": "green"
                },
    "diagram2": {
                    "color_min_max": "red",
                    "color_q1_q3": "lightblue",
                    "color_median": "blue"
                }
}


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


# @measure_time
def plot_lai_by_landuse_and_elevation_for_year_with_q1_q3_med_min_max(
    data_frame: pd.DataFrame,
    year: int | None = None,
    display_datas: List[str] = DEFAULT_DISPLAY_DATAS,
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
    # Filter the DataFrame for the specified year
    year_data = data_frame[data_frame["Date"].dt.year == year]

    # Ensure the results folder exists
    results_folder_png_path = ensure_directory_exists(results_folder_png)

    # Iterate over each combination of land use and elevation class
    for (landuse_class, elevation_class), group_data in year_data.groupby(
        ["Landuse", "Elevation_class"]
    ):
        plt.figure(figsize=(10, 6))

        # Use the new function to plot the graph
        plot_single_lai_graph(
            group_data,
            color_scheme=DEFAULT_COLOR_SCHEME["diagram1"],
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


def plot_comparison_of_two_lai_datasets(
    data_frame_first_path: str,
    data_frame_second_path: str,
    results_folder_png: str = DEFAULT_PLOT_COMPARE_OUTPUT_DIR,
    ) -> None:
    """
    Plot a comparison of two LAI (Leaf Area Index) datasets and save the 
    result as a PNG file.

    The function reads two CSV files, each containing LAI data, and then plots 
    both datasets on the same graph for comparison. It also extracts land use 
    and elevation information from the filenames of the datasets and includes 
    these in the graph's title and output filename.

    Parameters:
        data_frame_first_path (str): Path to the first CSV file containing LAI 
            data.
        data_frame_second_path (str): Path to the second CSV file containing
            LAI data.
        results_folder_png (str, optional): Directory path where the resulting 
            PNG plot will be saved. Defaults to DEFAULT_PLOT_COMPARE_OUTPUT_DIR

    Returns:
        None: This function does not return any value, but it saves a PNG file
            with the comparison plot.
    """
    # Ensure the results folder exists or create it if it doesn't
    results_folder_png_path = ensure_directory_exists(results_folder_png)

    # Read the two CSV files into DataFrames
    data_frame_first = pd.read_csv(data_frame_first_path)
    data_frame_second = pd.read_csv(data_frame_second_path)

    # Extract land use class and elevation from the filename for the dataset
    landuse_cls_1, elevation_cls_1 = extract_data_from_csv_filename(
        data_frame_first_path
        )
    
    # Extract land use class and elevation from the filename for the dataset
    landuse_cls_2, elevation_cls_2 = extract_data_from_csv_filename(
        data_frame_second_path
        )

    # Set up the figure size for the plot
    plt.figure(figsize=(10, 6))

    # Plot the first dataset using the defined color scheme
    plot_single_lai_graph(
        data_frame_first,
        color_scheme=DEFAULT_COLOR_SCHEME["diagram1"],
        label_prefix=landuse_cls_1,
    )

    # Plot the second dataset using the defined color scheme
    plot_single_lai_graph(
        data_frame_second,
        color_scheme=DEFAULT_COLOR_SCHEME["diagram2"],
        label_prefix=landuse_cls_2,
    )

    # Set the plot title, using the extracted land use and elevation classes
    plt.title(
        f"Comparison of LAI Statistical Values between Land Use Classes\
 {landuse_cls_1} and {landuse_cls_2} in the Elevation Range\
 of {elevation_cls_1} m"
    )

    

    # Set labels for the x and y axes
    plt.xlabel("Day of Year")
    plt.ylabel("LAI Value")

    # Add a legend to differentiate between the two datasets
    plt.legend()

    # Define the path for saving the comparison plot
    plot_file_path = (
        results_folder_png_path / f"lai_comparison_landuse_{landuse_cls_1}_"
        f"elevation_{elevation_cls_1}.png"
    )

    # Save the plot as a PNG file and close the plot to free up memory
    plt.savefig(plot_file_path)
    plt.close()


def plot_single_lai_graph(
    group_data: pd.DataFrame,
    color_scheme: dict,
    label_prefix: str = None,
    display_datas: List[str] = DEFAULT_DISPLAY_DATAS,
    ) -> None:
    """
    Plot LAI (Leaf Area Index) data for a specific time period with various 
    statistical measures such as Q1, Q3, Min, Max, and Median.

    The function visualizes the LAI statistics for different time periods and 
    fills the area between Q1 and Q3 as a shaded region. It also plots the 
    specific statistical measures (Min, Max, and Median) over the date.

    Parameters:
        group_data (pd.DataFrame): DataFrame containing LAI statistics with 
          columns like 'Date', 'Q1', 'Q3', 'Min', 'Max', 'Median', etc.
        color_scheme (dict): A dictionary containing color specifications for 
          different plot elements like 'color_q1_q3', 'color_min_max', and 
          'color_median'.
        display_datas (List[str], optional): A list of statistical measures 
          (e.g., 'Q1', 'Q3', 'Min', 'Max', 'Median') to display on the plot. 
          Defaults to DEFAULT_DISPLAY_DATAS.

    Returns:
        None: The function generates the plot but does not return any value.
    """
    # Convert 'Date' column to datetime format if it is not already
    group_data["Date"] = pd.to_datetime(group_data["Date"])

    # Check if both 'Q1' and 'Q3' are in the display_datas list
    # If yes, plot the shaded area between Q1 and Q3
    if "Q1" in display_datas and "Q3" in display_datas:

        plt.fill_between(
            group_data["Date"].dt.dayofyear,
            group_data["Q1"],
            group_data["Q3"],
            color=color_scheme["color_q1_q3"],
            alpha=0.5,
            label=f"{label_prefix} Q1 - Q3",
        )

    # Iterate through each specified statistical measure in display_datas
    for display_data in display_datas:

        # If the current measure is 'Min' or 'Max', plot it with specific style
        if display_data == "Min" or display_data == "Max":

            plt.plot(
                group_data["Date"].dt.dayofyear,
                group_data[display_data],
                color=color_scheme["color_min_max"],
                linestyle="-",
                linewidth=0.5,
                label=f"{label_prefix} {display_data}",
            )

        # If the current measure is 'Median', plot it with specific styling
        elif display_data == "Median":
            plt.plot(
                group_data["Date"].dt.dayofyear,
                group_data[display_data],
                color=color_scheme["color_median"],
                linestyle="-",
                linewidth=2,
                label=f"{label_prefix} {display_data}",
            )

        # For any other measure (other than Q1, Q3), plot it as is
        elif display_data not in ["Q1", "Q3"]:
            plt.plot(
                group_data["Date"].dt.dayofyear,
                group_data[display_data],
                label=f"{label_prefix} {display_data}",
            )
чісвло87тии78рть905б
