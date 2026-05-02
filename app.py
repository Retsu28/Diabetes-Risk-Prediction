from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import mysql.connector # Library to connect Python to MySQL
import joblib          # Library to load the saved 'model.pkl' and 'scaler.pkl'
import numpy as np     # Library for handling numerical data (arrays)

# Initialize the Flask application
app = Flask(__name__)

# A secret key is required for Flask 'flash' messages (pop-ups)
app.secret_key = 'your_super_secret_key'

# --- DATABASE CONFIGURATION ---
# IMPORTANT: Update these values to match your local MySQL settings
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '', # Often empty by default in XAMPP/WAMP
    'database': 'diabetes_db'
}

def get_db_connection():
    """
    Helper function to establish a connection to MySQL.
    We call this every time we need to talk to the database.
    """
    return mysql.connector.connect(**db_config)

# --- ERROR HANDLERS ---

@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 page that keeps the sidebar/topbar layout intact."""
    return render_template('404.html'), 404

# --- ROUTES ---

@app.route('/')
def dashboard():
    """
    DASHBOARD ROUTE (The Home Page)
    - Fetches total counts of patients and predictions.
    - Fetches the 5 most recent predictions to show on the table.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True) # dictionary=True makes results easier to use

        # 1. Get total number of patients
        cursor.execute("SELECT COUNT(*) AS total FROM patients")
        total_patients = cursor.fetchone()['total']

        # 2. Get total number of predictions made
        cursor.execute("SELECT COUNT(*) AS total FROM predictions")
        total_predictions = cursor.fetchone()['total']

        # 2b. Get counts for High Risk and Low Risk (for dashboard pie chart)
        cursor.execute("SELECT COUNT(*) AS total FROM predictions WHERE result = 'High Risk'")
        high_risk_count = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) AS total FROM predictions WHERE result = 'Low Risk'")
        low_risk_count = cursor.fetchone()['total']

        # 3. Get recent predictions with matching patient names using a JOIN
        query = """
            SELECT p.result, p.created_at, p.patient_id, pt.name as patient_name 
            FROM predictions p 
            JOIN patients pt ON p.patient_id = pt.id 
            ORDER BY p.created_at DESC 
            LIMIT 5
        """
        cursor.execute(query)
        recent = cursor.fetchall()

        # Calculate high risk rate percentage
        high_risk_rate = round((high_risk_count / total_predictions * 100), 1) if total_predictions > 0 else 0

        cursor.close()
        conn.close()

        # Send this data to the 'dashboard.html' template
        return render_template('dashboard.html', 
                               total_patients=total_patients, 
                               total_predictions=total_predictions, 
                               high_risk_count=high_risk_count,
                               low_risk_count=low_risk_count,
                               high_risk_rate=high_risk_rate,
                               recent=recent)
    except Exception as e:
        return f"Database Error: {str(e)}. Make sure your MySQL server is running and the database exists."

@app.route('/patients')
def list_patients():
    """
    LIST PATIENTS ROUTE
    - Fetches all records from the patients table and displays them.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM patients ORDER BY name ASC")
    patients = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('patients.html', patients=patients)

@app.route('/patients/add', methods=['GET', 'POST'])
def add_patient():
    """
    ADD PATIENT ROUTE
    - GET: Shows the blank form.
    - POST: Takes user input and saves it to the MySQL 'patients' table.
    """
    if request.method == 'POST':
        # Collect data from the form fields
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        contact = request.form['contact']

        conn = get_db_connection()
        cursor = conn.cursor()
        query = "INSERT INTO patients (name, age, gender, contact) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (name, age, gender, contact))
        conn.commit() # Save the changespermanently
        cursor.close()
        conn.close()
        
        flash("New patient successfully registered!")
        return redirect(url_for('list_patients'))

    return render_template('add_patient.html')

@app.route('/patients/edit/<int:id>', methods=['GET', 'POST'])
def edit_patient(id):
    """
    EDIT PATIENT ROUTE
    - GET: Fetches current data for one patient and pre-fills the form.
    - POST: Updates that specific patient's record.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        contact = request.form['contact']

        query = "UPDATE patients SET name=%s, age=%s, gender=%s, contact=%s WHERE id=%s"
        cursor.execute(query, (name, age, gender, contact, id))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Patient records updated!")
        return redirect(url_for('list_patients'))

    # Load current data for the form
    cursor.execute("SELECT * FROM patients WHERE id = %s", (id,))
    patient = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('edit_patient.html', patient=patient)

