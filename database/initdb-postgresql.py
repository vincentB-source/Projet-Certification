from sqlalchemy import Column, Integer, String, BigInteger, Double, Text
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import pandas as pd
from os.path import join as join


Base = declarative_base()
# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://vincent:vincent@localhost/M7-brief0?charset=utf8mb4"
SQLALCHEMY_DATABASE_URL = "postgresql://vincent:vincent@localhost/projet-certification"

# Connexion à une base Mysql
engine = create_engine(SQLALCHEMY_DATABASE_URL)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session() 

# on récupère le CSV pour clean des data avant injection en base
# voir NoteBook matrice-notebook.ipynb
dfs = []

for month in range(1, 2):
### on limite à 1 mois pour le testcsv"
### for month in range(1, 13):
    file = f"data/2016_{month:02}.csv"
    try:
        tmp = pd.read_csv(file, on_bad_lines='warn', low_memory=False)
        dfs.append(tmp)
        print(f"Loaded {file} ✅")
    except pd.errors.ParserError as e:
        print(f"ParserError for {file}: {e}")
    print("-" * 50)

# Concat all dataframes in "full_df"
df_data = pd.concat(dfs, ignore_index=True)
df_data = df_data.drop_duplicates()

# liste blanche des colonnes
df_filtered = df_data[[
    "YEAR",
#    "QUARTER",
    "MONTH",
    "DAY_OF_MONTH",
    "DAY_OF_WEEK",
#    "FL_DATE",
#    "UNIQUE_CARRIER",
    "AIRLINE_ID",
#    "CARRIER",
#    "TAIL_NUM",
#    "FL_NUM",
    "ORIGIN_AIRPORT_ID",
#    "ORIGIN_AIRPORT_SEQ_ID",
#    "ORIGIN_CITY_MARKET_ID",
#    "ORIGIN",
#    "ORIGIN_CITY_NAME",
#    "ORIGIN_STATE_ABR",
#    "ORIGIN_STATE_FIPS",
#    "ORIGIN_STATE_NM",
#    "ORIGIN_WAC",
    "DEST_AIRPORT_ID",
#    "DEST_AIRPORT_SEQ_ID",
#    "DEST_CITY_MARKET_ID",
#    "DEST",
#    "DEST_CITY_NAME",
#    "DEST_STATE_ABR",
#    "DEST_STATE_FIPS",
#    "DEST_STATE_NM",
#    "DEST_WAC",
    "CRS_DEP_TIME",
#    "DEP_TIME",
    "DEP_DELAY",
#    "DEP_DELAY_NEW",
#    "DEP_DEL15",
#    "DEP_DELAY_GROUP",
    "DEP_TIME_BLK",
#    "TAXI_OUT",
#    "WHEELS_OFF",
#    "WHEELS_ON",
#    "TAXI_IN",
    "CRS_ARR_TIME",
#    "ARR_TIME",
#    "ARR_DELAY",
#    "ARR_DELAY_NEW",
    "ARR_DEL15",
#   "ARR_DELAY_GROUP",
    "ARR_TIME_BLK",
#    "CANCELLED",
#   "CANCELLATION_CODE",
#    "DIVERTED",
    "CRS_ELAPSED_TIME",
#    "ACTUAL_ELAPSED_TIME",
#    "AIR_TIME",
    ]]

# on convertie les colonnes de time block de type string en type int
df_filtered['DEP_TIME_BLK'] = df_filtered['DEP_TIME_BLK'].map({
        "0001-0559" : 0,
        "0600-0659" : 1,
        "0700-0759" : 2,
        "0800-0859" : 3,
        "0900-0959" : 4,
        "1000-1059" : 5,
        "1100-1159" : 6,
        "1200-1259" : 7,
        "1300-1359" : 8,
        "1400-1459" : 9,
        "1500-1559" : 10,
        "1600-1659" : 11,
        "1700-1759" : 12,
        "1800-1859" : 13,
        "1900-1959" : 14,
        "2000-2059" : 15,
        "2100-2159" : 16, 
        "2200-2259" : 17,
        "2300-2359" : 18
    })   

df_filtered['ARR_TIME_BLK'] = df_filtered['ARR_TIME_BLK'].map({
        "0001-0559" : 0,
        "0600-0659" : 1,
        "0700-0759" : 2,
        "0800-0859" : 3,
        "0900-0959" : 4,
        "1000-1059" : 5,
        "1100-1159" : 6,
        "1200-1259" : 7,
        "1300-1359" : 8,
        "1400-1459" : 9,
        "1500-1559" : 10,
        "1600-1659" : 11,
        "1700-1759" : 12,
        "1800-1859" : 13,
        "1900-1959" : 14,
        "2000-2059" : 15,
        "2100-2159" : 16, 
        "2200-2259" : 17,
        "2300-2359" : 18
    })  

