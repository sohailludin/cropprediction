from pathlib import Path
import time
import shutil


def run(conn, geojson_dict, spatial_extent, raw_chunks_dir, time_windows):
    raw_chunks_dir.mkdir(parents=True, exist_ok=True)

    downloaded_files = []
    jobs = []

    for start_date, end_date in time_windows:
        chunk_name = f"BaWu_Wetter_{start_date}_to_{end_date}"
        expected_file = raw_chunks_dir / f"{chunk_name}.csv"
        downloaded_files.append(expected_file)

        if expected_file.exists():
            print(f"Skip {chunk_name} allready downloaded")
            continue

        cube = conn.load_collection(
            "AGERA5",
            spatial_extent=spatial_extent,
            temporal_extent=[start_date, end_date],
            bands=["temperature-mean", "precipitation-flux", "solar-radiation-flux"]
        )

        filtered_cube = cube.filter_spatial(geometries=geojson_dict)
        zonal_stats = filtered_cube.aggregate_spatial(geometries=geojson_dict, reducer="mean")

        job = zonal_stats.save_result(format="CSV").create_job(title=f"{chunk_name}")
        print("Create Job: " + job.describe().get("title", chunk_name))
        job.start()
        jobs.append(job)

    if not jobs:
        print("All chunks allready present")
        return downloaded_files

    while True:
        print("Check jobs")
        finished = True
        for job in jobs:
            if job.status() in ["created", "queued", "running"]:
                finished = False
                print("running, wating for cluster")
                break
        if finished is True:
            print("finished")
            break
        time.sleep(60)

    for job in jobs:
        if job.status() != "finished":
            print(f"Skip: {job.job_id}, Failed Job")
            continue

        temp_dir = raw_chunks_dir / f"temp_{job.job_id}"
        temp_dir.mkdir(exist_ok=True)
        job.get_results().download_files(temp_dir)

        csv_files = list(temp_dir.glob("*.csv"))
        job_title = job.describe().get("title", f"Wetter_{job.job_id}")
        final_dir = raw_chunks_dir / f'{job_title}.csv'

        if csv_files:
            csv_files[0].rename(final_dir)
            print(f"Weather-Chunk saved: {final_dir.name}")

        shutil.rmtree(temp_dir, ignore_errors=True)

    return downloaded_files
