from pathlib import Path
import shutil
from typing import List


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
    should_remove_temp: bool, temp_path: str = "temp"
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
