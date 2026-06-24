import streamlit as st
import pandas as pd
import numpy as np
import joblib
import geopandas as gpd
from numpy.random import default_rng as rng


def load_average():
    ertrag = pd.read_csv(f'../data/yield_pipeline/clean/bawu_winterweizen_geerntet.csv')
    nvdimodel = pd.read_csv('../data/cdse_data/data/03_processed/Crop_Prediction_BaWu_2016_to_2025.csv')
    gdf = gpd.read_file(f"../data/geodaten_pipeline/processed/landkreise_bawu_sauber.geojson")
      
    mapping_df = pd.DataFrame({
        'feature_index': gdf.index,
        'Kreis-Id': gdf['ARS']})
        
    nvdimodel = pd.merge(nvdimodel, mapping_df, on ="feature_index", how="left")

    nvdimodel['Jahr'] = pd.to_datetime(nvdimodel['date']).dt.year

    ertrag['Kreis-Id'] = ertrag['Kreis-Id'].astype(int)
    nvdimodel['Kreis-Id'] = nvdimodel['Kreis-Id'].astype(int)
    ertrag = ertrag.dropna(subset=['Winterweizen'])

    nvdimodel = nvdimodel.groupby(['Kreis-Id', 'Jahr']).agg({
            'band_unnamed': 'mean',           # Durchschnittlicher NDVI
            'temperature-mean': 'mean',       # Durchschnittstemperatur
            'solar-radiation-flux': 'mean',   # Durchschnittliche Sonne
            'precipitation-flux': 'sum'       # Gesamter Niederschlag im Jahr
        }).reset_index()

    ertragsdaten_model = pd.merge(nvdimodel, ertrag,  on=['Kreis-Id', 'Jahr'], how = 'inner')
    ertragsdaten_model = ertragsdaten_model.rename(columns={
        'band_unnamed': 'NDVI',
        'temperature-mean': 'Temperatur',
        'precipitation-flux': 'Niederschlagsrate',
    'solar-radiation-flux': 'Bestrahlungsstärke'})
    
    ertragsdaten_model = ertragsdaten_model.dropna()

    print("Daten wurden erfolgreich geladen und transformiert")

    return ertragsdaten_model

def durchschnitt_feature_wert(feature, data, ID):
    mask = data ['Kreis-Id'] == int(ID) 
    df = data[mask]
    df['Jahr'] = pd.to_datetime(df['Jahr'], format='%Y')
    df_chart = df[['Jahr', feature]]
    line_chart = st.line_chart(df_chart, x= "Jahr", y=feature, color =None, width="content")
    print(f"Line-Chart für {feature} für den Landkreis {ID} wurde erfolgreich erstellt")
    return line_chart
