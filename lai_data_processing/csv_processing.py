from pathlib import Path

import pandas as pd

from file_management import ensure_directory_exists

def save_mean_lai_by_period_to_csv(
                                    dataframe: pd.DataFrame,
                                    results_folder: str = "results",
                                    filename: str = "daily_lai.csv"
                                   ) -> None:
    """
    Save the mean LAI values by period from a DataFrame to a CSV file.

    This function takes a DataFrame containing mean LAI values and saves it as
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


def save_mean_lai_by_day_of_year_to_csv(
        data_frame: pd.DataFrame,
        results_folder: str = "results"
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



