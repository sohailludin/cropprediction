import pandas as pd
import numpy as np
import requests
import io
import zipfile

url = "https://www.regionalstatistik.de/genesisws/rest/2020/data/tablefile"

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "username" : "******",
    "password": "******",}

payload = {
    "name": "41241-01-03-4-B",
    "format": "csv",
    "startyear": "2005",
    "endyear": "2025",
    "regionalvariable": "KREISE",
    "regionalkey": "08*",
    "language": "de",
    "job": "true",
}



response = requests.post(url, headers=headers, params=payload)


print(response.text)
print(response.content)
if response.status_code == 200:
    if("Auftrag wird noch bearbeitet") in response.text:
        print("Auftrag dauert noch ein paar Minuten")
    # if response.content.startswith(b'PK'):
    #      print('ZIP Datein empfangen! Entpacke die CSV-Datei...')
    #      z = zipfile.ZipFile(io.BytesIO(response.content))
    #      z.extractall(".")
    #      print(f"Success! Die Datei ist unter {z.namelist[0]} gespeichert")
    if response.content.startswith("41241"):
        print("Fertige csv-Datei empfangen")
        open('erntedaten.csv', 'w').write(response.text)
        print(f"Csv-Datei unter erntedaten.csvc gespeichert")


elif response.status_code == 500:
    print(f"HTTP-Server Error {response.status_code}")
else:   
    print(f"Fehler HTTP Status_: {response.status_code}")
    print(response.text)






