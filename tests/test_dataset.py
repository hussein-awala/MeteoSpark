from os import path
import unittest
from meteo_spark import load_dataset
from pyspark import SparkContext, SparkConf


class LoadDatasetTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        conf = SparkConf().setAppName("Meteo Spark test")
        cls.sc = SparkContext(conf=conf)
        cls.dir_path = path.dirname(path.realpath(__file__))

    def test_loading_one_file(self):
        dataset = load_dataset(
            self.sc,
            paths=path.join(self.dir_path, "test_data/point1_24H.nc"),
            partition_on=["time"]
        )
        number_of_ele = dataset.count()
        self.assertEqual(24, number_of_ele)

    def test_loading_multiple_file(self):
        dataset = load_dataset(
            self.sc,
            paths=path.join(self.dir_path, "test_data/*.nc"),
            partition_on=["time"]
        )
        number_of_ele = dataset.count()
        self.assertEqual(24, number_of_ele)

    def test_partition_on_latitude(self):
        dataset = load_dataset(
            self.sc,
            paths=path.join(self.dir_path, "test_data/*.nc"),
            partition_on=["latitude"]
        )
        number_of_ele = dataset.count()
        self.assertEqual(2, number_of_ele)

    def test_partition_on_latitude(self):
        dataset = load_dataset(
            self.sc,
            paths=path.join(self.dir_path, "test_data/*.nc"),
            partition_on=["latitude"]
        )
        number_of_ele = dataset.count()
        self.assertEqual(2, number_of_ele)

    def test_partition_on_longitude(self):
        dataset = load_dataset(
            self.sc,
            paths=path.join(self.dir_path, "test_data/*.nc"),
            partition_on=["longitude"]
        )
        number_of_ele = dataset.count()
        self.assertEqual(2, number_of_ele)

    def test_partition_on_latitude_and_longitude(self):
        dataset = load_dataset(
            self.sc,
            paths=path.join(self.dir_path, "test_data/*.nc"),
            partition_on=["latitude", "longitude"]
        )
        number_of_ele = dataset.count()
        self.assertEqual(4, number_of_ele)

    def test_partition_on_all_dims(self):
        dataset = load_dataset(
            self.sc,
            paths=path.join(self.dir_path, "test_data/*.nc"),
            partition_on=["time", "latitude", "longitude"]
        )
        number_of_ele = dataset.count()
        self.assertEqual(96, number_of_ele)

    @classmethod
    def tearDownClass(cls):
        cls.sc.stop()
