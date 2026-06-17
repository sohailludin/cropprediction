import optuna 
import joblib
import sklearn
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, HistGradientBoostingRegressor
from sklearn.model_selection import cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def tune_hyperparameters(X, y, model_type, n_trials = 20):

    def objective(trial):
        if model_type == 'RF':
            params = { 
                'n_estimators': trial.suggest_int("n_estimators", 50, 300, log = True),
                'max_depth': trial.suggest_int("max_depth", 5, 32),
                'min_samples_split': trial.suggest_int('min_samples_split', 2, 10),
                'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 10)
            }
            model = RandomForestRegressor(**params, random_state=42)

        elif model_type == 'GB':
            params = {
            #'n_estimators': trial.suggest_int("n_estimators", 10, 200, log = True),
            "max_depth": trial.suggest_int("max_depth", 2, 32),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.1),
            'max_iter': trial.suggest_int('max_iter', 50, 500)
            }
            model = HistGradientBoostingRegressor(**params, random_state=42)

        score = cross_val_score(model, X, y, cv=3, scoring='neg_mean_absolute_error').mean()
        return score

    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials = n_trials)

    print(f"Beste Parameter für {model_type}: {study.best_params}")
    return study.best_params


def train_and_save_model(X_train, y_train, X_test, y_test, model_type, best_params, export_path):
    #Modellauswahl    
    if model_type == 'RF':
        model = RandomForestRegressor(**best_params, random_state=42)
    elif model_type == 'GB':
        print(f"Starte Training mit {len(X_train)} Zeilen...")
        model = HistGradientBoostingRegressor(**best_params, random_state=42)
    
    #Modelltraining
    model.fit(X_train, y_train)
    print("Training abgeschlossen! Erstelle Vorhersagen...")
    y_pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"--- Metriken für {model_type} ---")
    print(f"Mittlerer Fehler bei {model_type}: {mae:.2f} Dezitonnen/Hektar")
    print(f"Mean Squared Error bei {model_type}: {mse:.4f}")
    print(f"R2 Score bei {model_type}: {r2:.4f}")

    #Modellexport
    joblib.dump(model, export_path)
    print("Modell erfolgreich exportiert unter {export_path}.\n")

    return model




  