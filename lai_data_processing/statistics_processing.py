import numpy as np

def calculate_boxplot_stats(lai_data):
    """
    Calculate boxplot statistics for given LAI data.

    Parameters:
        lai_data (numpy.ndarray): Array containing LAI values.

    Returns:
        dict: A dictionary containing boxplot statistics.
    """
    Q1 = np.percentile(lai_data, 25)
    Q2 = np.percentile(lai_data, 50)
    Q3 = np.percentile(lai_data, 75)
    IQR = Q3 - Q1
    lower_whisker = Q1 - 1.5 * IQR
    upper_whisker = Q3 + 1.5 * IQR
    min_val = np.min(lai_data)
    max_val = np.max(lai_data)

    return {
        "Min": min_val,
        "Q1": Q1,
        "Median": Q2,
        "Q3": Q3,
        "Max": max_val,
        "Lower Whisker": lower_whisker,
        "Upper Whisker": upper_whisker,
    }


def calculate_mean_and_boxplot_lai(
                                    lai_data,
                                    landuse_data,
                                    elevation_data,
                                    landuse_class,
                                    elev_class
                                    ):
    """
    Calculate the mean LAI value and boxplot statistics for a given land use
    and elevation class.

    Parameters:
       lai_data (numpy.ndarray): Array containing LAI values.
       landuse_data (numpy.ndarray): Array containing land use classifications.
       elevation_data (numpy.ndarray): Array containing elevation classes.
       landuse_class (int): The land use class to filter.
       elev_class (int): The elevation class to filter.

    Returns:
        dict or None: A dictionary containing the mean LAI value and boxplot
                     statistics, or None if no pixels match the criteria.
    """
    mask = (landuse_data == landuse_class) & (elevation_data == elev_class)
    if np.any(mask):
        filtered_lai_data = lai_data[mask]
        mean_lai = np.mean(filtered_lai_data)
        boxplot_stats = calculate_boxplot_stats(filtered_lai_data)
        return {
            "Mean_LAI": mean_lai,
            **boxplot_stats
        }
    return None
