import os
import itertools
import xarray as xr
from typing import List, Union, BinaryIO
from pyspark import RDD, SparkContext
from fsspec.spec import AbstractBufferedFile
import s3fs
from pathlib import Path
from urllib.parse import urlparse


__all__ = ["load_dataset"]


def _read_files(
        paths: Union[List[str], str],
        aws_access_key_id: str = None,
        aws_secret_access_key: str = None,
        s3_endpoint_url: str = None,
        anon: bool = False
) -> List[Union[str, AbstractBufferedFile]]:
    if isinstance(paths, str):
        paths = [paths]
    files = []
    for path in paths:
        parsed_url = urlparse(path)
        if parsed_url.scheme == "":
            files.extend(
                _read_local_files(parsed_url.path)
            )
        elif parsed_url.scheme == "s3":
            files.extend(
                _read_s3_files(
                    bucket=parsed_url.netloc,
                    path=parsed_url.path,
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                    s3_endpoint_url=s3_endpoint_url,
                    anon=anon
                )
            )
    return files


def _read_local_files(
        path: str
) -> List[str]:
    split_path = path.split("/")
    if len(split_path) == 1 and split_path[0] != "":
        paths = list(Path("").glob(split_path[0]))
    elif split_path[0] == "":
        paths = list(Path("/").glob(os.path.join(*split_path[1:])))
    else:
        paths = list(Path(split_path[0]).glob(os.path.join(*split_path[1:])))
    return [str(p) for p in paths if p.is_file()]


def _read_s3_files(
        bucket: str,
        path: str,
        aws_access_key_id: str = None,
        aws_secret_access_key: str = None,
        s3_endpoint_url: str = None,
        anon: bool = False
) -> List[AbstractBufferedFile]:
    args = {}
    if anon:
        args["anon"] = anon
    else:
        if aws_access_key_id is not None:
            args["key"] = aws_access_key_id
        if aws_secret_access_key is not None:
            args["secret"] = aws_secret_access_key
        if s3_endpoint_url is not None:
            args["client_kwargs"] = {"endpoint_url": s3_endpoint_url}
    s3 = s3fs.S3FileSystem(**args)
    files_paths = s3.ls(bucket + path)
    files = [s3.open(file_path) for file_path in files_paths]
    return files


def load_dataset(
        sc: SparkContext,
        paths: Union[List[str], str],
        num_partitions: int = None,
        partition_on: Union[List[str], str] = "time",
        engine: str = None,
        aws_access_key_id: str = None,
        aws_secret_access_key: str = None,
        s3_endpoint_url: str = None,
        public_s3_bucket: bool = False
) -> RDD:
    """
    Read scientific files (netcdf, grib2, ...) and load them into a pyspark RDD.
    :param sc: The spark context
    :param paths: The path of the file/s to load
    :param num_partitions: The number of slices in the RDD
    :param partition_on: List of dimensions used to distribute the dataset
    :param engine: The engine used to read the files
    :param aws_access_key_id: AWS S3 access key
    :param aws_secret_access_key: AWS S3 secret key
    :param s3_endpoint_url: S3 endpoint url if different from AWS
    :param public_s3_bucket: a boolean to specify if the s3 bucket is public
    :return: A spark RDD of xarray datasets
    """
    if engine is None:
        engine = "h5netcdf"

    files = _read_files(
        paths=paths,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        s3_endpoint_url=s3_endpoint_url,
        anon=public_s3_bucket
    )

    # load the files as a xarray dataset
    xarray_dataset = xr.open_mfdataset(files, engine=engine).load()

    if isinstance(partition_on, str):
        partition_on = [partition_on]
    for dim in partition_on:
        if dim not in xarray_dataset.dims:
            raise Exception(f"dim {dim} doesn't exist in the dataset, you can choose from the following dimensions "
                            f"{list(xarray_dataset.dims.keys())}")

    indexes = list(itertools.product(*[[[i] for i in range(xarray_dataset.dims[dim])] for dim in partition_on]))
    indexes_dicts = [dict(zip(partition_on, indexes[i])) for i in range(len(indexes))]
    num_partitions = min(num_partitions, len(indexes_dicts)) if num_partitions is not None else len(indexes_dicts)
    return sc.parallelize(indexes_dicts, numSlices=num_partitions)\
        .map(lambda indexes_dict: xarray_dataset.isel(indexers=indexes_dict))
