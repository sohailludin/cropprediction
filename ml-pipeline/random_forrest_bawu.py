from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from scipy.stats import randint
import pandas as pd
import numpy as np
import joblib

# bawu_ertrag = pd.read_csv('/Users/sohailludin/Desktop/01 Arbeit/01 Universität /03 Master/02 2. Semester/06 Softwarearchitekturen/Labor/cropprediction/data/clean/winterweizen_geerntet.csv')
bawu_ertrag = pd.read_csv('/Users/sohailludin/Desktop/01 Arbeit/01 Universität /03 Master/02 2. Semester/06 Softwarearchitekturen/Labor/cropprediction/data/yield_pipeline/clean/bawu_winterweizen_geerntet.csv')

#Dummy Daten
np.random.seed(42)
bawu_ertrag['NDVI'] = np.random.uniform(0.4, 0.8, size=len(bawu_ertrag))
bawu_ertrag['EVI'] = np.random.uniform(0.5, 0.9, size=len(bawu_ertrag))
bawu_ertrag['Temp'] = np.random.uniform(12.0, 20.0, size=len(bawu_ertrag))
bawu_ertrag['Niederschlag'] = np.random.uniform(20.0, 100.0, size=len(bawu_ertrag))

bawu_ertrag = bawu_ertrag.dropna(subset=['Winterweizen'])


#Feature Engineering
feature_cols = ['NDVI', 'Temp', 'Niederschlag']
X = bawu_ertrag[feature_cols] #Input Variablen
y = bawu_ertrag[['Winterweizen']] #Output Variable, dt/ha , 1 Dezitonne = 100 kg

#Definition der Jahre

train_mask = bawu_ertrag['Jahr'] <= 2023
test_mask = bawu_ertrag['Jahr'] > 2023


#Train Test Split
X_train, y_train = X[train_mask], y[train_mask]
X_test, y_test = X[test_mask], y[test_mask]

#Modellauswahl

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train.values.ravel())

y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)

print(f"Mittlerer Fehler: {mae:.2f} Dezitonnen/Hektar")

#Modellexport
joblib.dump(model, 'rf_ertragsmodell.pkl')

# Test data export
app_data_2024 = bawu_ertrag[test_mask][['Kreis-Id'] + feature_cols]
app_data_2024.to_csv('features_2024_für_app.csv', index=False)
