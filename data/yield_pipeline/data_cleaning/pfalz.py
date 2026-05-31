import pandas as pd
import numpy as np

pfalz_raw = pd.read_csv('/Users/sohailludin/Desktop/01 Arbeit/01 Universität /03 Master/02 2. Semester/06 Softwarearchitekturen/Labor/cropprediction/data/raw/pfalz_raw.csv', sep = ';')

pfalz_raw.insert(0, 'Jahr', 0)

pfalz_raw['Jahr'] = np.where(pfalz_raw['Winterweizen'].isna(), pfalz_raw['Kreis-Id'], np.nan)

pfalz_raw['Jahr'] = pfalz_raw['Jahr'].ffill()

pfalz_order = pfalz_raw.dropna()

pfalz_winterweizen = pfalz_order.drop(columns=["Roggen und Wintermenggetreide", "Wintergerste", "Sommergerste", "Hafer", "Triticale", "Kartoffeln", "Zuckerrüben", "Winterraps", "Silomais"])

pfalz_yield = "/Users/sohailludin/Desktop/01 Arbeit/01 Universität /03 Master/02 2. Semester/06 Softwarearchitekturen/Labor/cropprediction/data/clean/pfalz_winterweizen_geerntet.csv"

pfalz_winterweizen = pfalz_winterweizen[~pfalz_winterweizen['Winterweizen'].str.contains('/')]

pfalz_winterweizen = pfalz_winterweizen[~pfalz_winterweizen['Winterweizen'].str.contains('.', regex = False)]

pfalz_winterweizen['Winterweizen'] = pfalz_winterweizen['Winterweizen'].astype(str).str.replace(",", ".")

pfalz_winterweizen['Winterweizen'] = pd.to_numeric(pfalz_winterweizen['Winterweizen'], errors = 'coerce')

pfalz_winterweizen.to_csv(pfalz_yield)




