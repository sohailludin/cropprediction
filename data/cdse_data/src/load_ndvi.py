from pathlib import Path
import time
import shutil

def run(conn, geojson_dict, spatial_extent, raw_chunks_dir, time_windows):
    raw_chunks_dir.mkdir(parents=True, exist_ok=True)

    downloaded_files = []
    jobs = []

    # 1. JOBS ERSTELLEN UND STARTEN
    for start_date, end_date in time_windows:
        chunk_name = f"BaWu_NDVI_{start_date}_to_{end_date}"
        expected_file = raw_chunks_dir / f"{chunk_name}.csv"
        downloaded_files.append(expected_file)

        if expected_file.exists():
            print(f"Skip {chunk_name} allready present.")
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

        job = zonal_stats.save_result(format="CSV").create_job(title=f"{chunk_name}")
        print("Create job: " + job.describe()["title"])
        job.start()
        jobs.append(job)

    if not jobs:
        print("All chunks allready present")
        return downloaded_files

    while True:
        print("Check Jobs")
        finished = True
        for job in jobs:
            if job.status() in ["created", "queued", "running"]:
                finished = False
                print("Not finished, waiting")
                break
        if finished is True:
            print("Finished")
            break
        time.sleep(300)

    for job in jobs:
        if job.status() != "finished":
            print(f"Skip {job.job_id}, failed")
            continue

        temp_dir = raw_chunks_dir / f"temp_{job.job_id}"
        temp_dir.mkdir(exist_ok=True)
        job.get_results().download_files(temp_dir)

        csv_files = list(temp_dir.glob("*.csv"))
        final_dir = raw_chunks_dir / f'{job.describe()["title"]}.csv'
        if csv_files:
            csv_files[0].rename(final_dir)
            print(f"Chunk saved: {final_dir.name}")

        shutil.rmtree(temp_dir, ignore_errors=True)

    return downloaded_files
