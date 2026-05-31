import requests
import zipfile
import io

url = "https://www.regionalstatistik.de/genesisws/rest/2020/data/result"


payload = {
    "username": "*****",
    "password": "******",
    "name": "41241-01-03-4-B_1780219847183_de.csv"}

print("Lade Dateien runter")
response = requests.post(url, params=payload)



if response.status_code == 200:
    if("Auftrag wird noch bearbeitet") in response.text:
        print("Auftrag dauert noch ein paar Minuten")
    if response.content.startswith(b'PK'):
         print('ZIP Datein empfangen! Entpacke die CSV-Datei...')
         z = zipfile.ZipFile(io.BytesIO(response.content))
         z.extractall(".")

         print(f"Success! Die Datei ist unter {z.namelist[0]} gespeichert")
    
    else:
        with open("erntedaten_final.csv","w", encoding="utf-8") as file:
                file.write(response.text)
        print("Daten unter erntedaten_final.csv gespeichert")

elif response.status_code == 500:
    print(f"HTTP-Server Error {response.status_code}")
else:   
    print(f"Fehler HTTP Status_: {response.status_code}")
    print(response.text)