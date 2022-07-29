import glob
import json
import os
from pathlib import Path

import pandas as pd
import tqdm
from sklearn.cluster import KMeans


class GTDataAnalyzer:
    """
    this class analyze data retrieved from google trend
    """

    def __init__(self, directory, filesize=35):
        """data to initialize the GTDataAnalyzer

        Args:
            directory (strings): directory of the retrieved data
            filesize (int, optional): size of valid file, can be changed over the time . Defaults to 35.
        """
        self.directory = directory
        self.filesize = filesize

    def create_df_from_json_file(self):

        """create dataframe from json files retrieved from google trend api"""

        all_files = glob.glob(f"{self.directory}/*.json")
        # remove malformed file, each correct file take up about 35KB
        files = [
            file
            for file in all_files
            if round(os.path.getsize(file) / 1000) == self.filesize
        ]
        # remove duplicates
        files = list(set(files))
        keywords = [file.split("/")[-1].split(".")[0] for file in files]
        dataframe = pd.DataFrame()
        for file in tqdm(files):
            li = []
            keyword = file.split("/")[-1].split(".")[0]
            with open(file, "r") as f:
                data = json.load(f)
                for d in data["default"]["timelineData"]:
                    li.append(d["value"][0])
                dataframe = pd.concat([dataframe, pd.DataFrame({keyword: li})], axis=1)

        dataframe.dropna(axis=0, inplace=True)
        dataframe.to_csv(self.directory)

        return keywords, dataframe.T

    def find_clusters(self, filepath, n_clusters):
        """function for dataclustering

        Args:
            data (string): path to the dataset as csv file
        Return:
            list of keywords
        """

        df = pd.read_csv(filepath, on_bad_lines="skip")
        kmeans = KMeans(n_clusters, random_state=42)
        clusters = kmeans.fit_predict(df)

        return clusters
