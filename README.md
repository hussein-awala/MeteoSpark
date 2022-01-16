# meteo-spark

meteo-spark is an open source project that aims to simplify the Climate Data Analysis
using [PySpark](https://spark.apache.org/docs/latest/api/python/index.html),
which allow the processing of very big files saved in the cloud
([S3](https://docs.aws.amazon.com/s3), [GCS](https://cloud.google.com/storage/docs),
...) on a large pyspark cluster managed by [YARN](https://hadoop.apache.org/docs/stable/hadoop-yarn/hadoop-yarn-site/YARN.html)
or [Kubernetes](https://kubernetes.io/).

## Installation
Install and update using [pip](https://pip.pypa.io/en/stable/getting-started/):
```shell
pip install meteo-spark
```

## A Simple Example

```python
from pyspark import SparkContext, SparkConf
from meteo_spark import load_dataset

# create a new spark context
conf = SparkConf().setAppName("Meteo Spark app")
sc = SparkContext(conf=conf)

# use the method load_dataset to read the netcdf files
# and load them as a RDD partitioned by longitude and latitude with 10 slices
meteo_data = load_dataset(
    sc,
    paths="data/*.nc",
    num_partitions=10,
    partition_on=["longitude", "latitude"]
)
# calculate the max temperature for each point for the whole period
max_meteo_data = meteo_data.map(lambda x: x["t2m"].max())
# take the first element
max_meteo_data.take(1)
```

## Process S3 data
In this example we use a local S3 server (minio), so we need to specify the S3 endpoint url:
```python
import os
# create env vars for AWS access and secret key
# we can also provide the access and the secret keys as arguments or store them in ~/.aws/credentials,
# for more info, you can read https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html
os.environ["AWS_ACCESS_KEY_ID"] = "minioadmin"
os.environ["AWS_SECRET_ACCESS_KEY"] = "minioadmin"

from pyspark import SparkContext, SparkConf
from meteo_spark import load_dataset
import xarray as xr
conf = SparkConf().setAppName("Process S3 files").set("spark.executor.instances", "3")
sc = SparkContext(conf=conf)

# load the data file from minio bucket and slice it by latitude and longitude (RDD of 10 partitions)
dataset = load_dataset(
    sc,
    paths=["s3://climate-bucket/one_day.nc"],
    num_partitions=10,
    partition_on=["latitude", "longitude"],
    s3_endpoint_url="http://minio:9000"
)

# calculate the mean values over time
daily_mean = dataset.map(lambda x: x.mean(["time"]))

# reduce the data and create a new xarray dataset
result_dataset = daily_mean.reduce(lambda x, y: xr.combine_by_coords([x, y]))
```