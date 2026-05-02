# DiabetesPredict — Capstone Presentation Content

> **Project**: Diabetes Risk Prediction System  
> **Stack**: Python · Flask · MySQL · Scikit-Learn · Chart.js · Bootstrap 5  
> **Date**: May 2026

---

## Slide 1: Introduction

### DiabetesPredict — AI-Powered Health Risk Assessment System

- A full-stack web application that combines **patient management** with **machine learning** to assess an individual's risk of developing diabetes.
- Built as a Capstone Project using modern, production-grade technologies.
- Designed for healthcare practitioners who need a fast, data-driven screening tool — not a replacement for clinical diagnosis, but a decision-support system.

**Technology Stack**:

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, Flask |
| Database | MySQL (MariaDB via XAMPP) |
| ML Engine | Scikit-Learn (Logistic Regression) |
| Frontend | Jinja2 Templates, Bootstrap 5, Chart.js |
| Data Handling | Pandas, NumPy |
| Model Persistence | Joblib (model.pkl, scaler.pkl) |

---

## Slide 2: Problem Statement

### The Growing Diabetes Crisis

- **Diabetes mellitus** is one of the fastest-growing chronic diseases worldwide. According to the WHO, the number of adults living with diabetes has more than quadrupled since 1980.
- Early detection is critical — **Type 2 diabetes is preventable** if risk factors are identified early and lifestyle interventions are applied.
- Many clinics, especially in underserved communities, lack access to advanced screening tools. Risk assessment often relies on subjective judgment rather than data.

### What This Project Solves

- Provides a **free, lightweight, locally-hosted** screening tool that any clinic with a basic computer can run.
- Uses **8 standard clinical biomarkers** (no expensive lab equipment beyond basic blood work) to generate an instant risk classification.
- Stores patient records and prediction history in a persistent database, enabling **longitudinal tracking** of a patient's health trajectory over time.

### Key Question

> *Given a set of 8 clinical biomarkers, can we accurately classify whether a patient is at high risk or low risk for diabetes?*

---

## Slide 3: System Features

### Feature Overview

**1. Patient Management (Full CRUD)**
- Register new patients with demographics (Name, Age, Gender, Contact)
- View, search, edit, and delete patient records
- Real-time client-side search with instant filtering

**2. AI-Powered Risk Prediction**
- Input 8 clinical biomarkers into a validated form
- ML model classifies the patient as **High Risk** or **Low Risk**
- Results are saved to the database and linked to the patient's history

**3. Analytics Dashboard**
- Total patients, total assessments, and high-risk rate at a glance
- Interactive doughnut chart showing risk distribution (High vs. Low)
- Color-coded bar chart of the 5 most recent assessments

**4. Patient Health History Timeline**
- Chronological timeline of all assessments for any individual patient
- Biomarker trend charts (Glucose, BP, BMI, Insulin, DPF, Age) across visits
- Pre-filled "New Assessment" button for quick follow-up evaluations

**5. UX & Accessibility**
- Client-side biomarker validation with real-time range feedback
- Skeleton loading overlay during ML prediction
- Responsive sidebar layout for desktop and mobile
- Accessible focus rings, ARIA labels, and screen-reader-friendly risk badges

---

## Slide 4: Database Design

### Schema: `diabetes_db`

The system uses **two tables** with a one-to-many relationship.

**Table 1: `patients`**

| Column | Type | Description |
|--------|------|-------------|
| `id` | INT (PK, Auto-increment) | Unique patient identifier |
| `name` | VARCHAR(255) | Full name |
| `age` | INT | Age in years |
| `gender` | VARCHAR(20) | Male / Female / Other |
| `contact` | VARCHAR(255) | Phone number or email |
| `created_at` | TIMESTAMP | Registration timestamp |

**Table 2: `predictions`**

