import openeo
from pathlib import Path

target_dir = Path("openeo_downloads/raw_chunks")
target_dir.mkdir(parents=True, exist_ok=True)

conn = openeo.connect("openeo.dataspace.copernicus.eu").authenticate_oidc()

job_id = "j-2605112353464659864538822b67be3d"
job = conn.job(job_id)

print(f"Downloading results for job {job_id}...")
job.get_results().download_files(target_dir)

