from utils import Bundesland, test_data_export
from ml_pipeline import  tune_hyperparameters, train_and_save_model
from prediction import make_prediction

bawu = Bundesland(name = "bawu")

bawu_df = bawu.load_and_prepare_data()

#Feature Engineering
feature_cols = ['NDVI', 'Temperatur', 'Niederschlagsrate','Bestrahlungsstärke' ]
X = bawu_df[feature_cols] #Input Variablen
y = bawu_df[['Winterweizen']] #Output Variable, dt/ha , 1 Dezitonne = 100 kg

y = y.values.ravel()

rf_parameters = tune_hyperparameters(X,y,'RF')
gb_parameters = tune_hyperparameters(X,y, 'GB')


train_mask = bawu_df['Jahr'] <= 2023
test_mask = bawu_df['Jahr'] > 2023

X_train, y_train = X[train_mask], y[train_mask]
X_test, y_test = X[test_mask], y[test_mask]

random_forrest = train_and_save_model(X_train, y_train, X_test, y_test, 'RF', rf_parameters, '../03_pkl-files/rf_ertragsmodell.pkl')
gradient_boost = train_and_save_model(X_train, y_train, X_test, y_test, 'GB', gb_parameters, '../03_pkl-files/gb_ertragsmodell.pkl')


export = test_data_export(bawu_df, test_mask, feature_cols, name = "bawu")

prediction = make_prediction()

#predictions = check_model_predictions(y_test, X_test)
