import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import pandas as pd
import joblib
import branca.colormap as cm


@st.cache_resource
def load_rf_model():
    return joblib.load('../ml-pipeline/rf_ertragsmodell.pkl')

@st.cache_data
def get_predictions():
    gdf = gpd.read_file("../data/geodaten_pipeline/processed/landkreise_bawu_sauber.geojson")
    
    input_data = pd.read_csv('../ml-pipeline/features_2024_für_app.csv')

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

st.title("Ertragsprognose Baden-Württemberg")

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




@st.cache_resource
def load_rf_model_pfalz():
    return joblib.load('../ml-pipeline/pfalz_ertragsmodell.pkl')

@st.cache_data
def get_predictions_pfalz():
    gdfp = gpd.read_file("../data/geodaten_pipeline/processed/landkreise_pfalz_sauber.geojson")
    
    input_data = pd.read_csv('../ml-pipeline/features_pfalz_2024_für_app.csv')

    for col in gdfp.select_dtypes(include=['datetime64', 'datetimetz']).columns:
        gdfp[col] = gdfp[col].astype(str)
            
    for col in input_data.select_dtypes(include=['datetime64', 'datetimetz']).columns:
        input_data[col] = input_data[col].astype(str)
    
    model = load_rf_model()
    feature_cols = ['NDVI', 'Temp', 'Niederschlag']
    input_data['Prognose_dt_ha'] = model.predict(input_data[feature_cols])
    
    input_data['Kreis-Id'] = input_data['Kreis-Id'].astype(str).str.zfill(5)
    gdfp['ARS'] = gdfp['ARS'].astype(str).str.zfill(5)
    
    gdfp_final = gdfp.merge(input_data[['Kreis-Id', 'Prognose_dt_ha']], left_on='ARS', right_on='Kreis-Id', how='left')
    
    gdfp_final['geometry'] = gdfp_final['geometry'].simplify(tolerance=0.001, preserve_topology=True)
    
    return gdfp_final

st.title("Ertragsprognose Pfalz")

gdfp = get_predictions_pfalz()

# remove blue highlight when clicking
st.markdown("""
    <style>
    path.leaflet-interactive:focus {
        outline: none;
    }
    </style>
    """, unsafe_allow_html=True)

min_yield = gdfp['Prognose_dt_ha'].min()
max_yield = gdfp['Prognose_dt_ha'].max()
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
    gdfp,
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
