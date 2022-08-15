import pystore
import pandas as pd
import numpy as np
from tqdm import tqdm
import os
import time
import re


class DataBase:
    def __init__(self, store_dir: str = "DataStore/PQT") -> None:
        """
        DataBase class handling all of the pystore functionality, also contains Test class for manipulating indiv. test's data.
        store_dir: Path to PyStore
        """
        pystore.set_path(os.path.dirname(os.path.abspath(__file__)))

        self.store = pystore.store(store_dir)

        self.collection = self.store.collection("Tests")

        self.loaded_df = None

    def load_df(self, filename: str, *df_kwargs) -> None:
        """
        Load in DataFrame from file, loaded_df is held as (name, pd.DataFrame) tuple.
        filename: Path to .csv to be loaded
        """
        # try:
        df = pd.read_csv(filename, skiprows=11, skipfooter=2)
        
        print("read")
        
        df = df.dropna(axis=1, how="all")
        df = df.dropna(axis=0, how="all")
        print("dropped nan")
        df = df.astype(float)
        print("to float")
        self.loaded_df = (filename[:-4], df)
        print(df.head(1))
        # except:
        #     print("Error reading file {}...".format(filename))

    def store_df(
        self, name: str = None, df: pd.DataFrame = None, collection="Tests"
    ) -> None:
        """
        Store loaded or specified dataframe as pystore item (.parquet format).
        name: Name of test to be labelled
        df: pandas DataFrame object to be stored
        """
        if df is None:
            df = self.loaded_df[1]
        if name is None:
            name = self.loaded_df[0]

        name = name.split("/")
        name = name[-1]

        try:
            self.collection.write(name, df, overwrite=True)
            print("DataFrame written - {}".format(name))
        except:
            print("DataFrame write failed - {}".format(name))

    def find_filenames(self, path, suffix=".csv") -> list:
        # path_to_dir = os.path.dirname(os.path.abspath(path))
        filenames = os.listdir(path)
        return [filename for filename in filenames if filename.endswith(suffix)]

    def batch_transform_df(
        self, directory: str, collection: str = "Tests", **df_read_kwargs
    ) -> None:
        """
        Load and store directory of .csv test files, must all be similar format.
        directory: Path to directory of test .csv's.
        collection: Name of collection directories to be stored in.
        df_read_kwargs: Keyword args to be pass to pd.read_csv, e.g. skiprows, records...
        """
        files = self.find_filenames(directory)
        for file in tqdm(files):
            try:
                self.load_df(directory + "/" + file, **df_read_kwargs)
                self.store_df(collection=collection)

            except:
                print("File {} in {} failed to convert...".format(file, directory))
        print("Files successfully converted.")


class Test:
    def __init__(self, db, item_name):
        """
        Test object containing raw timeseries data from DataStore, metadata on test parameters and classified Sigma data.
        """
        self.db = db
        self.item = self.db.collection.item(item_name)
        self.data = self.item.to_pandas()
        self.test_name = item_name
        self.puffs = {}
        self.sigma_data = None
        self.sigma_results = None

    def load_puffs(self):
        for i in list(self.data["Puff Count"].unique()):
            self.puffs[i] = self.data.loc["Puff Count" == i, :]


class Results:
    def __init__(self, db, result_sub=None):
        """
        top-level data-structure containing results of all categorised tests
        """
        self.db = db
        self.results = self.db.store.collection("Results")
        self.results_sub = result_sub

        if result_sub is None:
            self.data = self.results.item("main")
            self.results_sub = "main"
        else:
            self.data = self.results.item(result_sub).to_pandas()

        if self.data.empty():
            self.data = self.data.assign(
                [
                    "Test Name",
                    "Puffs",
                    "Voltage [V]",
                    "Power [W]",
                    "Mixture",
                    "Date",
                    "Puff Length [ms]",
                    "Puff Period [ms]",
                    "Time Run [s]",
                    "Sigma Detection",
                    "Sigma Puff",
                    "IQOS Detection, IQOS Puff",
                    "Max Resistance [Ohms]",
                ]
            )

    def update(self, inplace=True):
        if inplace:
            self.results.write(self.results_sub, self.data)
        else:
            return self.data
