import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import joblib  # Used to save the trained model and scaler to files

# --- CONFIGURATION ---
DATASET_PATH = 'diabetes.csv'  # Pima Indians Diabetes Dataset (768 samples)
MODEL_PATH = 'model.pkl'
SCALER_PATH = 'scaler.pkl'

# The 8 features from the Pima Indians Diabetes Dataset
FEATURE_COLUMNS = [
    'Pregnancies',
    'Glucose',
    'BloodPressure',
    'SkinThickness',
    'Insulin',
    'BMI',
    'DiabetesPedigreeFunction',
    'Age'
]
TARGET_COLUMN = 'Outcome'

def train_and_save():
    print("=" * 50)
    print("Diabetes Risk Prediction - Model Training Pipeline")
    print("Using: Pima Indians Diabetes Dataset (768 samples)")
    print("=" * 50)

    # --- STEP 1: LOAD THE REAL DATASET ---
    print("\n[1/5] Loading dataset from:", DATASET_PATH)
    df = pd.read_csv(DATASET_PATH)
    print(f"  -> Dataset shape: {df.shape[0]} rows x {df.shape[1]} columns")
    print(f"  -> Outcome distribution:\n{df[TARGET_COLUMN].value_counts().to_string()}")

    # --- STEP 2: SPLIT FEATURES AND TARGET ---
    print("\n[2/5] Preparing features and target...")
    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    # --- STEP 3: TRAIN/TEST SPLIT ---
    print("\n[3/5] Splitting into train/test sets (80/20)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"  -> Training samples: {len(X_train)}")
    print(f"  -> Testing samples:  {len(X_test)}")

    # --- STEP 4: SCALE FEATURES ---
    print("\n[4/5] Scaling features with StandardScaler...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # --- STEP 5: TRAIN AND EVALUATE ---
    print("\n[5/5] Training Logistic Regression model...")
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train_scaled, y_train)

    # Evaluate on test set
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)

    print("\n" + "=" * 50)
    print(f"  Model Accuracy: {accuracy:.2%}")
    print("=" * 50)
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Low Risk (0)', 'High Risk (1)']))

    # --- SAVE MODEL AND SCALER ---
    joblib.dump(model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)

    print("-" * 50)
    print(f"SUCCESS: Model saved as '{MODEL_PATH}'")
    print(f"SUCCESS: Scaler saved as '{SCALER_PATH}'")
    print("You can now run 'app.py' and perform predictions!")
    print("-" * 50)

if __name__ == "__main__":
    train_and_save()
