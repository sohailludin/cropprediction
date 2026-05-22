import json
import datetime
from datetime import timedelta
import openeo
import geopandas as gpd

def authenticate_cdse():
    print("Login CDSE")
    return openeo.connect("openeo.dataspace.copernicus.eu").authenticate_oidc()

def authenticate_vito():
    print("Login VITO")
    return openeo.connect("https://openeo-cdse.vito.be").authenticate_oidc()

def load_geojson(filepath):
    gdf = gpd.read_file(filepath)
    for col in gdf.select_dtypes(include=['datetime64', 'datetimetz']).columns:
        gdf[col] = gdf[col].astype(str)
    return json.loads(gdf.to_json())

def create_time_chunks(start_date_str, end_date_str, days_per_chunk=95):
    start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")

    time_windows = []
    current_chunk_start = start_date

    while current_chunk_start < end_date:
        current_chunk_end = current_chunk_start + timedelta(days=days_per_chunk)
        if current_chunk_end > end_date:
            current_chunk_end = end_date

        time_windows.append([
            current_chunk_start.strftime("%Y-%m-%d"),
            current_chunk_end.strftime("%Y-%m-%d")
        ])
        current_chunk_start = current_chunk_end

    return time_windows
