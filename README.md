# meteo-spark

spark-xarray is an open source project that aims to simplify the Climate Data Analysis
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