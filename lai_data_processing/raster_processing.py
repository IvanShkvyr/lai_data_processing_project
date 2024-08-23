from pathlib import Path

import numpy as np
import rasterio

from file_management import ensure_directory_exists


def convert_hdr_to_tif(
    data_file_path: Path,
    temp_lai_folder_path: str = "temp\\temp_lai_processing",
    driver: str = "ENVI",
) -> Path:
    """
    Convert a HDR format raster file to TIFF format and save it in a specified
    temporary folder.

    Parameters:
       data_file_path (Path): Path to the HDR format raster file.
       temp_lai_folder_path (str, optional): Path to the temporary folder where
                the TIFF file will be saved.
                Defaults to 'temp\\temp_lai_processing'.
       driver (str, optional): Rasterio driver to open the HDR file.
                Defaults is 'ENVI'.

    Returns:
       Path: Full path to the converted TIF file saved in the temporary folder.

    Notes:
        - The function reads data from the HDR file, updates its profile for
          TIF format, and saves it in the specified temporary folder.
        - If the specified temporary folder does not exist, it will be created
          before saving the TIFF file.
    """
    # Define the Path object for the temporary folder
    temp_lai_folder_path = ensure_directory_exists(temp_lai_folder_path)

    # Read data from HDR file
    with rasterio.open(data_file_path, "r", driver=driver) as src:
        data = src.read(1)
        profile = src.profile

        # Replace values less than 0 with NaN
        data[data < 0] = np.nan

    # Update profile for saving in GTiff format
    profile.update(
                    driver="GTiff",
                    dtype=rasterio.float32,
                    count=1,
                    nodata=np.nan,
                    compress="lzw"
                  )

    # Formulate path to tif file based on HDR file name in the temporary folder
    tiff_file_name = f"{Path(data_file_path).stem}.tif"
    out_tif_file = temp_lai_folder_path / tiff_file_name

    # Save data in TIFF format
    with rasterio.open(out_tif_file, "w", **profile) as dst:
        dst.write(data.astype(rasterio.float32), 1)

    return out_tif_file


def create_template_raster(
    base_raster: Path,
    output_folder: str = "temp",
    filename: str = "template_raster.tif",
) -> Path:
    """
    Create a template raster file based on another raster, filled with zeros.

    Parameters:
        base_raster (Path): Path to the base raster file from which metadata
          will be read.
        output_folder (str): Path to the output folder where the template
          raster file will be created.
        filename (str): Name of the output template raster file to be created.

    Returns:
        str: Path to the created template raster file.

    Notes:
        - This function reads the metadata (profile) from the base raster,
          removes unnecessary parameters, updates the profile for saving in
          GTiff format, and creates a new raster file filled with zeros.
        - The output raster file will have the same dimensions and coordinate
          system as the base raster, but all pixel values will be set to 0.
    """
    # Define the Path object for the output folder
    output_folder_path = ensure_directory_exists(output_folder)

    # Formulate the path to the output file
    template_raster_path = output_folder_path / filename

    # Open the base raster and read its profile
    with rasterio.open(base_raster, "r") as src:
        profile = src.profile

        # Remove nodata parameter if it exists (not needed for an empty file)
        profile.pop("nodata", None)

        # Update profile for saving in GTiff format
        profile.update(
                      driver="GTiff",
                      dtype=rasterio.float32,
                      count=1,
                      compress="lzw"
                      )

        # Create a new TIFF file with all pixels set to 0
        with rasterio.open(template_raster_path, "w", **profile) as dst:
            # Create an array filled with zeros
            zeros_array = np.zeros((src.height, src.width), dtype=np.float32)

            # Write the zeros array to the output file
            dst.write(zeros_array, 1)
    return template_raster_path


def read_raster(raster_path: Path) -> np.ndarray:
    """
    Reads the first band of a raster file and returns it as a numpy array.

    Parameters:
        raster_path (Path): The path to the raster file to be read.

    Returns:
        numpy.ndarray: The first band of the raster file as a 2D array.
    """
    with rasterio.open(raster_path) as src:
        return src.read(1)
