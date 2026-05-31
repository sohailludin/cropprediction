import pandas as pd
import numpy as np
import requests

url = "https://www.regionalstatistik.de/genesis/online"

response = requests.get(url)

response_json = response.json()
print(response_json)



bawu_raw = pd.read_csv('/Users/sohailludin/Desktop/01 Arbeit/01 Universität /03 Master/02 2. Semester/06 Softwarearchitekturen/Labor/cropprediction/data/raw/bawu_raw.csv', sep = ';')

bawu_raw.insert(0, 'Jahr', 0)

bawu_raw['Jahr'] = np.where(bawu_raw['Winterweizen'].isna(), bawu_raw['Kreis-Id'], np.nan)

bawu_raw['Jahr'] = bawu_raw['Jahr'].ffill()

bawu_order = bawu_raw.dropna()

bawu_winterweizen = bawu_order.drop(columns=["Roggen und Wintermenggetreide", "Wintergerste", "Sommergerste", "Hafer", "Triticale", "Kartoffeln", "Zuckerrüben", "Winterraps", "Silomais"])

file_winterweizen_yield = "/Users/sohailludin/Desktop/01 Arbeit/01 Universität /03 Master/02 2. Semester/06 Softwarearchitekturen/Labor/cropprediction/data/clean/bawu_winterweizen_geerntet.csv"

bawu_winterweizen_slash = bawu_winterweizen[~bawu_winterweizen['Winterweizen'].str.contains('/')]

bawu_winterweizen_nodash = bawu_winterweizen_slash[~bawu_winterweizen_slash['Winterweizen'].str.contains('.', regex = False)]

bawu_winterweizen_nodash['Winterweizen'] = bawu_winterweizen_nodash['Winterweizen'].astype(str).str.replace(",", ".")

bawu_winterweizen_nodash['Winterweizen'] = pd.to_numeric(bawu_winterweizen_nodash['Winterweizen'], errors = 'coerce')

bawu_winterweizen_nodash.to_csv(file_winterweizen_yield)



