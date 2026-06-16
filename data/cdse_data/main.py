from pathlib import Path
from src import utils, load_ndvi, load_weather, data_fusion

START_DATE = "2016-01-01"
END_DATE = "2025-12-31"

GEOJSON_PATH = "data/01_geodata/landkreise_bawu_sauber.geojson"
SPATIAL_EXTENT = {"west": 7.5, "south": 47.5, "east": 10.5, "north": 49.8}

RAW_DIR_NDVI = Path("data/02_raw_chunks/ndvi")
RAW_DIR_WEATHER = Path("data/02_raw_chunks/weather")
FINAL_OUTPUT_FILE = Path("data/03_processed/Crop_Prediction_BaWu_2016_2025.csv")

if __name__ == "__main__":
    print("Start data aggergation")

    geojson_dict = utils.load_geojson(GEOJSON_PATH)
    ndvi_chunks = utils.create_time_chunks(START_DATE, END_DATE, days_per_chunk=95)
    weather_chunks = utils.create_time_chunks(START_DATE, END_DATE, days_per_chunk=365)

    print("Start NDVI aggregation")
    conn_cdse = utils.authenticate_cdse()
    downloaded_ndvi_files = load_ndvi.run(
        conn=conn_cdse,
        geojson_dict=geojson_dict,
        spatial_extent=SPATIAL_EXTENT,
        raw_chunks_dir=RAW_DIR_NDVI,
        time_windows=ndvi_chunks
    )

    print("Start WEATHER aggergation")
    conn_vito = utils.authenticate_vito()
    downloaded_weather_files = load_weather.run(
        conn=conn_vito,
        geojson_dict=geojson_dict,
        spatial_extent=SPATIAL_EXTENT,
        raw_chunks_dir=RAW_DIR_WEATHER,
        time_windows=weather_chunks
    )

    print("Combine Data")
    data_fusion.merge_pipelines(
        ndvi_files=downloaded_ndvi_files,
        weather_files=downloaded_weather_files,
        final_output_path=FINAL_OUTPUT_FILE
    )
