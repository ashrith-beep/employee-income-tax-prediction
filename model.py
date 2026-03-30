# model.py
# This file trains the machine learning model for tax prediction
# We are using RandomForestRegressor from sklearn
# Run this file once before starting the app

import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
import joblib

DATASET_PATH = os.path.join(os.path.dirname(__file__), 'dataset', 'tax_dataset.csv')
MODEL_PATH   = os.path.join(os.path.dirname(__file__), 'tax_model.pkl')


# calculate tax based on Indian tax slabs
def compute_tax(taxable_income):
    if taxable_income <= 250000:
        tax = 0
    elif taxable_income <= 500000:
        tax = (taxable_income - 250000) * 0.05
    elif taxable_income <= 1000000:
        tax = 12500 + (taxable_income - 500000) * 0.20
    else:
        tax = 112500 + (taxable_income - 1000000) * 0.30
    return max(0, round(tax, 2))


# generate fake dataset for training if csv not found
def generate_dataset(n=8000):
    np.random.seed(42)
    annual_salary = np.random.randint(200000, 5000000, n)
    other_income  = np.random.randint(0, 500000, n)
    investments   = np.clip(np.random.randint(0, 200000, n), 0, 150000)
    deductions    = np.random.randint(0, 100000, n)
    age           = np.random.randint(21, 65, n)

    standard_deduction = 50000
    gross_income   = annual_salary + other_income
    taxable_income = np.maximum(0, gross_income - investments - deductions - standard_deduction)
    tax_paid       = np.array([compute_tax(ti) for ti in taxable_income])

    df = pd.DataFrame({
        'annual_salary': annual_salary,
        'other_income':  other_income,
        'investments':   investments,
        'deductions':    deductions,
        'age':           age,
        'tax_paid':      tax_paid,
    })

    os.makedirs(os.path.dirname(DATASET_PATH), exist_ok=True)
    df.to_csv(DATASET_PATH, index=False)
    print("Dataset saved to:", DATASET_PATH)
    return df


def train():
    # load dataset or generate it
    if not os.path.exists(DATASET_PATH):
        print("Dataset not found, generating...")
        df = generate_dataset()
    else:
        df = pd.read_csv(DATASET_PATH)
        print("Dataset loaded,", len(df), "rows")

    # features we use for prediction
    FEATURES = ['annual_salary', 'other_income', 'investments', 'deductions', 'age']
    TARGET   = 'tax_paid'

    X = df[FEATURES]
    y = df[TARGET]

    # split into train and test 80/20
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # train random forest model
    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=15,
        min_samples_leaf=2,
        n_jobs=-1,
        random_state=42
    )
    model.fit(X_train, y_train)

    # check accuracy
    y_pred = model.predict(X_test)
    r2  = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)

    print("R2 Score:", round(r2, 4))
    print("Mean Absolute Error: Rs.", round(mae, 2))

    # save the model
    joblib.dump(model, MODEL_PATH)
    print("Model saved to:", MODEL_PATH)
    return model


if __name__ == '__main__':
    train()
