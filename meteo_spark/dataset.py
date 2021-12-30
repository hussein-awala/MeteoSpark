import itertools
import xarray as xr
from typing import List, Union
from pyspark import RDD, SparkContext


def load_dataset(
        sc: SparkContext,
        paths: Union[List[str], str],
        num_partitions: int = None,
        partition_on: Union[List[str], str] = "time",
        engine: str = None
) -> RDD:
    """
    Read scientific files (netcdf, grib2, ...) and load them into a pyspark RDD.
    :param sc: The spark context
    :param paths: The path of the file/s to load
    :param num_partitions: The number of slices in the RDD
    :param partition_on: List of dimensions used to distribute the dataset
    :param engine: The engine used to read the files
    :return: A spark RDD of xarray datasets
    """
    if engine is None:
        engine = "netcdf4"

    # load the files as a xarray dataset
    xarray_dataset = xr.open_mfdataset(paths, engine=engine).load()

    if isinstance(partition_on, str):
        partition_on = [partition_on]
    for dim in partition_on:
        if dim not in xarray_dataset.dims:
            raise Exception(f"dim {dim} doesn't exist in the dataset, you can choose from the following dimensions "
                            f"{list(xarray_dataset.dims.keys())}")

    indexes = list(itertools.product(*[range(xarray_dataset.dims[dim]) for dim in partition_on]))
    indexes_dicts = [dict(zip(partition_on, indexes[i])) for i in range(len(indexes))]
    num_partitions = min(num_partitions, len(indexes_dicts)) if num_partitions is not None else len(indexes_dicts)
    return sc.parallelize(indexes_dicts, numSlices=num_partitions)\
        .map(lambda indexes_dict: xarray_dataset.isel(indexers=indexes_dict))
