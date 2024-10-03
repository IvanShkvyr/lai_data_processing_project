from pathlib import Path
import os

import pandas as pd
import numpy as np

from file_management import ensure_directory_exists


DEFAULT_RESULTS_DIR = "results"
DEFAULT_CSV_FOLDER = "results\\results_daily_csv"
DEFAULT_CSV_PREFIX_FILENAME = "daily_lai.csv"
DEFAULT_CSV_YEAR_FILENAME = "mean_characteristic_year.csv"
DEFAULT_CSV_FILENAME = "lai.csv"


def save_data_to_csv(
    dataframe: pd.DataFrame,
    filename: str = DEFAULT_CSV_FILENAME,
    results_folder: str = DEFAULT_RESULTS_DIR,
    ) -> None: 
    """
    Save the LAI data from the provided DataFrame to a CSV file.

    This function saves the entire DataFrame as a CSV file. The user can
    specify the name of the file and the folder where the CSV will be stored.
    If no custom filename or folder is provided, the function will use the
    default settings. The DataFrame is saved without the index column.

    Parameters:
        dataframe (pd.DataFrame): The DataFrame containing LAI data to be saved
        filename (str, optional): The name of the CSV file. Defaults to the
                                   value specified in `DEFAULT_CSV_FILENAME`
        results_folder (str, optional): Path to the folder where the CSV file 
                                        will be saved. Defaults to the value 
                                        specified in `DEFAULT_RESULTS_DIR`

    Returns:
        None

    Notes:
        - The function ensures that the specified results folder exists before
          attempting to save the file
        - The DataFrame is saved without the index column to keep the CSV clean
    """
    # Ensure the results folder exists
    directory_path = ensure_directory_exists(results_folder)

    # Formulate the full path to the output CSV file
    filepath = os.path.join(directory_path, filename)

    # Save the DataFrame to a CSV file
    dataframe.to_csv(filepath, index=False)


def create_stat_lai_by_clusters(
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

    # Group by the unique combinations of Years, Landuse, and Elevation_class
    grouped = dataframe.groupby(["Year", "Landuse", "Elevation_class"])

    # Iterate through each group and save to a CSV
    for (year, landuse, elevation_class), group in grouped:

        # Formulate the full path to the output CSV file
        filename = f"lai_data_{year}_{landuse}_{elevation_class}.csv"

        group = group.drop(["Year", "Landuse", "Elevation_class"], axis=1)

        save_data_to_csv(group, filename, results_folder)


def create_stat_lai_by_day_of_year(
    data_frame: pd.DataFrame,
    results_folder: str = DEFAULT_RESULTS_DIR,
    file_name: str = DEFAULT_CSV_YEAR_FILENAME,
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
    # Convert the 'Date' column to datetime format if not already
    data_frame["Date"] = pd.to_datetime(data_frame["Date"])

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

    save_data_to_csv(mean_lai_by_day, file_name, results_folder)


def create_lai_modification_csv(
        df: pd.DataFrame,
        current_landuse_class: int,
        target_landuse_class: int,
        ) -> pd.DataFrame:
    """
    Create a DataFrame that calculates the modification ratio for LAI
    adjustment between two land use classes (current and target) across
    different elevation classes and dates.

    This function processes the input DataFrame, filtering data by land use
    classes (current and target) and merging the data for comparison. It
    computes the ratio (DIFF) of median LAI values between the target and 
    current land use classes. The result is used for further LAI adjustment
    based on land use changes.

    Parameters:
        df (pd.DataFrame): Input DataFrame containing LAI data for various
                           dates, land use classes, and elevation classes.
        current_landuse_class (int): The land use class to be adjusted
                           (current).
        target_landuse_class (int): The land use class to which adjustment will
                            be made (target).

    Returns:
        pd.DataFrame
    """
    # Filter data for the current and target land use class
    df_target = df[df['Landuse'] == target_landuse_class]
    df_current = df[df['Landuse'] == current_landuse_class]

    # Merge data based on 'Date' and 'Elevation_class' columns
    merged_df = pd.merge(
                        df_target,
                        df_current,
                        on=['Date', 'Elevation_class'],
                        suffixes=('_target', '_current')
                        )

    # Select relevant columns for the result DataFrame
    result_df = merged_df[[
                            'Date',
                            'Elevation_class',
                            'Landuse_target',
                            'Landuse_current',
                            'Median_target',
                            'Median_current',
                            'Q1_target',
                            'Q3_target',
                          ]]
    
    result_df = result_df.copy()
    result_df.loc[:, 'Sum_of_pix'] = np.nan
    result_df.loc[:, 'Count_unchanged_pix'] = np.nan
    
    # Create a copy of the DataFrame to avoid modification warnings
    # Add the 'DIFF' column, which is the ratio of median LAI values
    copy_df = result_df.copy()
    copy_df["DIFF"] = copy_df['Median_target'] / copy_df['Median_current']

    return copy_df
