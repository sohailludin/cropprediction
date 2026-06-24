import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import pandas as pd
import joblib
import branca.colormap as cm
from charts import load_average, durchschnitt_feature_wert



@st.cache_data
def get_predictions():
    gdf = gpd.read_file("../data/cdse_data/data/01_geodata/landkreise_bawu_sauber.geojson")
    
    input_data = pd.read_csv('../ml-pipeline/02_features/predictions.csv')

    for col in gdf.select_dtypes(include=['datetime64', 'datetimetz']).columns:
        gdf[col] = gdf[col].astype(str)
            
    
    input_data['Kreis-Id'] = input_data['Kreis-Id'].astype(str).str.zfill(5)
    gdf['ARS'] = gdf['ARS'].astype(str).str.zfill(5)
    
    gdf_final = gdf.merge(input_data[['Kreis-Id', 'Prognose_dt_ha', 'Stadt']], left_on='ARS', right_on='Kreis-Id', how='left')
    
    gdf_final['Kreis-Id'] = gdf_final['Kreis-Id'].astype(str)

   
    gdf_final = gpd.GeoDataFrame(gdf_final, geometry='geometry')
    
    gdf_final['geometry'] = gdf_final['geometry'].simplify(tolerance=0.01, preserve_topology=True)
    
    print("Daten erfolgreich transformiert")

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


#Ab hier beginnt die Karten Erstellung
print("Karte wird erstellt")

# map creation    
m = folium.Map(location=[48.5, 9.0], zoom_start=8, tiles=None)

folium.TileLayer(
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attr='Esri', name='Satellitenbild'
).add_to(m)


print("Karte wird weiter fertigestellt")
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
        fields=['Kreis-Id', 'Prognose_dt_ha', 'Stadt'],
        aliases=['Name', 'Landkreis ID:', 'Prognose (dt/ha):'],
        labels=True
    )
).add_to(m)

# 4. Legende zur Karte hinzufügen
colormap.add_to(m)


print("Karte wurde fertiggestellt")


st_data = st_folium(
    m, 
    width=800, 
    height=600,
    key='bw_map',
    returned_objects=['last_active_drawing'],
    zoom=8
)

data = load_average()

if st_data is not None and st_data.get('last_active_drawing') is not None:
    label_id = st_data['last_active_drawing']['properties']['Kreis-Id']
    stadt_name = st_data['last_active_drawing']['properties']["Stadt"]

    st.subheader(f"Analyse für {stadt_name}")

    
    plot = durchschnitt_feature_wert("Winterweizen", data, int(label_id))
    ndvi = durchschnitt_feature_wert("NDVI", data, int(label_id))


    
else:
    # Das wird angezeigt, wenn die App frisch lädt und noch kein Klick passiert ist
    st.info("👆 Klicke auf einen Landkreis auf der Karte, um den NDVI-Verlauf zu sehen.")

