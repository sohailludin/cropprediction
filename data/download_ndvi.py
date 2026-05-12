import openeo
import geopandas as gpd
from pathlib import Path
import json
import pandas as pd
import shutil

output_dir = Path("openeo_downloads")
output_dir.mkdir(exist_ok=True)

raw_chunks_dir = output_dir / "raw_chunks"
raw_chunks_dir.mkdir(exist_ok=True)

conn = openeo.connect("openeo.dataspace.copernicus.eu").authenticate_oidc() #auth

# geojason -> json
gdf = gpd.read_file("geodaten_pipeline/processed/landkreise_bawu_sauber.geojson")
for col in gdf.select_dtypes(include=['datetime64', 'datetimetz']).columns: # remove timeseries format
    gdf[col] = gdf[col].astype(str)
geojson_dict = json.loads(gdf.to_json()) 

# create chunks for 2023 and 2024 in 3 Months
time_windows = [
    ["2023-01-01", "2023-03-31"],
    ["2023-04-01", "2023-06-30"],
    ["2023-07-01", "2023-09-30"],
    ["2023-10-01", "2023-12-31"],
    ["2024-01-01", "2024-03-31"],
    ["2024-04-01", "2024-06-30"],
    ["2024-07-01", "2024-09-30"],
    ["2024-10-01", "2024-12-31"]
]

downloaded_files = []

# main loop
for start_date, end_date in time_windows:
    chunk_name = f"NDVI_{start_date}_to_{end_date}"
    expected_file = raw_chunks_dir / f"{chunk_name}.csv"
    downloaded_files.append(expected_file)
    
    # Skip if script is restarted and chunk allready exists
    if expected_file.exists():
        continue
        
    # create request graph
    cube = conn.load_collection(
        "SENTINEL2_L2A",
        spatial_extent={"west": 7.5, "south": 47.5, "east": 10.5, "north": 49.8}, # Bounding Box BaWu
        temporal_extent=[start_date, end_date],
        bands=["B04", "B08"] #Bands of Satelite needed for NDVI, B04=red, B08=near infra red, reduces IO/Data
    )

    ndvi_cube = cube.ndvi(red="B04", nir="B08") #pass bands into ndvi
    zonal_stats = ndvi_cube.aggregate_spatial(geometries=geojson_dict, reducer="mean")  # take Landkreise and create mean ndvi for each

    # Create and start the job
    job = zonal_stats.save_result(format="CSV").create_job(title=f"BaWu_{chunk_name}")
    job.start_and_wait() # wait for chunk to finish
    #TODO CREATE ALL JOBS HERE

    # Download file
    temp_dir = raw_chunks_dir / f"temp_{job.job_id}"
    temp_dir.mkdir(exist_ok=True)
    job.get_results().download_files(temp_dir)
    
    # Rename file, CDSE allways returns somthing like "timeseries.csv"
    csv_files = list(temp_dir.glob("*.csv"))
    if csv_files:
        csv_files[0].rename(expected_file)
    
    shutil.rmtree(temp_dir, ignore_errors=True) # cleanup

# When all Chunks exist, put them together
dataframes = []
for file_path in downloaded_files:
    if file_path.exists():
        df = pd.read_csv(file_path)
        dataframes.append(df)

# Combine all DataFrames into one
master_df = pd.concat(dataframes, ignore_index=True)

# Save the final Master CSV
final_output_path = output_dir / "NDVI_BaWu_2023_2024_Complete.csv"
master_df.to_csv(final_output_path, index=False)
    
