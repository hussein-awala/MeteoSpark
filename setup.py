from setuptools import setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="meteo-spark",
    version_config={
        "template": "{tag}",
    },
    description="A python package to process climate scientific files using pyspark.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    setup_requires=["wheel", "setuptools-git-versioning"],
    url="https://github.com/hussein-awala/MeteoSpark",
    project_urls={
        "Bug Tracker": "https://github.com/hussein-awala/MeteoSpark/issues",
    },
    author="Hussein Awala",
    author_email="hussein.awala.96@gmail.com",
    packages=["meteo_spark"],
    install_requires=["pyspark", "xarray", "dask", "h5netcdf", "fsspec", "s3fs"],
    python_requires=">=3.6",
    license="http://www.apache.org/licenses/LICENSE-2.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ]
)
