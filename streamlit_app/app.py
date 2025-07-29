import streamlit as st
import io  
import requests
from loguru import logger
import json


# DOCKER URL
#API_URL = "http://0.0.0.0:8000/"
# URL
API_URL = "http://127.0.0.1:8000/"

logger.add("logs/app.log", rotation="1 MB")

st.title("Veuillez saisir les informations sur le vol")

response = ""

# Fonction pour predire
def analyse_retard(jsonInfo):
    try:
        response = requests.post(f"{API_URL}/prediction/", jsonInfo)
        return response.json()
    # traitement de la réponse
    except requests.exceptions.RequestException as e:
        st.error(f"Erreur de connexion à l'API : {e}")
        logger.error(f"Erreur de connexion à l'API : {e}")
    except Exception as e :
        st.error(f"Une erreur est survenue: {e}")
        logger.error(f"Une erreur est survenue: {e}")

# Fonction pour sauvegarder
def save_real_data(jsonInfo):
    try:
        response = requests.post(f"{API_URL}/save_real_data/", jsonInfo)
        return response.json()
    # traitement de la réponse
    except requests.exceptions.RequestException as e:
        st.error(f"Erreur de connexion à l'API : {e}")
        logger.error(f"Erreur de connexion à l'API : {e}")
    except Exception as e :
        st.error(f"Une erreur est survenue: {e}")
        logger.error(f"Une erreur est survenue: {e}")

with st.form("prediction_form"):
    origin_airport = st.number_input("ID Aeroport de départ.", value=11298, format="%d")
    dest_airport = st.number_input("ID Aeroport d'arrivée.", value=1057, format="%d")
    origin_departure_block = st.number_input("ID Bloc horaire de départ.", value=1, format="%d")
    dest_departure_block = st.number_input("ID Bloc horaire d'arrivée.", value=1, format="%d")
    dep_delay = st.number_input("Nombre de minute de retard au décollage", value=0, format="%d")
    elapsed_time = st.number_input("Nombre de minute de temps de vol", value=120, format="%d")
    airline_id = st.number_input("ID de la compagnie", value=19805, format="%d")
    crs_dep_time = st.number_input("Heure départ", value=1600, format="%d")
    crs_arr_time = st.number_input("Heure arrrivée", value=1600, format="%d")
    year = st.number_input("Année", value=2016, format="%d")
    month = st.number_input("Mois (entre 1 et 12)", value=1, format="%d")
    day_of_month = st.number_input("Jour (entre 1 et 31)", value=12, format="%d")
    day_of_week = st.number_input("Jour de la semaine (entre 1 et 7)", value=2, format="%d")
    
    submitted = st.form_submit_button("Analyser")
    if submitted:
        jsonInfo = {
            "origin_airport": origin_airport,
            "dest_airport": dest_airport,
            "origin_departure_block": origin_departure_block,
            "dest_departure_block": dest_departure_block,
            "dep_delay": dep_delay,
            "elapsed_time": elapsed_time,
            "airline_id": airline_id,
            "crs_dep_time": crs_dep_time,
            "crs_arr_time": crs_arr_time,
            "year": year,
            "month": month,
            "day_of_month": day_of_month,
            "day_of_week": day_of_week
        }
        logger.info(f"Form submitted with data: {jsonInfo}")
        result = analyse_retard(json.dumps(jsonInfo))

        logger.info(f"Prediction result: {result}")

        #gestion de la réponse à ce niveau 
        if result['prediction'] == "0":
            st.write("Pas de retard (ou alors <15 min)")
        elif result['prediction'] == "1":
            st.write("Retard >15 min")
        else:
            st.write(result)

with st.form("save_data_form"):
    real_min_delay = st.number_input("Combien de minutes de retard à l'arrivée", value=16, format="%d")
    save_data = st.form_submit_button("Sauvegarder la data")
    if save_data:
        # on converti les min de retard en plus ou moins 15 minutes de retard
        if real_min_delay > 15:
            arr_del15 = 1
        else:
            arr_del15 = 0

        jsonInfo = {
            "origin_airport": origin_airport,
            "dest_airport": dest_airport,
            "origin_departure_block": origin_departure_block,
            "dest_departure_block": dest_departure_block,
            "dep_delay": dep_delay,
            "elapsed_time": elapsed_time,
            "airline_id": airline_id,
            "crs_dep_time": crs_dep_time,
            "crs_arr_time": crs_arr_time,
            "year": year,
            "month": month,
            "day_of_month": day_of_month,
            "day_of_week": day_of_week,
            "arr_del15": arr_del15
        }
        logger.info(f"Save data submitted with data: {jsonInfo}")
        result_save = save_real_data(json.dumps(jsonInfo))
        st.write(result_save['training_cnn'])

