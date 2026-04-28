-- Create the main database
CREATE DATABASE IF NOT EXISTS diabetes_db;
USE diabetes_db;

-- 1. Patients Table
-- This table stores a list of all your patients.
CREATE TABLE IF NOT EXISTS patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    age INT NOT NULL,
    gender VARCHAR(20) NOT NULL,
    contact VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Predictions Table
-- This table stores every assessment done by the AI system.
-- It is linked to a patient using 'patient_id'.
CREATE TABLE IF NOT EXISTS predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    pregnancies INT DEFAULT 0,
    glucose INT DEFAULT 0,
    blood_pressure INT DEFAULT 0,
    bmi FLOAT DEFAULT 0.0,
    age INT DEFAULT 0,
    result VARCHAR(50) NOT NULL, -- "High Risk" or "Low Risk"
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_patient FOREIGN KEY (patient_id) 
    REFERENCES patients(id) ON DELETE CASCADE
);