| Column | Type | Description |
|--------|------|-------------|
| `id` | INT (PK, Auto-increment) | Unique prediction identifier |
| `patient_id` | INT (FK → patients.id) | Links prediction to a patient |
| `pregnancies` | INT | Number of pregnancies |
| `glucose` | INT | Plasma glucose concentration (mg/dL) |
| `blood_pressure` | INT | Diastolic blood pressure (mm Hg) |
| `skin_thickness` | INT | Triceps skinfold thickness (mm) |
| `insulin` | INT | 2-hour serum insulin (mu U/ml) |
| `bmi` | FLOAT | Body mass index (kg/m²) |
| `diabetes_pedigree` | FLOAT | Diabetes pedigree function score |
| `age` | INT | Age at time of assessment |
| `result` | VARCHAR(50) | "High Risk" or "Low Risk" |
| `created_at` | TIMESTAMP | Assessment timestamp |

### Relationship

```
patients (1) ──── (∞) predictions
   │                      │
   └── id (PK)    patient_id (FK, ON DELETE CASCADE)
```

- One patient can have **many predictions** over time.
- Deleting a patient **cascades** to remove all their prediction history.

---

## Slide 5: Machine Learning Model

### Dataset: Pima Indians Diabetes Dataset

- **Source**: UCI Machine Learning Repository / Kaggle
- **Size**: 768 patient samples, 8 features, 1 binary target
- **Population**: Female patients of Pima Indian heritage, age ≥ 21

### The 8 Input Features

| # | Feature | Unit | Range in Dataset |
|---|---------|------|-----------------|
| 1 | Pregnancies | count | 0 – 17 |
| 2 | Glucose | mg/dL | 0 – 199 |
| 3 | Blood Pressure | mm Hg | 0 – 122 |
| 4 | Skin Thickness | mm | 0 – 99 |
| 5 | Insulin | mu U/ml | 0 – 846 |
| 6 | BMI | kg/m² | 0 – 67.1 |
| 7 | Diabetes Pedigree Function | score | 0.078 – 2.42 |
| 8 | Age | years | 21 – 81 |

### Training Pipeline (`train_model.py`)

1. **Load** — Read `diabetes.csv` (768 rows × 9 columns)
2. **Split** — 80/20 train-test split with stratification (`random_state=42`)
3. **Scale** — StandardScaler applied to normalize all features to zero mean and unit variance
4. **Train** — Logistic Regression classifier (`max_iter=1000`)
5. **Evaluate** — Accuracy, precision, recall, F1-score on the test set
6. **Persist** — Model saved as `model.pkl`, scaler saved as `scaler.pkl` via Joblib

### Why Logistic Regression?

- Simple, interpretable, and clinically explainable
- Well-suited for binary classification (High Risk vs. Low Risk)
- Fast inference time — results return instantly in the web application
- Low computational requirements — runs on any machine, no GPU needed

---

## Slide 6: Flask + MySQL Integration

### Application Architecture

```
┌─────────────────────────────────────────────────────┐
│                     Browser                         │
│         (HTML / CSS / JS / Chart.js)                │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP Requests
┌──────────────────────▼──────────────────────────────┐
│                  Flask (app.py)                      │
│  ┌──────────────────────────────────────────────┐   │
│  │  Routes:                                      │   │
│  │  GET  /              → Dashboard              │   │
│  │  GET  /patients      → Patient List           │   │
│  │  POST /patients/add  → Register Patient       │   │
│  │  POST /patients/edit → Update Patient         │   │
│  │  GET  /patients/del  → Delete Patient         │   │
│  │  GET  /patients/:id/history → Timeline        │   │
│  │  GET  /predict       → Prediction Form        │   │
│  │  POST /predict       → Run ML Prediction      │   │
│  └──────────────────────────────────────────────┘   │
│            │                        │                │
│   ┌────────▼────────┐    ┌─────────▼──────────┐     │
│   │ mysql.connector  │    │ joblib.load()      │     │
│   │ (Database CRUD)  │    │ model.pkl          │     │
│   │                  │    │ scaler.pkl         │     │
│   └────────┬────────┘    └────────────────────┘     │
└────────────┼────────────────────────────────────────┘
             │
    ┌────────▼────────┐
    │  MySQL Server   │
    │  (diabetes_db)  │
    │  ┌───────────┐  │
    │  │ patients   │  │
    │  │ predictions│  │
    │  └───────────┘  │
    └─────────────────┘
```

