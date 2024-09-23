from pathlib import Path
import os

import pandas as pd

from file_management import ensure_directory_exists


DEFAULT_RESULTS_DIR = "results"
DEFAULT_CSV_FOLDER = "results\\results_daily_csv"
DEFAULT_CSV_PREFIX_FILENAME = "daily_lai.csv"


def save_mean_lai_by_period_to_csv(
    dataframe: pd.DataFrame,
    results_folder: str = DEFAULT_CSV_FOLDER,
    ) -> None:
    """
    Save mean LAI values grouped by year, land use, and elevation class to
    separate CSV files.

    This function takes a DataFrame containing mean LAI values along with their
    corresponding dates, land use types, and elevation classes. It processes
    the DataFrame to extract the year from the "Date" column and then groups
    the data by unique combinations of year, land use, and elevation class.
    Each unique group is saved to a separate CSV file named in the format:
    "lai_data_{year}_{Landuse}_{Elevation_class}.csv".

    Parameters:
        dataframe (pd.DataFrame): The DataFrame containing the mean LAI values
            along with columns "Date", "Landuse", and "Elevation_class".
        results_folder (str, optional): Path to the folder where the CSV files
            will be saved. Defaults to 'results'.

    Returns:
        None

    Notes:
        - The function ensures that the specified results folder exists before
          attempting to save the files.
        - The "Date" column in the DataFrame is used to extract the year for
          grouping purposes.
        - The DataFrame is expected to contain the columns "Date", "Landuse",
          and "Elevation_class".
        - Columns "Year", "Landuse", and "Elevation_class" are removed from
          each group before saving to CSV.
    """
    dataframe["Date"] = pd.to_datetime(dataframe["Date"])
    dataframe["Year"] = dataframe["Date"].dt.year

    # Ensure the results folder exists
    directory_path = ensure_directory_exists(results_folder)

    # Group by the unique combinations of Years, Landuse, and Elevation_class
    grouped = dataframe.groupby(["Year", "Landuse", "Elevation_class"])

    # Iterate through each group and save to a CSV
    for (year, landuse, elevation_class), group in grouped:

        # Formulate the full path to the output CSV file
        filename = f"lai_data_{year}_{landuse}_{elevation_class}.csv"
        filepath = os.path.join(directory_path, filename)

        group = group.drop(["Year", "Landuse", "Elevation_class"], axis=1)

        # Save the DataFrame to a CSV file
        group.to_csv(filepath, index=False)


def save_mean_lai_by_day_of_year_to_csv(
    data_frame: pd.DataFrame, results_folder: str = DEFAULT_RESULTS_DIR
) -> None:
    """
    Calculates the mean LAI values for each day of the year grouped by land use
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

    # Group by 'Day_of_Year', 'Landuse', and 'Elevation_class' and calculate
    # the mean LAI
    mean_lai_by_day = (
        data_frame.groupby(["Day_of_Year", "Landuse", "Elevation_class"])
        .agg(
            {
                "Mean_LAI": "mean",
                "Min": "mean",
                "Q1": "mean",
                "Median": "mean",
                "Q3": "mean",
                "Max": "mean",
                "Lower Whisker": "mean",
                "Upper Whisker": "mean",
            }
        )
        .reset_index()
    )

    # Save the DataFrame with mean LAI values to a CSV file
    mean_lai_by_day.to_csv(mean_characteristic_year_path, index=False)
