from setuptools import setup, find_packages


setup(
    name='lai_data_processing',
    version='0.1.0',
    packeges=find_packages(),
    install_requires=[
        'numpy==2.0.1',
        'pandas==2.2.2',
        'rasterio==1.3.10',
        'matplotlib==3.9.1',
    ],
    entry_point={
        'console_scriots':[
            # TODO: Add console scripts
        ],
    },
    author='Ivan Shkvyr',
    author_email='shkvyr.i@czechglobe.cz',
    description=(
                 'This module processes Leaf Area Index (LAI) data and '
                 'calculates basic statistical indicators of the LAI index '
                 'based on land use and elevation. The processed data is then '
                 'saved in a CSV file and visualized in the form of graphs.'
                 ),
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/IvanShkvyr/lai_data_processing_project',
)