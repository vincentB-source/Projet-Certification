from fastapi import FastAPI, Form, Depends
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST, Histogram
from loguru import logger
from sqlalchemy.orm import Session
import requests
from pydantic import BaseModel
import json

import time

import psutil
from starlette.requests import Request
from starlette.responses import Response
from typing import Annotated
import numpy as np

from training.model import init_model_cnn, init_model_logistic, init_model_random_forest, prediction_cnn, training_cnn
from training.train import prepare_data_before_departure
from training.trainAfterDeparture import prepare_data_after_departure

import os
import sys

sys.path.insert(0,
                os.path.abspath(
                    os.path.join(
                        os.path.dirname(__file__),
                        ".."
                    )
                ))
from database.db import get_db, Data_Csv
from database.initdbPostgresql import init_db

logger.add("logs/app.log", rotation="1 MB")

app = FastAPI()


REQUEST_COUNT = Counter('http_request_total', 'Total HTTP Requests', ['method', 'status', 'path']) 
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP Request Duration', ['method', 'status', 'path'])
REQUEST_IN_PROGRESS = Gauge('http_requests_in_progress', 'HTTP Requests in progress', ['method', 'path'])
  
# System metrics
  
CPU_USAGE = Gauge('process_cpu_usage', 'Current CPU usage in percent')
MEMORY_USAGE = Gauge('process_memory_usage_bytes', 'Current memory usage in bytes')
REGISTRY = generate_latest()

def update_system_metrics():
    CPU_USAGE.set(psutil.cpu_percent())
    MEMORY_USAGE.set(psutil.Process().memory_info().rss)

@app.middleware("http")
async def monitor_requests(request: Request, call_next):
      method = request.method
      path = request.url.path
        
      REQUEST_IN_PROGRESS.labels(method=method, path=path).inc()
      start_time = time.time()
      response = await call_next(request)
      duration = time.time() - start_time
      status = response.status_code
      REQUEST_COUNT.labels(method=method, status=status, path=path).inc()
      REQUEST_LATENCY.labels(method=method, status=status, path=path).observe(duration) 
      REQUEST_IN_PROGRESS.labels(method=method, path=path).dec()
        
      return response



@app.get("/")
async def root():
    return {"message": "Hello World from FastAPI APP"}

@app.get("/data_a_trouver/{id_data}")
async def get_data_a_trouver_by_id(id_data: int, db: Session = Depends(get_db)) -> dict[str, str]:
    logger.info(f"Route '/data/id_data' (GET) appelée avec l'id {id_data} ")
    print(f"Route '/data/id_data' (GET) appelée avec l'id {id_data} ")
    # On recupère un client en base de données
    data = db.query(Data_Csv).filter_by(index=id_data).first()

    return {"message": f"Data found: {data.YEAR}-{data.MONTH}-{data.DAY_OF_MONTH}  for index {id_data}"}


class Item(BaseModel):
    origin_airport: int
    dest_airport: int
    origin_departure_block: int
    dest_departure_block: int
    dep_delay: int
    elapsed_time: int
    airline_id: int
    crs_dep_time: int
    crs_arr_time: int
    year: int
    month: int
    day_of_month: int
    day_of_week: int

@app.post("/prediction/")
async def creer_prediction(item: Item) -> dict[str, str]:
    logger.info("Route '/prediction/' (POST) appelée.")
    print(f"Route '/prediction/' (POST) appelée avec les données {item}") 
    # On prépare les données
    data = {
        "ORIGIN_AIRPORT_ID": item.origin_airport,
        "DEST_AIRPORT_ID": item.dest_airport,
        "DEP_DELAY": item.dep_delay,
        "CRS_ELAPSED_TIME": item.elapsed_time,
        #"AIRLINE_ID": item.airline_id,
        #"CRS_DEP_TIME": item.crs_dep_time,
        #"CRS_ARR_TIME": item.crs_arr_time,
        #"YEAR": item.year,
        #"MONTH": item.month,
        #"DAY_OF_MONTH": item.day_of_month,
        #"DAY_OF_WEEK": item.day_of_week,
        "DEP_TIME_BLK": item.origin_departure_block,
        "ARR_TIME_BLK": item.dest_departure_block,
    }  
    
    result = prediction_cnn(data=data)
    return {"prediction": f"{result}"}