@app.route('/patients/delete/<int:id>')
def delete_patient(id):
    """
    DELETE PATIENT ROUTE
    - Removes a patient based on their unique ID.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM patients WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Patient has been removed.")
    return redirect(url_for('list_patients'))

@app.route('/patients/<int:id>/history')
def patient_history(id):
    """
    PATIENT HISTORY ROUTE
    - Displays a vertical timeline of all past assessments for a specific patient.
    - Provides biomarker trend data for Chart.js line charts.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch patient details
    cursor.execute("SELECT * FROM patients WHERE id = %s", (id,))
    patient = cursor.fetchone()

    if not patient:
        cursor.close()
        conn.close()
        flash("Patient not found.")
        return redirect(url_for('list_patients'))

    # Fetch ALL predictions for this patient, ordered newest first (for timeline)
    cursor.execute("""
        SELECT * FROM predictions 
        WHERE patient_id = %s 
        ORDER BY created_at DESC
    """, (id,))
    predictions = cursor.fetchall()

    # Prepare chronological data for trend charts (oldest first)
    predictions_chrono = list(reversed(predictions))

    cursor.close()
    conn.close()

    return render_template('patient_history.html',
                           patient=patient,
                           predictions=predictions,
                           predictions_chrono=predictions_chrono)

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    """
    PREDICTION ROUTE
    - GET: Shows form with a dropdown list of patients.
    - POST: 
      1. Loads the Scikit-learn model and scaler from .pkl files.
      2. Runs prediction logic using all 8 Pima dataset features.
      3. Saves the detailed result into the 'predictions' table.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        patient_id = request.form['patient_id']
        preg = float(request.form['pregnancies'])
        gluc = float(request.form['glucose'])
        bp = float(request.form['blood_pressure'])
        skin = float(request.form['skin_thickness'])
        insulin = float(request.form['insulin'])
        bmi = float(request.form['bmi'])
        dpf = float(request.form['diabetes_pedigree'])
        age = float(request.form['age'])

        try:
            # 1. Load the pre-trained Logistic Regression model and scaler
            model = joblib.load('model.pkl')
            scaler = joblib.load('scaler.pkl')
            
            # 2. Arrange inputs into a 2D array matching training feature order
            # Format: [[Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age]]
            input_data = np.array([[preg, gluc, bp, skin, insulin, bmi, dpf, age]])
            
            # 3. Scale the input using the same scaler used during training
            input_scaled = scaler.transform(input_data)
            
            # 4. Predict (returns 0 for healthy, 1 for diabetes)
            prediction_bin = model.predict(input_scaled)[0]
            result_text = "High Risk" if prediction_bin == 1 else "Low Risk"

            # 5. Save this specific prediction into MySQL history
            query = """
                INSERT INTO predictions 
                (patient_id, pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, diabetes_pedigree, age, result)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (patient_id, preg, gluc, bp, skin, insulin, bmi, dpf, age, result_text))
            conn.commit()
            cursor.close()
            conn.close()

            return render_template('predict.html', result=result_text, patients=[])
        except Exception as e:
            return f"Error during prediction: {str(e)}. Did you run 'train_model.py' first?"

    # For the GET request, we need a list of patients for the dropdown menu
    cursor.execute("SELECT id, name FROM patients")
    patients_list = cursor.fetchall()
    cursor.close()
    conn.close()

    # Check if a patient_id was passed via query param (e.g. from Patient History page)
    preselected_patient_id = request.args.get('patient_id', default=None, type=int)

    return render_template('predict.html', patients=patients_list,
                           preselected_patient_id=preselected_patient_id)

if __name__ == '__main__':
    # Start the server. In your local VS Code, debug=True is very helpful.
    app.run(host='0.0.0.0', port=3000, debug=True)
