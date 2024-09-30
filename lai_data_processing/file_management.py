from pathlib import Path
import re
import shutil
from typing import List

from decorators import measure_time


DEFAULT_TEMP_DIR = "temp"


def ensure_directory_exists(directory_path: str) -> Path:
    """
    Ensure that the specified exists. If not, create it.

    Parameters:
       directory_path (str or Path): The path to the folder to check or create.

    Returns:
        Path: The Path object of the ensured directory.
    """
    path = Path(directory_path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    return path


def remove_directory_if_needed(
    should_remove_temp: bool, temp_path: str = DEFAULT_TEMP_DIR
) -> None:
    """
    Removes the specified directory if the removal flag is set to True.

    Parameters:
        should_remove_temp (bool): Flag indicating whether the directory should
          be removed.
        temp_path (str, optional): Path to the directory to be removed.
          Defaults to "temp".

    Returns:
        None

    Notes:
        - If `should_remove_temp` is `True`, the function will attempt to
          remove the directory specified by `temp_path`.
        - If the directory does not exist or `should_remove_temp` is `False`,
          no action is taken.
    """
    if should_remove_temp:
        temp_folder = Path(temp_path)

        # Check if the directory exists and is indeed a directory
        if temp_folder.exists() and temp_folder.is_dir():
            shutil.rmtree(temp_folder)

@measure_time
def grab_raw_lai_data_files(path: Path) -> List[Path]:
    """
    Get a list of raw LAI data files without extensions in the specified folder

    This function returns a list of files (without extensions) representing raw
    LAI data found in the specified folder.

    Parameters:
        path (Path): The path to the folder to scan.

    Returns:
        List[Path]: A list of Path objects representing raw LAI data files
                    without extensions in the folder.
    """

    files_without_extension = []

    for element in path.iterdir():
        if element.is_file() and element.suffix == "":
            files_without_extension.append(element)

    return files_without_extension


def extract_data_from_csv_filename(filename: str) -> tuple[int, str]:
    """
    Extract the land use class and elevation class from a CSV filename.

    This function uses a regular expression to extract the land use class and 
    elevation class from a filename that follows the pattern 
    'lai_data_<year>_<landuse_class>_<elevation_class>.csv'.

    Parameters:
        filename (str): The name of the CSV file, expected to follow the 
            pattern 'lai_data_<year>_<landuse_class>_<elevation_class>.csv'.
    
    Returns:
        tuple[int, str]: A tuple where the first element is the land use class 
                        (as an integer) and the second element is the
                        elevation class (as a string, in the format 'low-high')
    
    Raises:
        ValueError: If the filename does not match the expected pattern.
    
    Example:
        >>> extract_data_from_csv_filename('lai_data_2021_3_400-500.csv')
        (3, '400-500')
    """
    # Use regex to extract land use and elevation class from the filename
    match = re.search(r'lai_data_\d+_(\d+)_(\d+-\d+)\.csv', filename)
    
    # If a match is found, extract land use and elevation classes
    if match:
        landuse_class = int(match.group(1))
        elevation_class = match.group(2)

        return landuse_class, elevation_class
    
    else:
        # Raise an error if the filename does not match the expected format
        raise ValueError("Filename does not match expected pattern")
