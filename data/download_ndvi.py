"""Calculate and download the needed data in the CDSE Cloud"""
from pathlib import Path
import shutil
import datetime
from datetime import timedelta
import json
import time
import pandas as pd
import openeo
import geopandas as gpd

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

# Time Scope for Data
start_of_data_date = datetime.datetime(2023, 1, 1)
end_of_data_date = datetime.datetime(2024, 12, 31)

# Automaticaly Chunk date scope into 95 day chunks
time_windows=[]
current_chunk_start_date = start_of_data_date
while current_chunk_start_date < end_of_data_date:
    current_chunk_end_date = current_chunk_start_date + timedelta(days=95)
    if current_chunk_end_date > end_of_data_date: # last chunk end is after 
        current_chunk_end_date = end_of_data_date
    time_windows.append([current_chunk_start_date.strftime("%Y-%m-%d"), current_chunk_end_date.strftime("%Y-%m-%d")]) 
    current_chunk_start_date = current_chunk_end_date

downloaded_files = []
jobs = []

# main loop
for start_date, end_date in time_windows:
    chunk_name = f"BaWu_NDVI_{start_date}_to_{end_date}"
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
    
    filtered_cube = cube.filter_spatial(geometries=geojson_dict) # pre filter to reduce compute
    ndvi_cube = filtered_cube.ndvi(red="B04", nir="B08") #pass bands into ndvi
    zonal_stats = ndvi_cube.aggregate_spatial(geometries=geojson_dict, reducer="mean")  # take Landkreise and create mean ndvi for each

    # Create and start the job
    job = zonal_stats.save_result(format="CSV").create_job(title=f"{chunk_name}")
    print("created Job: " + job.describe()["title"])
    job.start()
    jobs.append(job)

# wait for all Jobs to finish or to fail
while True:
    print("check if jobs finished")
    finished = True
    for job in jobs:
        if job.status() in ["created", "queued", "running"]: # Job status is not "failed" or "error" or "finished"
            finished = False
            print("NO")
            break
    if finished is True:
        print("YES")
        break
    time.sleep(300) # wait 5 Minutes

# Download and rename files from chunks
for job in jobs:
    if job.status() != "finished": # if job failed skip download
        continue

    # download chuck data into temp folder
    temp_dir = raw_chunks_dir / f"temp_{job.job_id}"
    temp_dir.mkdir(exist_ok=True)
    job.get_results().download_files(temp_dir)

    # Rename file, CDSE allways returns somthing like "timeseries.csv"
    csv_files = list(temp_dir.glob("*.csv"))
    final_dir = raw_chunks_dir / f'{job.describe()["title"]}.csv'
    if csv_files:
        csv_files[0].rename(final_dir)


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
final_output_path = output_dir / "TEST_NDVI_BaWu_2023_2024_Complete.csv"
master_df.to_csv(final_output_path, index=False)
