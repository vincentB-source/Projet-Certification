
# Config env 

## env virtuel
python -m venv .venv
source .venv/bin/activate

## install package
pip freeze > requirements.txt
pip install -r requirements.txt

## lancer l'api
cd fastapi_app
uvicorn main:app --host 127.0.0.1 --port 8000 --reload

## lancer streamlit (formulaire de prédiction)
cd streamlit_app
streamlit run app.py

# DOCKER 
## build image 
docker build -t my-python-app . --no-cache
## lancer docker
docker run -p 8000:8000 my-python-app

# DOCKER-COMOPOSE
## lancer docker-compose après avoir config les dockerfile
docker-compose buil
docker-compose up

## accès grafana
http://localhost:3000/login
admin
l!Z4MoutGN9fLE1H

## accès Prometheus
http://localhost:3000/login
admin
l!Z4MoutGN9fLE1H

## accès kuma
http://localhost:3001/login
admin
admin-44