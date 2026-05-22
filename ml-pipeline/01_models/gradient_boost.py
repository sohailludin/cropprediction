from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.pipeline import Pipeline
import pandas as pd
import numpy as np
import joblib
import geopandas as gpd


bawu_ertrag = pd.read_csv('/Users/sohailludin/Desktop/01 Arbeit/01 Universität /03 Master/02 2. Semester/06 Softwarearchitekturen/Labor/cropprediction/data/yield_pipeline/clean/bawu_winterweizen_geerntet.csv')
nvdi_model = pd.read_csv("/Users/sohailludin/Desktop/01 Arbeit/01 Universität /03 Master/02 2. Semester/06 Softwarearchitekturen/Labor/cropprediction/data/openeo_downloads/NDVI_BaWu_2023_2024_Complete.csv")
gdf = gpd.read_file("/Users/sohailludin/Desktop/01 Arbeit/01 Universität /03 Master/02 2. Semester/06 Softwarearchitekturen/Labor/cropprediction/data/geodaten_pipeline/processed/landkreise_bawu_sauber.geojson")


mapping_df = pd.DataFrame({
      'feature_index': gdf.index,
      'Kreis-Id': gdf['ARS']
})

nvdi_model = pd.merge(nvdi_model, mapping_df, on ="feature_index", how="left")

nvdi_model['Jahr'] = pd.to_datetime(nvdi_model['date']).dt.year

bawu_ertrag['Kreis-Id'] = bawu_ertrag['Kreis-Id'].astype(int)
nvdi_model['Kreis-Id'] = nvdi_model['Kreis-Id'].astype(int)

bawu_ertrag = bawu_ertrag.dropna(subset=['Winterweizen'])

ertragsdaten_model = pd.merge(nvdi_model, bawu_ertrag, on=['Kreis-Id', 'Jahr'], how = 'inner')

ertragsdaten_model = ertragsdaten_model.rename(columns={'band_unnamed': 'NDVI'})



#Feature Engineering
feature_cols = ['NDVI']
X = ertragsdaten_model[feature_cols] #Input Variablen
y = ertragsdaten_model[['Winterweizen']] #Output Variable, dt/ha , 1 Dezitonne = 100 kg


# #Feature Engineering
# feature_cols = ['NDVI', 'Temp', 'Niederschlag']
# X = bawu_ertrag[feature_cols] #Input Variablen
# y = bawu_ertrag[['Winterweizen']] #Output Variable, dt/ha , 1 Dezitonne = 100 kg

#Definition der Jahre

train_mask = ertragsdaten_model['Jahr'] <= 2023
test_mask = ertragsdaten_model['Jahr'] > 2023


X_train, y_train = X[train_mask], y[train_mask]
X_test, y_test = X[test_mask], y[test_mask]

pipeline = Pipeline([('scaler', MinMaxScaler()), ('regressor', GradientBoostingRegressor())])
pipeline.fit(X_train, y_train)

r2 = pipeline.score(X_test, y_test)
print(f"GBR: {r2}") # GBR: 0.783733539514218