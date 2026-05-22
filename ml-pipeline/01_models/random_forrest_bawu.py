from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from scipy.stats import randint
import pandas as pd
import numpy as np
import joblib
import geopandas as gpd

# bawu_ertrag = pd.read_csv('/Users/sohailludin/Desktop/01 Arbeit/01 Universität /03 Master/02 2. Semester/06 Softwarearchitekturen/Labor/cropprediction/data/clean/winterweizen_geerntet.csv')
bawu_ertrag = pd.read_csv('/Users/sohailludin/Desktop/01 Arbeit/01 Universität /03 Master/02 2. Semester/06 Softwarearchitekturen/Labor/cropprediction/data/yield_pipeline/clean/bawu_winterweizen_geerntet.csv')
nvdi_model = pd.read_csv('/Users/sohailludin/Desktop/01 Arbeit/01 Universität /03 Master/02 2. Semester/06 Softwarearchitekturen/Labor/cropprediction/data/cdse_data/data/03_processed/Crop_Prediction_BaWu_2023_2024.csv')
gdf = gpd.read_file("/Users/sohailludin/Desktop/01 Arbeit/01 Universität /03 Master/02 2. Semester/06 Softwarearchitekturen/Labor/cropprediction/data/geodaten_pipeline/processed/landkreise_bawu_sauber.geojson")
weather_model = pd.read_csv('/Users/sohailludin/Desktop/01 Arbeit/01 Universität /03 Master/02 2. Semester/06 Softwarearchitekturen/Labor/cropprediction/data/cdse_data/data/03_processed/Crop_Prediction_BaWu_2023_2024.csv')


# #Dummy Daten
# np.random.seed(42)
# bawu_ertrag['NDVI'] = np.random.uniform(0.4, 0.8, size=len(bawu_ertrag))
# bawu_ertrag['EVI'] = np.random.uniform(0.5, 0.9, size=len(bawu_ertrag))
# bawu_ertrag['Temp'] = np.random.uniform(12.0, 20.0, size=len(bawu_ertrag))
# bawu_ertrag['Niederschlag'] = np.random.uniform(20.0, 100.0, size=len(bawu_ertrag))




mapping_df = pd.DataFrame({
      'feature_index': gdf.index,
      'Kreis-Id': gdf['ARS']
})


nvdi_model = pd.merge(nvdi_model, mapping_df, on ="feature_index", how="left")

nvdi_model['Jahr'] = pd.to_datetime(nvdi_model['date']).dt.year
weather_model['Jahr'] = pd.to_datetime(weather_model['date']).dt.year

bawu_ertrag['Kreis-Id'] = bawu_ertrag['Kreis-Id'].astype(int)
nvdi_model['Kreis-Id'] = nvdi_model['Kreis-Id'].astype(int)


bawu_ertrag = bawu_ertrag.dropna(subset=['Winterweizen'])

ertragsdaten_model = pd.merge(nvdi_model, bawu_ertrag,  on=['Kreis-Id', 'Jahr'], how = 'inner')

ertragsdaten_model = ertragsdaten_model.rename(columns={'band_unnamed': 'NDVI'})
ertragsdaten_model = ertragsdaten_model.rename(columns={'temperature-mean': 'Temperatur'})
ertragsdaten_model = ertragsdaten_model.rename(columns={'precipitation-flux': 'Niederschlagsrate'})
ertragsdaten_model = ertragsdaten_model.rename(columns={'solar-radiation-flux': 'Bestrahlungsstärke'})




#Feature Engineering
feature_cols = ['NDVI', 'Temperatur', 'Niederschlagsrate','Bestrahlungsstärke' ]
X = ertragsdaten_model[feature_cols] #Input Variablen
y = ertragsdaten_model[['Winterweizen']] #Output Variable, dt/ha , 1 Dezitonne = 100 kg


# #Feature Engineering
# feature_cols = ['NDVI', 'Temp', 'Niederschlag']
# X = bawu_ertrag[feature_cols] #Input Variablen
# y = bawu_ertrag[['Winterweizen']] #Output Variable, dt/ha , 1 Dezitonne = 100 kg

#Definition der Jahre

train_mask = ertragsdaten_model['Jahr'] <= 2023
test_mask = ertragsdaten_model['Jahr'] > 2023


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
joblib.dump(model, '03_pkl-files/rf_ertragsmodell.pkl')

# Test data export
app_data_2024 = ertragsdaten_model[test_mask][['Kreis-Id'] + feature_cols]
map_df = pd.DataFrame({
      'Kreis-Id': bawu_ertrag['Kreis-Id'],
      'Stadt': bawu_ertrag[' Stadt']
    })
app_data_2024 = pd.merge(map_df, app_data_2024, on ="Kreis-Id", how="right")
app_data_2024.to_csv('02_features/features_2024_für_app.csv', index=False)