class SavedItem(BaseModel):
    origin_airport: int
    dest_airport: int
    origin_departure_block: int
    dest_departure_block: int
    dep_delay: int
    elapsed_time: int
    airline_id: int
    crs_dep_time: int
    crs_arr_time: int
    year: int
    month: int
    day_of_month: int
    day_of_week: int
    arr_del15: int

@app.post("/save_real_data/")
async def save_real_data(savedItem: SavedItem) -> dict[str, str]:
    logger.info("Route '/save_real_data/' (POST) appelée.")
    print(f"Route '/save_real_data/' (POST) appelée avec les données {savedItem}") 
    # On prépare les données
    data = {
        "ORIGIN_AIRPORT_ID": savedItem.origin_airport,
        "DEST_AIRPORT_ID": savedItem.dest_airport,
        "DEP_DELAY": savedItem.dep_delay,
        "CRS_ELAPSED_TIME": savedItem.elapsed_time,
        #"AIRLINE_ID": savedItem.airline_id,
        #"CRS_DEP_TIME": savedItem.crs_dep_time,
        #"CRS_ARR_TIME": savedItem.crs_arr_time,
        #"YEAR": savedItem.year,
        #"MONTH": savedItem.month,
        #"DAY_OF_MONTH": savedItem.day_of_month,
        #"DAY_OF_WEEK": savedItem.day_of_week,
        "DEP_TIME_BLK": savedItem.origin_departure_block,
        "ARR_TIME_BLK": savedItem.dest_departure_block,
        "ARR_DEL15": savedItem.arr_del15
    }  
    
    result = training_cnn(data=data)
    return {"training_cnn": f"{result}"}


@app.get("/init-data")
async def insert_data(db: Session = Depends(get_db)) -> dict[str, str]:
    print(f"Route '/init-data' (GET) appelée")
    init_db()
    return {"message": f"init data done"}

@app.get("/init_model_cnn_before_departure")
async def init_model_cnn_before_departure_api():
    print(f"Route '/init_model_cnn_before_departure' (GET) appelée")
    X_train, X_test, y_train, y_test, preprocessor, df =  prepare_data_before_departure()
    train_message = init_model_cnn(X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test, preprocessor=preprocessor)
    return {"message": train_message}

@app.get("/init_model_lr_before_departure")
async def init_model_lr_before_departure_api():
    print(f"Route '/init_model_lr_before_departure' (GET) appelée")
    X_train, X_test, y_train, y_test, preprocessor, df =  prepare_data_before_departure()
    train_message = init_model_logistic(X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test, preprocessor=preprocessor)
    return {"message": train_message}

@app.get("/init_model_rf_before_departure")
async def init_model_rf_before_departure_api():
    print(f"Route '/init_model_rf_before_departure' (GET) appelée")
    X_train, X_test, y_train, y_test, preprocessor, df =  prepare_data_before_departure()
    train_message = init_model_random_forest(df)
    return {"message": train_message}

@app.get("/init_model_cnn_after_departure")
async def init_model_cnn_after_departure_api():
    print(f"Route '/init_model_cnn_after_departure' (GET) appelée")
    X_train, X_test, y_train, y_test, preprocessor, df =  prepare_data_after_departure()
    train_message = init_model_cnn(X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test, preprocessor=preprocessor)
    return {"message": train_message}

@app.get("/init_model_lr_after_departure")
async def init_model_lr_after_departure_api():
    print(f"Route '/init_model_lr_after_departure' (GET) appelée")
    X_train, X_test, y_train, y_test, preprocessor, df =  prepare_data_after_departure()
    train_message = init_model_logistic(X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test, preprocessor=preprocessor)
    return {"message": train_message}

@app.get("/init_model_rf_after_departure")
async def init_model_rf_after_departure_api():
    print(f"Route '/init_model_rf_after_departure' (GET) appelée")
    X_train, X_test, y_train, y_test, preprocessor, df =  prepare_data_after_departure()
    train_message = init_model_random_forest(df)
    return {"message": train_message}

@app.get("/metrics")
async def metrics():
    update_system_metrics()    
    # Return Prometheus metrics
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)