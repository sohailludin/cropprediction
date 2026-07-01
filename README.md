# 🌾 CropPrediction: Regionaler Ertragsmonitor

Ein Machine-Learning-gestütztes System zur Prognose von landwirtschaftlichen Ernteerträgen auf Kreisebene (mit Fokus auf Baden-Württemberg und die Pfalz). Das Projekt kombiniert historische Erntestatistiken mit Wetter- und Satellitendaten (NDVI via openEO) für präzise Ernteschätzungen mithilfe von Ensemble-Lernmethoden.


## 📌 Projektüberblick

Die Vorhersage landwirtschaftlicher Erträge ist entscheidend für die strategische Planung und Ernährungssicherheit. Dieses Projekt kombiniert Erdbeobachtungsdaten, historische Statistiken und Wetterinformationen mit klassischen ML-Ansätzen, um effiziente Vorhersagemodelle zu entwickeln, die ohne hohe Rechenlast (wie Deep Learning) auskommen.

* **Ziel:** Vorhersage landwirtschaftlicher Erträge (dt/ha), insbesondere Winterweizen.
* **Region:** Landkreise in Baden-Württemberg und der Pfalz.
* **Methodik:** Gradient Boosting & Random Forest Regression auf Basis von historischen Ertragsdaten, NDVI-Zeitreihen und Wetterdaten.

## ✨ Features

* **Automatisierte Daten-Pipeline:** Direkter und asynchroner Datenabruf der historischen Ernteerträge über die API der Regionaldatenbank Deutschland (GENESIS).
* **Wetter-Integration:** Abruf und Verarbeitung historischer und aktueller Wetterdaten (z. B. via Open-Meteo oder ERA5).
* **Satellitendaten (NDVI):** Integration von Vegetationsindizes zur Beurteilung der Pflanzengesundheit (Sentinel-2 via openEO).
* **Machine Learning:** Training, Evaluierung und Vorhersage mittels Scikit-Learn (Gradient Boosting & Random Forest).
* **Interaktive App:** Visualisierung der Vorhersagen und Ertragsdaten auf einer interaktiven Karte für verschiedene Bundesländer via Streamlit.

## 🛠 Tech Stack

| Komponente | Technologie |
| --- | --- |
| **Sprache** | Python 3.10+ |
| **Datenbeschaffung** | [GENESIS API](https://www.regionalstatistik.de/), [CDSE openEO](https://openeo.cloud/) |
| **Machine Learning** | Scikit-learn (Random Forest, Gradient Boosting) | Optuna Hyperparameter Tuning 
| **Datenverarbeitung** | Pandas, NumPy |
| **Frontend** | Streamlit |

## 🚀 Architektur & Workflow

Das Projekt ist modular aufgebaut und durchläuft folgende Kernprozesse:

1. **Data Engineering (`data_cleaning/`):** Automatisierter Download historischer Ertragsdaten via GENESIS API, Extraktion von monatlichen NDVI-Medianen (openEO) und Wetterdaten. Bereinigung und Konsolidierung der Datensätze.
2. **Feature Engineering & Modellierung (`ML-Pipeline/`):** Erstellung von Feature-Vektoren pro Landkreis und Jahr. Training und Evaluierung der Regressionsmodelle (Random Forest & Gradient Boosting).
3. **Inferenz & Visualisierung (`app/`):** Nutzung der trainierten Modelle zur Vorhersage in einer interaktiven Streamlit-Web-App, inklusive kartenbasierter Darstellung der Ergebnisse.

## 📂 Projektstruktur

```text
cropprediction/
├── data/               # Bereinigte Daten (Ertrag, Landkreise)
│   └── cdse_data    # CDSE Pipeline
│   └── geodaten_pipeline    # Lädt und bereinigt BKG-Daten für Landkreise
│   └── openeo_downloads    # Dateiordner für fertige OpenEO Dateien in CSV-Format
│   └── yield_pipeline    # Ertragsdaten Abruf via API Schnittstelle zu Regionalstatistik
├── ML-Pipeline/        # Skripte für Training und Validierung
│   └── 01_models # Kern-Algorithmen (Regression, Gradient Boosting)
│   └── 02_features # Feature Export
│   └── 03_pkl-files # PKL Files Export
├── app/
│   └── app.py          # Interaktives Streamlit Frontend
├── requirements.txt    # Projektabhängigkeiten
└── README.md

```

## 🚀 Installation & Setup

**1. Repository klonen**

```bash
git clone https://github.com/sohailludin/cropprediction.git
cd cropprediction

```

**2. Virtuelle Umgebung erstellen und aktivieren (Empfohlen)**

```bash
# MacOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate

```

**3. Abhängigkeiten installieren**

```bash
pip install -r requirements.txt

```

## 🔐 Konfiguration (API Zugangsdaten)

Um die automatisierte Daten-Pipeline (z.B. für GENESIS) zu nutzen, werden API-Zugangsdaten benötigt.


Erstelle im Hauptverzeichnis eine Datei namens `.env` (diese wird von Git durch die `.gitignore` ignoriert) und trage dort deine Zugangsdaten ein:

```env
GENESIS_USER=dein_benutzername
GENESIS_PASSWORD=dein_passwort

```

## ⚙️ Nutzung

**Daten-Pipeline starten (Beispiel GENESIS):**
Um die historischen Ertragsdaten (z. B. Tabelle `41241-01-03-4-B`) als ZIP/CSV abzurufen:

```bash
cd data_cleaning
python api_yield.py

```

**Frontend starten:**
Um die interaktive Karte und die Prognosen anzusehen:

```bash
cd app
streamlit run app.py

```

---
