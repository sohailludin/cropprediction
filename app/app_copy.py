import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import pandas as pd
import joblib
import branca.colormap as cm
import os
from pathlib import Path
import pickle


ML_DIR = Path("../ml-pipeline")
GEO_DIR = Path("../data/geodaten_pipeline/processed")
OUTPUT_PICKEL = Path("../ml-pipeline/ende.pkl")


@st.cache_resource
def load_rf_model():
    combined_df = pd.DataFrame()
    for root, dirs, files in os.walk(ML_DIR):
        print(f"Suche im Ordner: {root}, Finde Dateien: {files}")
        for file in files:
                if file.endswith(".pkl"):
                    print(f"Dateienname lautet: {file}")
                    ml_path = os.path.join(root, file)
                    print(f"Pfad lautet: {ml_path}")
                    with open(ml_path, 'rb') as f:
                        ml_inhalt = pickle.load(f)
                        if isinstance(ml_inhalt, pd.DataFrame):
                            combined_df = pd.concat([combined_df, ml_inhalt], ignore_index = True)
                            pickle.dump(combined_df, protocol=pickle.HIGHEST_PROTOCOL)
                   
    return joblib.load(OUTPUT_PICKEL)
                 
                    
            

@st.cache_data
def get_predictions():
    geo = []
    for root, dirs, files in os.walk(GEO_DIR):
            print(f"Suche im Ordner: {root}, Finde Dateien: {files}")
            for file in files:
                    if file.endswith(".geojson"):
                        geo_path = os.path.join(root, file)
                        geo_inhalt = gpd.read_file(geo_path)
                        geo.append(geo_inhalt)
    gdf = pd.concat(geo)                           
                            
                   
    data = []                         
    for root, dirs, files in os.walk(ML_DIR):
            for file in files:
                    if file.endswith(".csv"):
                        data_path = os.path.join(root, file)
                        data_inhalt = pd.read_csv(data_path)
                        data.append(data_inhalt)
    input_data = pd.concat(data)
                    

    for col in gdf.select_dtypes(include=['datetime64', 'datetimetz']).columns:
       gdf[col] = gdf[col].astype(str)
            
    for col in input_data.select_dtypes(include=['datetime64', 'datetimetz']).columns:
        input_data[col] = input_data[col].astype(str)
    
    model = load_rf_model()
    feature_cols = ['NDVI', 'Temp', 'Niederschlag']
    input_data['Prognose_dt_ha'] = model.predict(input_data[feature_cols])
    
    input_data['Kreis-Id'] = input_data['Kreis-Id'].astype(str).str.zfill(5)
    gdf['ARS'] = gdf['ARS'].astype(str).str.zfill(5)
    
    gdf_final = gdf.merge(input_data[['Kreis-Id', 'Prognose_dt_ha']], left_on='ARS', right_on='Kreis-Id', how='left')
    
    gdf_final['geometry'] = gdf_final['geometry'].simplify(tolerance=0.001, preserve_topology=True)
    
    return gdf_final

st.title("Ertragsprognosen Baden-Württemberg und Rheinland-Pfalz")

gdf = get_predictions()

# remove blue highlight when clicking
st.markdown("""
    <style>
    path.leaflet-interactive:focus {
        outline: none;
    }
    </style>
    """, unsafe_allow_html=True)

min_yield = gdf['Prognose_dt_ha'].min()
max_yield = gdf['Prognose_dt_ha'].max()
if pd.isna(min_yield): min_yield, max_yield = 0, 100
colormap = cm.linear.YlGn_09.scale(min_yield, max_yield)
colormap.caption = 'Prognostizierter Ertrag (dt/ha)'

# map creation    
m = folium.Map(location=[48.5, 9.0], zoom_start=8, tiles=None)

folium.TileLayer(
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attr='Esri', name='Satellitenbild'
).add_to(m)

# 3. Das Choropleth-Objekt mit Highlight-Effekt
# Wir nutzen hier eine GeoJson-Ebene direkt, da sie feiner steuerbar ist als das Standard-Choropleth
folium.GeoJson(
    gdf,
    style_function=lambda x: {
        # Hier ist der Trick: 
        # Wir prüfen, ob der Wert existiert. Wenn ja -> Colormap, wenn nein -> Grau.
        'fillColor': colormap(x['properties']['Prognose_dt_ha']) 
                     if pd.notna(x['properties']['Prognose_dt_ha']) 
                     else '#4a4a4a', # Das Grau für "No Data"
        'color': 'black',
        'weight': 0.5,
        'fillOpacity': 0.6
    },
    highlight_function=lambda x: {
        'weight': 3,
        'color': '#333333', 
        'fillOpacity': 0.8
    },
    popup=folium.GeoJsonPopup(
        fields=['Kreis-Id', 'Prognose_dt_ha'],
        aliases=['Landkreis ID:', 'Prognose (dt/ha):'],
        labels=True
    )
).add_to(m)

# 4. Legende zur Karte hinzufügen
colormap.add_to(m)

st_data = st_folium(
    m, 
    width=800, 
    height=600,
    key='bw_map',
    returned_objects=[],
    zoom=8
)


