# CNN
from tensorflow import keras
import pandas as pd
from sklearn.model_selection import train_test_split

from training.preprocess import preprocessing

#lr
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score


from training.model import init_model_cnn, init_model_logistic, init_model_random_forest

import os
import sys



from database.db import engine_connect, Data_Csv

def prepare_data_after_departure():
    """
    Prepare the data for training
    """
    # on recupère les données sur la base de données
    print("On récupère les données de la base de données")
    # on utilise la fonction engine_connect pour se connecter à la base de données
    # et on utilise pandas pour lire la table data_csv
    df = pd.read_sql_table("data_csv",engine_connect())
    # on supprime la colonne index
    df = df.drop(columns=["index"])
    df = df.drop(columns=[
        "CRS_ARR_TIME", 
        "CRS_DEP_TIME",
        "YEAR",
        "MONTH",
        "DAY_OF_MONTH",
        "DAY_OF_WEEK",
        "AIRLINE_ID"
        ])


    print(df[0:5])

    # on process les données
    print("On prétraite les données")

    numerical_cols = [
        "ORIGIN_AIRPORT_ID",
        "DEST_AIRPORT_ID",
        "DEP_TIME_BLK",
        "ARR_TIME_BLK",
        "DEP_DELAY",
        "CRS_ELAPSED_TIME"
    ]

    categorical_cols = []

    # on utilise la fonction preprocessing pour prétraiter les données
    X, y, preprocessor = preprocessing(df, 
                                    numerical_cols=numerical_cols,
                                    categorical_cols=categorical_cols)

    # on convertie y en numpy array
    y = y.to_numpy()

    # on split les données
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)

    return X_train, X_test, y_train, y_test, preprocessor, df