# 🌾 CropPrediction: Regionaler Ertragsmonitor

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![Architecture](https://img.shields.io/badge/Architecture-Data--Science--MVP-orange)
![License](https://img.shields.io/badge/license-MIT-green)

Ein Machine-Learning-gestütztes System zur Prognose von Winterweizen-Erträgen auf Landkreisebene in Baden-Württemberg. Das Projekt nutzt Satellitendaten (Sentinel-2 via openEO) und historische Ertragsstatistiken für eine präzise Ernteschätzung.

## 📌 Projektüberblick

Die Vorhersage landwirtschaftlicher Erträge ist entscheidend für die strategische Planung und Ernährungssicherheit. Dieses Projekt kombiniert Erdbeobachtungsdaten mit klassischen ML-Ansätzen, um ein effizientes Vorhersagemodell zu entwickeln, das ohne hohe Rechenlast (Deep Learning) auskommt.

- **Ziel:** Vorhersage des Winterweizen-Ertrags (dt/ha).
- **Region:** Landkreise in Baden-Württemberg.
- **Methodik:** Random Forest Regression auf Basis von NDVI-Zeitreihen und Wetterdaten.

## 🛠 Tech Stack

| Komponente | Technologie |
| :--- | :--- |
| **Sprache** | Python 3.10+ |
| **Backend / API** | [CDSE openEO](https://openeo.cloud/) |
| **Machine Learning** | Scikit-learn (Random Forest Regressor) |
| **Datenverarbeitung** | Pandas, NumPy |
| **Frontend** | Streamlit (in Planung) |

## 🚀 Architektur & Workflow

Das Projekt folgt einem 3-Phasen-Sprint-Plan:

1. **Data Engineering:** Extraktion von monatlichen NDVI-Medianen und ERA5-Wetterdaten via openEO. Bereinigung der Ertragsdaten von Destatis Genesis.
2. **Feature Engineering:** Erstellung flacher Feature-Vektoren pro Landkreis und Jahr [NDVI_Mai, NDVI_Jun, Temp_Mai, ...].
3. **Modellierung & Inferenz:** Training eines Random Forest Regressors mit *Leave-one-year-out* Kreuzvalidierung.

## 📂 Projektstruktur

```text
cropprediction/
├── data/               # Bereinigte CSV-Daten (Ertrag, Landkreise)
│   └── load_data.py    # Läd und bereinigt bkg daten für Landkreise
├── ml-pipeline/        # Skripte für Training und Validierung
│   └── random_forest.py # Kern-Algorithmus (Regression)
├── app/
│   └── app.py 			# interaktives frontend
├── requirements.txt    # Projektabhängigkeiten
└── README.md