# on supprime les lignes avec des valeurs manquantes (constatées sur les colonnes de retard au départ et de retard à l'arrivée)
df_filtered = df_filtered.dropna(subset=['DEP_DELAY', 'ARR_DEL15'])

print(f"Nombre de vol dans df_filtered: {len(df_filtered)}")
print("On sauvegarde les données de vol dans la base")
# on sauvegarde les données de vol en base
with engine.connect() as con:
    df_filtered.to_sql(
    name="data_csv", 
    con=con, 
    if_exists="replace"
    )

######################################################################################################################################################
# on va créer une liste d'aéroport
df_aeroport_orig = df_data[[
    "ORIGIN_AIRPORT_ID",
    "ORIGIN_AIRPORT_SEQ_ID",
    "ORIGIN_CITY_MARKET_ID",
    "ORIGIN",
    "ORIGIN_CITY_NAME",
    "ORIGIN_STATE_ABR",
    "ORIGIN_STATE_FIPS",
    "ORIGIN_STATE_NM",
    "ORIGIN_WAC",
]]
df_aeroport_dest = df_data[[
    "DEST_AIRPORT_ID",
    "DEST_AIRPORT_SEQ_ID",
    "DEST_CITY_MARKET_ID",
    "DEST",
    "DEST_CITY_NAME",
    "DEST_STATE_ABR",
    "DEST_STATE_FIPS",
    "DEST_STATE_NM",
    "DEST_WAC",
]]
df_aeroport_orig = df_aeroport_orig.drop_duplicates()
df_aeroport_dest = df_aeroport_dest.drop_duplicates()
# Renommer la colonne
df_aeroport_orig = df_aeroport_orig.rename(columns={'ORIGIN_AIRPORT_ID': 'AIRPORT_ID', 'ORIGIN_AIRPORT_SEQ_ID': 'AIRPORT_SEQ_ID', 'ORIGIN_CITY_MARKET_ID': 'CITY_MARKET_ID', 'ORIGIN': 'ORIGIN', 'ORIGIN_CITY_NAME': 'CITY_NAME', 'ORIGIN_STATE_ABR': 'STATE_ABR', 'ORIGIN_STATE_FIPS': 'STATE_FIPS', 'ORIGIN_STATE_NM': 'STATE_NM', 'ORIGIN_WAC': 'WAC'})
df_aeroport_dest = df_aeroport_dest.rename(columns={'DEST_AIRPORT_ID': 'AIRPORT_ID', 'DEST_AIRPORT_SEQ_ID': 'AIRPORT_SEQ_ID', 'DEST_CITY_MARKET_ID': 'CITY_MARKET_ID', 'DEST': 'ORIGIN', 'DEST_CITY_NAME': 'CITY_NAME', 'DEST_STATE_ABR': 'STATE_ABR', 'DEST_STATE_FIPS': 'STATE_FIPS', 'DEST_STATE_NM': 'STATE_NM', 'DEST_WAC': 'WAC'})

frames = [df_aeroport_orig, df_aeroport_dest]

df_all_aeroport = pd.concat(frames).drop_duplicates()

print(f"Nombre d'aéroport dans df_all_aeroport: {len(df_all_aeroport)}")

print("On sauvegarde les données de aeroport dans la base")
# on sauvegarde les données de vol en base
with engine.connect() as con:
    df_all_aeroport.to_sql(
    name="data_airport", 
    con=con, 
    if_exists="replace"
    )


######################################################################################################################################################
# on va créer une liste de conpagnie aérienne
df_compagnie = df_data[[
    "AIRLINE_ID",
    "UNIQUE_CARRIER",
    "CARRIER"
]]
df_compagnie = df_compagnie.drop_duplicates()
df_compagnie = df_compagnie.reset_index(drop=True)

# on supprime les lignes avec des valeurs incohérentes
indexToDrop = df_compagnie[df_compagnie['AIRLINE_ID'] > 99999].index
df_compagnie = df_compagnie.drop(indexToDrop)

print("On sauvegarde les données de aeroport dans la base")
# on sauvegarde les données de vol en base
with engine.connect() as con:
    df_compagnie.to_sql(
    name="data_airline", 
    con=con, 
    if_exists="replace"
    )