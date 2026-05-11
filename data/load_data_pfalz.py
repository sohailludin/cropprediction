import os
import requests
import zipfile
import geopandas as gpd
from pathlib import Path

URL = "https://daten.gdz.bkg.bund.de/produkte/vg/vg250_ebenen_0101/aktuell/vg250_01-01.utm32s.shape.ebenen.zip"

BASE_DIR = Path("geodaten_pipeline")
RAW_DIR = BASE_DIR / "raw"
PROCESSED_DIR = BASE_DIR / "processed"
ZIP_PATH = RAW_DIR / "bkg_daten.zip"
GEOJSON_OUT = PROCESSED_DIR / "landkreise_pfalz_sauber.geojson"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

response = requests.get(URL, stream=True)
response.raise_for_status()

with open(ZIP_PATH, "wb") as file:
    for chunk in response.iter_content(chunk_size=8192):
        file.write(chunk)

with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
    zip_ref.extractall(RAW_DIR)

shp_path = None
for root, dirs, files in os.walk(RAW_DIR):
    for file in files:
        if file.upper().endswith("KRS.SHP"):
            shp_path = os.path.join(root, file)
            break
    if shp_path:
        break

if not shp_path:
    raise FileNotFoundError("Konnte die Kreis-Shapefile (KRS.shp) nicht finden!")

gdf = gpd.read_file(shp_path)

if 'SN_L' in gdf.columns:
    gdf_pfalz = gdf[gdf['SN_L'] == '07'].copy()
else:
    gdf_pfalz = gdf[gdf['ARS'].str.startswith('07')].copy()

gdf_pfalz = gdf_pfalz.to_crs(epsg=4326)

gdf_pfalz.geometry = gdf_pfalz.geometry.simplify(0.001)

if GEOJSON_OUT.exists():
    GEOJSON_OUT.unlink() 
    
gdf_pfalz.to_file(GEOJSON_OUT, driver="GeoJSON")

