import time
import shutil
from pathlib import Path

def run(conn, geojson_dict, spatial_extent, raw_chunks_dir, time_windows):
    """Erstellt, überwacht und lädt die NDVI Jobs für alle Chunks herunter."""
    raw_chunks_dir.mkdir(parents=True, exist_ok=True)
    
    downloaded_files = []
    jobs = []

    # 1. JOBS ERSTELLEN UND STARTEN
    for start_date, end_date in time_windows:
        chunk_name = f"BaWu_NDVI_{start_date}_to_{end_date}"
        expected_file = raw_chunks_dir / f"{chunk_name}.csv"
        downloaded_files.append(expected_file)

        if expected_file.exists():
            print(f"Chunk {chunk_name} allready present")
            continue

        cube = conn.load_collection(
            "SENTINEL2_L2A",
            spatial_extent=spatial_extent,
            temporal_extent=[start_date, end_date],
            bands=["B04", "B08"] 
        )

        filtered_cube = cube.filter_spatial(geometries=geojson_dict) 
        ndvi_cube = filtered_cube.ndvi(red="B04", nir="B08") 
        zonal_stats = ndvi_cube.aggregate_spatial(geometries=geojson_dict, reducer="mean")  

        job = zonal_stats.save_result(format="CSV").create_job(title=chunk_name)
        
        print(f"Create Job: {chunk_name}") 
        job.start()
        
        jobs.append({"obj": job, "title": chunk_name})

    if not jobs:
        return downloaded_files

    # 2. AUF ABSCHLUSS WARTEN
    while True:
        print("Check Jobs:")
        finished = True
        for item in jobs:
            job = item["obj"]
            if job.status() in ["created", "queued", "running"]: 
                finished = False
                print("Not finished, waiting")
                break
        if finished is True:
            print("Finished")
            break
        time.sleep(300) 

    # 3. HERUNTERLADEN UND UMBENENNEN
    for item in jobs:
        job = item["obj"]
        title = item["title"]
        
        if job.status() != "finished": 
            print(f"Skip failed job: {title}")
            continue

        temp_dir = raw_chunks_dir / f"temp_{job.job_id}"
        temp_dir.mkdir(exist_ok=True)
        job.get_results().download_files(temp_dir)

        csv_files = list(temp_dir.glob("*.csv"))
        
        final_dir = raw_chunks_dir / f"{title}.csv"
        
        if csv_files:
            csv_files[0].rename(final_dir)
            print(f"Chunk saved: {final_dir.name}")

        shutil.rmtree(temp_dir, ignore_errors=True) 
        
    return downloaded_files
