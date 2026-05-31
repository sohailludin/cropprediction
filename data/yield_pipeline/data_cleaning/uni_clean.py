import pandas as pd
import numpy as np
import os
from pathlib import Path


BASE_DIR = Path("data")
RAW_DIR = BASE_DIR / "raw"
CLEAN_DIR = BASE_DIR / "clean"

for file in os.walk("RAW_DIR"):
    os.open(file)
    FILE_NAME = os.path.basename(RAW_DIR)
    
file.insert(0, 'Jahr', 0)

file['Jahr'] = np.where(file['Winterweizen'].isna(), file['Kreis-Id'], np.nan)

file['Jahr'] = file['Jahr'].ffill()

file.dropna()

file.drop(columns=["Roggen und Wintermenggetreide", "Wintergerste", "Sommergerste", "Hafer", "Triticale", "Kartoffeln", "Zuckerrüben", "Winterraps", "Silomais"])

file[~file['Winterweizen'].str.contains('/')]

file[~file['Winterweizen'].str.contains('.', regex = False)]

file['Winterweizen'].astype(str).str.replace(",", ".")

file['Winterweizen'] = pd.to_numeric(file['Winterweizen'], errors = 'coerce')

file_winterweizen_yield = ".../data/clean/{FILE_NAME}.csv"

file.to_csv(file_winterweizen_yield)







