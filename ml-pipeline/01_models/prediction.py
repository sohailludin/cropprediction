import joblib 
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def load_gb_model():
    return joblib.load('../03_pkl-files/gb_ertragsmodell.pkl')

def load_rf_model():
    return joblib.load("../03_pkl-files/rf_ertragsmodell.pkl")

def make_prediction_old():
    model = load_gb_model()
    
    input_data = pd.read_csv('../02_features/bawu_features_2024_für_app.csv')
    feature_cols = ['NDVI', 'Temperatur', 'Niederschlagsrate', 'Bestrahlungsstärke']
    input_data['Prognose_dt_ha'] = model.predict(input_data[feature_cols])

    input_data.to_csv('../02_features/predictions.csv')

    return input_data

def check_model_predictions(y_test, X_test):
    gradient_boost = load_gb_model()
    random_forrest = load_rf_model()

    predictions_rf = random_forrest.predict(X_test)
    predictions_gb = gradient_boost.predict(X_test)

    mse_rf = mean_squared_error(y_test, predictions_rf)
    mse_gb = mean_squared_error(y_test, predictions_gb)
    mae_rf = mean_absolute_error(y_test, predictions_rf)
    mae_gb = mean_absolute_error(y_test, predictions_gb)
    r2_rf = r2_score(y_test, predictions_rf)
    r2_gb = r2_score(y_test, predictions_gb)

    print(f"Mittlerer Fehler bei Random Forrest: {mse_rf:.2f} Dezitonnen/Hektar")
    print(f"Mean Absolute Score für Random Forrest: {mae_rf:.4f}")
    print(f"R2 Score für Random Forrest: {r2_rf}")
    
    print(f"Mittlerer Fehler bei Gradient Boost: {mse_gb:.2f} Dezitonnen/Hektar")
    print(f"Mean Absolute Score für Gradient Boost: {mae_gb:.4f}")
    print(f"R2 Score für Random Gradient Boost: {r2_gb}")