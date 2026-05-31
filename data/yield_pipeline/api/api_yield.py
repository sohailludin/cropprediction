import pandas as pd
import numpy as np
import requests
import io
import zipfile
from pathlib import Path

DATA_PATH = Path("../raw")

url = "https://www.regionalstatistik.de/genesisws/rest/2020/data/tablefile"

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "username" : "***",
    "password": "*****",}

payload = {
    "name": "41241-01-03-4-B",
    "contents":"BAWU_ERNTE",
    "format": "csv",
    "startyear": "2010",
    "endyear": "2025",
    "regionalvariable": "KREISE",
    "regionalkey": "08*",
    "language": "de",
    "job": "true",
}



response = requests.post(url, headers=headers, params=payload)
content_type = response.headers.get("Content-Type", '')


print(response.text)

if response.status_code == 200:
    if("Auftrag wird noch bearbeitet") in response.text:
        print("Auftrag dauert noch ein paar Minuten")
if 'text/csv' in content_type:
    print("Der Server gibt eine CSV Datei zurück")
elif 'application/zip' in content_type:
    print("Der Server gibt eine ZIP Datei zurück")
if response.content.startswith(b'PK'):
    print('ZIP Datein empfangen! Entpacke die CSV-Datei...')
    
    Path = DATA_PATH
    old_name = "alteratei.csv"
    z = zipfile.ZipFile(io.BytesIO(response.content))
    file_info = z.getinfo(response.)
    file_info.filename = "BAWU_ERNTE.csv"
    z.extractall(file_info, Path)
    print(f"Success! Die Datei ist unter {DATA_PATH} gespeichert")



elif response.status_code == 500:
    print(f"HTTP-Server Error {response.status_code}")
else:   
    print(f"Fehler HTTP Status_: {response.status_code}")
    print(response.text)






