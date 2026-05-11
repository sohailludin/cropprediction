import pandas as pd
import numpy as np
import requests
import io
import zipfile

url = "https://www.regionalstatistik.de/genesisWS/rest/2020/data/tabelfile/"

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "username" : "sohail.akram%40web.de",
    "password": "Ganga2212%24%24",}

payload = {
    
    "name": "41241-01-03-4",
    "format" : "csv",
    "regionalkey" : "08",
    "startyear" : 1999,
    "endyear" : 2025,
    "language" : "de",
}



response = requests.post(url, headers=headers, json=payload)

response.text 


