from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from scipy.stats import randint
import pandas as pd
import numpy as np
import joblib
import os
import geopandas as gpd



ERTRAG_DIR = ("../data/yield_pipeline/clean")
NVDI_DIR = ("../data/openeo_downloads")


ertragsdaten = pd.DataFrame()
nvdi = pd.DataFrame()

ertrag = []

for root, dirs, files in os.walk(ERTRAG_DIR):
        for file in files:
            if file.endswith(".csv"):
                print(f"Dateiname lautet: {file}")
                df_path = os.path.join(root,file)
                ertrag.append(pd.read_csv(df_path))
                
ertragsdaten = pd.concat([ertrag], ignore_index=True)
                               

nvdi = []

for root, dirs, files in os.walk(NVDI_DIR):
        for file in files:
            if file.endswith(".csv"):   
                  nvdi_path = os.path.join(root,file)
                  nvdi.append(pd.read_csv(nvdi_path))
                  
nvdi_model = pd.concat([nvdi], ignore_index=True)



gdf = gpd.read_file("/Users/sohailludin/Desktop/01 Arbeit/01 Universität /03 Master/02 2. Semester/06 Softwarearchitekturen/Labor/cropprediction/data/geodaten_pipeline/processed/landkreise_bawu_sauber.geojson")

mapping_df = pd.DataFrame({
      'feature_index': gdf.index,
      'Kreis-Id': gdf['AGS']
})

nvdi_model = pd.merge(nvdi_model, mapping_df, on ="feature_index", how="left")


nvdi_model['Jahr'] = pd.to_datetime(nvdi_model['date']).dt.year

#Dummy Daten
#np.random.seed(42)
#pfalz_ertrag['NDVI'] = np.random.uniform(0.4, 0.8, size=len(pfalz_ertrag))
#pfalz_ertrag['EVI'] = np.random.uniform(0.5, 0.9, size=len(pfalz_ertrag))
#pfalz_ertrag['Temp'] = np.random.uniform(12.0, 20.0, size=len(pfalz_ertrag))
#pfalz_ertrag['Niederschlag'] = np.random.uniform(20.0, 100.0, size=len(pfalz_ertrag))


ertragsdaten = ertragsdaten.dropna(subset=['Winterweizen'])

ertragsdaten_model = pd.merge(nvdi, ertragsdaten, on=['Kreis-ID', 'Jahr'], how = 'inner')


#Feature Engineering
feature_cols = ['feature_index', 'band_unnamed']
X = ertragsdaten_model[feature_cols] #Input Variablen
y = ertragsdaten_model[['Winterweizen']] #Output Variable, dt/ha , 1 Dezitonne = 100 kg

#Definition der Jahre

train_mask = ertragsdaten['Jahr'] == 2023
test_mask = ertragsdaten['Jahr'] > 2023


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
joblib.dump(model, 'ertragsmodell.pkl')

# Test data export
app_data_pfalz_2024 = ertragsdaten[test_mask][['Kreis-Id'] + feature_cols]
app_data_pfalz_2024.to_csv('features_2024_für_app.csv', index=False)
