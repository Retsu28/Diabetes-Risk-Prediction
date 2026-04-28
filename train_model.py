import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
import joblib # Used to save the trained model to a file

# --- STEP 1: CREATE SAMPLE DATA ---
# Since we are using a synthetic sample, we provide some example numbers.
# In a real project, you would load a CSV file here.
def get_sample_data():
    data = {
        'Pregnancies': [1, 8, 1, 1, 0, 5, 3, 10, 2, 8, 1, 0, 1, 5, 7],
        'Glucose': [85, 183, 89, 78, 137, 116, 78, 115, 197, 125, 110, 168, 139, 189, 100],
        'BloodPressure': [66, 64, 66, 50, 40, 74, 50, 0, 70, 96, 92, 74, 80, 60, 0],
        'BMI': [26.6, 23.3, 28.1, 31, 43.1, 25.6, 31, 35.3, 34.3, 0, 37.6, 38, 27.1, 30.1, 30],
        'Age': [31, 32, 21, 26, 33, 30, 26, 29, 53, 54, 30, 41, 22, 59, 32],
        'Outcome': [0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0] # 1 = Diabetes Risk, 0 = Low Risk
    }
    return pd.DataFrame(data)

def train_and_save():
    print("Starting Model Training Pipeline...")

    # 1. Load the data
    df = get_sample_data()

    # 2. Define Features (X) and Target (y)
    # X = the factors we use to guess (Pregnancies, Glucose, etc.)
    # y = the actual answer (Outcome)
    X = df[['Pregnancies', 'Glucose', 'BloodPressure', 'BMI', 'Age']]
    y = df['Outcome']

    # 3. Initialize the Logistic Regression algorithm
    # This is a standard math-based model for binary classification (Yes/No answers)
    model = LogisticRegression(max_iter=1000)

    # 4. Train the model (this is where it "learns" the patterns)
    print("Fitting model to data...")
    model.fit(X, y)

    # 5. Save the trained model to a file called 'model.pkl'
    # The '.pkl' file contains the math weights the model just learned.
    joblib.dump(model, 'model.pkl')
    
    print("-" * 30)
    print("SUCCESS: Model trained and saved as 'model.pkl'")
    print("You can now run 'app.py' and perform predictions!")
    print("-" * 30)

if __name__ == "__main__":
    train_and_save()
