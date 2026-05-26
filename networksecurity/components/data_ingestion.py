from networksecurity.exception.exception import NetworkSecurityException

from networksecurity.logging.logger import logging

#configuration of the data ingestion config 

from networksecurity.entity.config_entity import DataIngestionConfig
from networksecurity.entity.artifact_entity import DataIngestionArtifact


import os
import sys
import numpy as np
import pandas as pd
import pymongo 
from typing import List
from sklearn.model_selection import train_test_split
import certifi
ca = certifi.where()

from dotenv import load_dotenv
load_dotenv()

MONGO_DB_URL=os.getenv("MONGO_DB_URL")


class DataIngestion:
    def __init__(self,data_ingestion_config:DataIngestionConfig):
        try :
            self.data_ingestion_config=data_ingestion_config
            # FIXED 1: mongo_client initialize kiya (with certifi for SSL issues)
            self.mongo_client = pymongo.MongoClient(MONGO_DB_URL, tlsCAFile=ca)
            
            # FIXED 2: database aur collection ka naam define kiya 
            # Note: "AI" aur "NetworkData" ko apne actual MongoDB DB aur Collection ke naam se change kar lein.
            self.database_name = "KARTIKEY" 
            self.collection_name = "NetworkData"    
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def export_collection_as_dataframe(self):
        try:
            collection = self.mongo_client[self.database_name][self.collection_name]

            print("Database Name:", self.database_name)
            print("Collection Name:", self.collection_name)

            print("All Databases:")
            print(self.mongo_client.list_database_names())

            print("Collections:")
            print(
                self.mongo_client[self.database_name].list_collection_names()
            )

            data = list(collection.find())

            print("First Record:")
            print(collection.find_one())    

            print("Total records fetched:", len(data))

            df = pd.DataFrame(data)

            if "_id" in df.columns.to_list():
                df = df.drop("_id", axis=1)

            return df

        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def export_data_into_feature_store(self,dataframe:pd.DataFrame):
        try:
            feature_store_file_path=self.data_ingestion_config.feature_store_file_path
            # creating folder 
            dir_path=os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path,exist_ok=True)
            dataframe.to_csv(feature_store_file_path,index=False,header=True)
            return dataframe
        
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def split_data_as_train_test(self,dataframe:pd.DataFrame):
        try:
            train_set,test_set=train_test_split(
                dataframe, test_size=self.data_ingestion_config.train_test_split_ratio
            )
            logging.info("Performed train test split on the dataframe")

            logging.info(
                "Excited split_data_as_train_test method of Data_Ingestion class"
            )

            dir_path = os.path.dirname(self.data_ingestion_config.training_file_path)
            os.makedirs(dir_path,exist_ok=True)

            logging.info(f"Exporting train and test file path ")

            train_set.to_csv(
                self.data_ingestion_config.training_file_path,index = False, header=True
            )

            test_set.to_csv(
                self.data_ingestion_config.testing_file_path,index = False, header=True
            )
            logging.info(f"Exported Train and test file path")

        except Exception as e:
            raise NetworkSecurityException(e,sys)

    def initiate_data_ingestion(self):
        try:
            dataframe = self.export_collection_as_dataframe()
 
            dataframe = self.export_data_into_feature_store(dataframe)

            self.split_data_as_train_test(dataframe)

            dataingestionartifact = DataIngestionArtifact(
                trained_file_path=self.data_ingestion_config.training_file_path,
                test_file_path=self.data_ingestion_config.testing_file_path
            )

            return dataingestionartifact

        except Exception as e:
           raise NetworkSecurityException(e, sys)