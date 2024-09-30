import asyncio
from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.mask import mask

from file_management import ensure_directory_exists


TEMP_LAI_DIR = "temp\\temp_lai_processing"
DEFAULT_HDR_DRIVER = "ENVI"
DEFAULT_TEMP_RASTER_NAME = "template_raster.tif"
DEFAULT_TEMP_DIR = "temp"


def convert_hdr_to_tif(
    data_file_path: Path,
    temp_lai_folder_path: str = TEMP_LAI_DIR,
    driver: str = DEFAULT_HDR_DRIVER,
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

    # Ensure the directory exists
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

    # Formulate path to tif file based on HDR file name in the temporary
    # folder
    tiff_file_name = f"{Path(data_file_path).stem}.tif"
    out_tif_file = temp_lai_folder_path / tiff_file_name

    # Save data in TIFF format
    with rasterio.open(out_tif_file, "w", **profile) as dst:
        dst.write(data.astype(rasterio.float32), 1)

    return out_tif_file


def cut_land_use_file_path(
    file_path: str,
    aoi_path: str,
    output_folder: str = DEFAULT_TEMP_DIR,
) -> str:
    """
    Crops a land use raster file to the boundaries defined by an area of
    interest (AOI) shapefile.

    This function reads the AOI shapefile to obtain the boundaries, then uses
    these boundaries to crop the provided land use raster file. The cropped
    raster is saved to the specified output folder, and the path to the newly
    created raster file is returned.

    Parameters:
       file_path (str): The path to the land use raster file that needs
        to be cropped.
       aoi_path (str): The path to the shapefile defining the area of
       interest (AOI) used for cropping.
       output_folder (str, optional): The folder where the cropped raster file
        will be saved. Defaults to "temp".

    Returns:
        str: The path to the cropped raster file.

    Notes:
        - The output raster file will be saved in GeoTIFF format.
    """
    # Loading the area of interest boundaries
    aoi_file = gpd.read_file(aoi_path)

    with rasterio.open(file_path) as src:
        raster_crs = src.crs

        # Reproject AOI if necessary
        if aoi_file.crs != raster_crs:
            aoi_file = aoi_file.to_crs(raster_crs)

        geoms = aoi_file.geometry.values
        out_image, out_transform = mask(src, geoms, crop=True)
        out_meta = src.meta.copy()
        out_meta.update(
            {
                "driver": "GTiff",
                "height": out_image.shape[1],
                "width": out_image.shape[2],
                "transform": out_transform,
            }
        )

    # Get the file name without the extension
    name_file = Path(file_path).name
    out_raster = f"{output_folder}/{name_file}"

    # Write the cropped image
    with rasterio.open(out_raster, "w", **out_meta) as dest:
        dest.write(out_image)

    return out_raster


def create_template_raster(
    base_raster: Path,
    output_folder: str = DEFAULT_TEMP_DIR,
    filename: str = DEFAULT_TEMP_RASTER_NAME,
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


def save_lai_to_raster(
    lai_adjusted: np.ndarray,
    reference_raster_path: str,
    output_path: str,
) -> None:
    """
    Saves the adjusted LAI data to a new raster file using the metadata from
    a reference raster.

    Parameters:
        lai_adjusted (numpy.ndarray): Adjusted LAI data to be saved.
        reference_raster_path (str): Path to the reference raster file, used to
          extract metadata. 
        output_path (str): Path where the new raster file will be saved.

    Raises:
        ValueError: If the dimensions of lai_adjusted do not match the
        reference raster.

    Returns:
        None: The function saves the LAI data as a new raster file.
    """
    # Open the reference raster to retrieve metadata
    with rasterio.open(reference_raster_path) as ref_raster:
        # Copy metadata from the reference raster
        meta = ref_raster.meta.copy()
        
        # Update metadata to match the data type of lai_adjusted (float32)
        meta.update(dtype='float32', count=1)
        
        # Check if the dimensions of lai_adjusted match the reference raster
        if lai_adjusted.shape != (meta['height'], meta['width']):
            raise ValueError("The dimensions of lai_adjusted do not match the \
reference raster dimensions.")
        
        # Write the adjusted LAI data to the new raster file
        with rasterio.open(output_path, 'w', **meta) as dst:
            dst.write(lai_adjusted.astype('float32'), 1)
