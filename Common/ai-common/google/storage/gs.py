""" Connector and method accessing Google Cloud Storage """

import os
import logging

import pandas as pd

from google.cloud import storage


class GSConnector:
    """
    Class for interacting with GS Buckets
    """

    def __init__(self, cred_filepath: str, bucket: str):
        """
        Constructor for GSConnector
        :param cred_filepath: path to GS credential file
        :param bucket: GS bucket name
        """
        self._logger = logging.getLogger(__name__)
        gs_client = storage.Client.from_service_account_json(cred_filepath)
        self._bucket = gs_client.get_bucket(bucket)

    def push_file(self, local_path: str, gs_path: str):
        """
        Push a local file to gs
        :param local_path: local file path
        :param gs_path: remote GS file path

        """
        blob = self._bucket.blob(gs_path)

        self._logger.info("Pushing file %s to GS remote %s", local_path, gs_path)
        blob.upload_from_filename(local_path)

    def get_file(self, gs_path: str, local_path: str):
        """
        Download a GS file to local
        :param local_path: local file path
        :param gs_path: remote GS file path

        """
        blob = self._bucket.blob(gs_path)
        self._logger.info("Downloading file %s to %s", gs_path, local_path)
        blob.download_to_filename(local_path)

    def read_csv_to_df(self, gs_path: str):
        """
        Read a CSV file from GS bucket and convert it to Pandas dataframe
        :param gs_path: remote GS file path
        :returns Pandas dataframe from CSV file

        """
        self._logger.info("Reading GS file %s ", gs_path)
        self.get_file(gs_path, "tmp.csv")
        df = pd.read_csv("tmp.csv")
        os.remove("tmp.csv")
        return df

    def write_df_to_csv(self, data_frame: pd.DataFrame, gs_path: str):
        """
        Write a dataframe to GS CSV file
        :param gs_path: remote GS csv file path
        :data_frame Pandas dataframe
        """
        if data_frame.empty:
            self._logger.info("The dataframe is empty! No file will be written!")
            return None

        self._logger.info("Pushing data frame to CSV GS file %s ", gs_path)
        data_frame.to_csv("tmp.csv", index=False)
        self.push_file("tmp.csv")
        os.remove("tmp.csv")