### Key Integration Points

**1. Database Connection**
- Uses `mysql.connector` with a reusable `get_db_connection()` helper
- All queries use parameterized statements (`%s` placeholders) to prevent SQL injection

**2. Prediction Flow (POST /predict)**
```
User submits form → Flask receives 8 biomarkers
  → joblib.load('scaler.pkl') → scaler.transform(input)
  → joblib.load('model.pkl')  → model.predict(scaled_input)
  → result = "High Risk" or "Low Risk"
  → INSERT INTO predictions (...) VALUES (...)
  → render result page
```

**3. Template Rendering**
- Jinja2 templates receive Python data and render server-side HTML
- Chart.js receives data via inline JavaScript arrays built from Jinja2 loops
- Flash messages provide user feedback for CRUD operations

---

## Slide 7: Results

### Model Performance

| Metric | Low Risk (0) | High Risk (1) | Overall |
|--------|-------------|---------------|---------|
| Precision | ~0.80 | ~0.70 | — |
| Recall | ~0.85 | ~0.62 | — |
| F1-Score | ~0.82 | ~0.66 | — |
| **Accuracy** | — | — | **~77%** |

> *Values are approximate based on the standard Pima dataset with Logistic Regression. Actual figures depend on the random split.*

### System Capabilities Demonstrated

- ✅ End-to-end patient registration and management
- ✅ Instant risk classification from 8 clinical biomarkers
- ✅ Historical tracking with per-patient assessment timelines
- ✅ Visual analytics (doughnut chart, activity bar chart, biomarker trend lines)
- ✅ Responsive design that works on desktop and mobile
- ✅ Client-side input validation preventing out-of-range submissions
- ✅ Accessible interface with ARIA labels and focus indicators

### Limitations

- Model trained on a single demographic (Pima Indian women, age ≥ 21) — may not generalize well to other populations
- Logistic Regression is a linear model — cannot capture complex non-linear feature interactions
- No server-side validation of biomarker ranges (client-side only)
- Single-user system — no authentication or role-based access control

---

## Slide 8: Conclusion

### Summary

**DiabetesPredict** demonstrates a complete, functional integration of:
- **Web development** (Flask, Jinja2, Bootstrap 5, Chart.js)
- **Database design** (MySQL with relational schema and foreign key constraints)
- **Machine learning** (Scikit-Learn pipeline: preprocessing → training → persistence → inference)
- **UI/UX engineering** (responsive layout, micro-animations, validation, accessibility)

### What Was Learned

- How to bridge the gap between a trained ML model and a production web application
- The importance of data preprocessing consistency (the same scaler must be used at training and inference time)
- Building a real full-stack CRUD application with a relational database
- Designing user interfaces that communicate clinical information clearly and responsibly

### Future Improvements

| Area | Enhancement |
|------|------------|
| Model | Upgrade to Random Forest, XGBoost, or ensemble methods for higher accuracy |
| Data | Train on larger, more diverse datasets beyond the Pima population |
| Security | Add user authentication (login system) and role-based access |
| Deployment | Containerize with Docker for cloud deployment (e.g., AWS, Heroku) |
| Features | Add PDF report generation for each risk assessment |
| Validation | Implement server-side biomarker validation in the Flask route |

### Final Statement

> DiabetesPredict is a proof-of-concept that shows how accessible, AI-powered health tools can be built with open-source technologies — making early diabetes screening available to clinics that need it most.

---

*End of Presentation Content*
