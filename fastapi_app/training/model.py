# CNN
from tensorflow import keras
from keras.layers import Input, Dense
from keras.models import Sequential
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import joblib

#lr
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

import os
import sys

#CNN
def init_model_cnn(X_train, y_train, X_test, y_test, preprocessor):

    # On convertie y en categorie
    y_train = keras.utils.to_categorical(y_train)
    y_test = keras.utils.to_categorical(y_test)

    print("Initializing CNN model...")
    # On crée le modèle
    model = Sequential()
    # On ajoute la couche d'entrée
    model.add(Input(shape=(X_train.shape[1],)))
    # On ajoute les couches cachées
    model.add(Dense(128, activation='relu'))
    model.add(Dense(64, activation='relu'))
    model.add(Dense(16, activation='relu'))
    # On ajoute la couche de sortie
    model.add(Dense(2, activation='softmax'))  # Assuming binary classification

    # On compile 
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    # on entraine
    model.fit(X_train, y_train, batch_size = 28, epochs = 3, verbose=1)

    # on evalue à la fin
    scores = model.evaluate(X_test, y_test)
    print("Neural network accuracy: %.2f%%" % (scores[1]*100))

    # On prédit
    print("Making predictions...")
    y_pred = model.predict(X_test)

    # On affiche la matrice de confusion
    print("Confusion Matrix:")
    #on convertie les classes en nombre
    y_pred_nombre = np.argmax(y_pred, axis=1)
    y_test_nombre = np.argmax(y_test, axis=1)

    cf_matrix = confusion_matrix(y_test_nombre, y_pred_nombre)
    disp = ConfusionMatrixDisplay(confusion_matrix=cf_matrix, display_labels=range(2))
    disp.plot(cmap='viridis', xticks_rotation='vertical', values_format=".0f")
    plt.title('Matrice de confusion')
    plt.show()

    # On sauvegarde le modèle
    model.save("model_cnn.keras")
    # On sauvegarde le preprocessor
    joblib.dump(preprocessor, 'modpreprocessor_cnn.pkl')

    print("Model trained and saved successfully.")
    print("Preprocessor saved successfully.")

    # On retourne le score
    return "Model CNN trained successfully with accuracy: %.2f%%" % (scores[1]*100)

def init_model_logistic(X_train, y_train, X_test, y_test, preprocessor):
    print("Initializing Logistic Regression model...")
    # On crée le modèle
    model = LogisticRegression()

    # On entraine le modèle
    model.fit(X_train, y_train)

    # On evalue le modèle
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred.round())
    
    print(f"Logistic Regression accuracy: {accuracy * 100:.2f}%")

    # on fait les tests
    print(classification_report(y_test, y_pred))

    # On sauvegarde le modèle et le preprocessor
    joblib.dump(model, 'model_lr.pkl')
    joblib.dump(preprocessor, 'preprocessor_lr.pkl')

    print("Logistic Regression model trained and saved successfully.")
    
    return f"Model Logistic Regression trained successfully with accuracy: {accuracy * 100:.2f}%"

def init_model_random_forest(df):
    import tensorflow_decision_forests as tfdf

    tf_dataset = tfdf.keras.pd_dataframe_to_tf_dataset(df, label="ARR_DEL15")

    model = tfdf.keras.RandomForestModel()
    model.fit(tf_dataset)

    print(model.summary())
    
    return "Model Random_Forest trained successfully"

def prediction_cnn(data, model_path="model_cnn.keras", preprocessor_path='modpreprocessor_cnn.pkl'):
    # On charge le modèle
    model = keras.models.load_model(model_path)
    # On charge le preprocessor
    preprocessor = joblib.load(preprocessor_path)
    # On prédit
    df = pd.DataFrame(data, index=[0])
    print("Preprocessing data for prediction...")
    df = preprocessor.transform(df)
    # On reshape les données pour une seule entrée
    df = np.array(df).reshape(1, -1)  # Reshape for a single sample
    print("Making prediction...")
    prediction = model.predict(df)
    print(f"Prediction: {prediction}")
    # On retourne la classe prédite
    return np.argmax(prediction, axis=1)[0]  # Return the class index