-- ============================================
-- Diabetes Risk Prediction System
-- Database Schema (MySQL / MariaDB - XAMPP)
-- ============================================

-- Create the database
CREATE DATABASE IF NOT EXISTS diabetes_db;
USE diabetes_db;

-- Drop existing tables first (predictions depends on patients, so drop it first)
DROP TABLE IF EXISTS predictions;
DROP TABLE IF EXISTS patients;

-- ============================================
-- 1. Patients Table
-- Stores registered patient information.
-- ============================================
CREATE TABLE patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    age INT NOT NULL,
    gender VARCHAR(20) NOT NULL,
    contact VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================
-- 2. Predictions Table
-- Stores every AI risk assessment.
-- All 8 features from the Pima Indians Diabetes Dataset.
-- Linked to a patient via 'patient_id'.
-- ============================================
CREATE TABLE predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    pregnancies INT DEFAULT 0,
    glucose INT DEFAULT 0,
    blood_pressure INT DEFAULT 0,
    skin_thickness INT DEFAULT 0,
    insulin INT DEFAULT 0,
    bmi FLOAT DEFAULT 0.0,
    diabetes_pedigree FLOAT DEFAULT 0.0,
    age INT DEFAULT 0,
    result VARCHAR(50) NOT NULL COMMENT 'High Risk or Low Risk',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_patient FOREIGN KEY (patient_id)
        REFERENCES patients(id) ON DELETE CASCADE
) ENGINE=InnoDB;
