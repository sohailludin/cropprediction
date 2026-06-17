import joblib 
import pandas as pd


def load_rf_model():
    return joblib.load('../03_pkl-files/gb_ertragsmodell.pkl')


def make_prediction():
    model = load_rf_model()
    input_data = pd.read_csv('../02_features/bawu_features_2024_für_app.csv')
    feature_cols = ['NDVI', 'Temperatur', 'Niederschlagsrate', 'Bestrahlungsstärke']
    input_data['Prognose_dt_ha'] = model.predict(input_data[feature_cols])

    input_data.to_csv('../02_features/predictions.csv')

    return input_data


prediction = make_prediction()