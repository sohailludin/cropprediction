import pandas as pd
import numpy as np
import joblib
import geopandas as gpd


class Bundesland:
  def __init__(self, name):
      self.name = name
  def load_and_prepare_data(self):
      
      self.ertrag = pd.read_csv(f'../../data/yield_pipeline/clean/{self.name}_winterweizen_geerntet.csv')
      self.nvdimodel = pd.read_csv('../../data/cdse_data/data/03_processed/Crop_Prediction_BaWu_2016_to_2025.csv')
      self.gdf = gpd.read_file(f"../../data/geodaten_pipeline/processed/landkreise_{self.name}_sauber.geojson")
      
      mapping_df = pd.DataFrame({
        'feature_index': self.gdf.index,
        'Kreis-Id': self.gdf['ARS']})
      
      self.nvdimodel = pd.merge(self.nvdimodel, mapping_df, on ="feature_index", how="left")

      self.nvdimodel['Jahr'] = pd.to_datetime(self.nvdimodel['date']).dt.year

      self.ertrag['Kreis-Id'] = self.ertrag['Kreis-Id'].astype(int)
      self.nvdimodel['Kreis-Id'] = self.nvdimodel['Kreis-Id'].astype(int)
      self.ertrag = self.ertrag.dropna(subset=['Winterweizen'])

      nvdimodel = self.nvdimodel.groupby(['Kreis-Id', 'Jahr']).agg({
              'band_unnamed': 'mean',           # Durchschnittlicher NDVI
              'temperature-mean': 'mean',       # Durchschnittstemperatur
              'solar-radiation-flux': 'mean',   # Durchschnittliche Sonne
              'precipitation-flux': 'mean'       # Gesamter Niederschlag im Jahr
          }).reset_index()

      self.ertragsdaten_model = pd.merge(nvdimodel, self.ertrag,  on=['Kreis-Id', 'Jahr'], how = 'inner')
      self.ertragsdaten_model = self.ertragsdaten_model.rename(columns={
         'band_unnamed': 'NDVI',
         'temperature-mean': 'Temperatur',
          'precipitation-flux': 'Niederschlagsrate',
        'solar-radiation-flux': 'Bestrahlungsstärke'})
      
      self.ertragsdaten_model = self.ertragsdaten_model.dropna()

      return self.ertragsdaten_model
  


def prepare_prediction(dataframe):
      stadt_daten = pd.read_csv(f'../../data/yield_pipeline/clean/bawu_winterweizen_geerntet.csv')
      nvdimodel = pd.read_csv('../../data/cdse_data/data/03_processed/Crop_Prediction_BaWu_2026.csv')
      gdf = gpd.read_file(f"../../data/geodaten_pipeline/processed/landkreise_bawu_sauber.geojson")
      
      mapping_df = pd.DataFrame({
        'feature_index': gdf.index,
        'Kreis-Id': gdf['ARS']})
      
      nvdimodel = pd.merge(nvdimodel, mapping_df, on ="feature_index", how="left")

      nvdimodel['Jahr'] = pd.to_datetime(nvdimodel['date']).dt.year

      nvdimodel['Kreis-Id'] = nvdimodel['Kreis-Id'].astype(int)
   

      nvdimodel = nvdimodel.groupby(['Kreis-Id', 'Jahr']).agg({
              'band_unnamed': 'mean',           # Durchschnittlicher NDVI
              'temperature-mean': 'mean',       # Durchschnittstemperatur
              'solar-radiation-flux': 'mean',   # Durchschnittliche Sonne
              'precipitation-flux': 'mean'       # Gesamter Niederschlag im Jahr
          }).reset_index()

    
      prediction_model = nvdimodel.rename(columns={
         'band_unnamed': 'NDVI',
         'temperature-mean': 'Temperatur',
          'precipitation-flux': 'Niederschlagsrate',
        'solar-radiation-flux': 'Bestrahlungsstärke'})
      
      prediction_model = prediction_model.dropna()

      df = pd.DataFrame({
        'Kreis-Id' : stadt_daten['Kreis-Id'],
        'Stadt' : stadt_daten[' Stadt']})
      
      prediction_model = pd.merge(prediction_model, df, on='Kreis-Id', how="right")

      return prediction_model

    
  

def test_data_export(dataframe, test_mask, feature_cols, name):
     stadt_daten = pd.read_csv(f'../../data/yield_pipeline/clean/{name}_winterweizen_geerntet.csv')
     data = dataframe[test_mask] [['Kreis-Id'] + feature_cols] 
     df = pd.DataFrame({
        'Kreis-Id' : stadt_daten['Kreis-Id'],
        'Stadt' : stadt_daten[' Stadt']})
     data = pd.merge(data, df, on='Kreis-Id', how="right")
     data.to_csv(f'../02_features/{name}_features_2025_für_app.csv', index=False)

     return data

