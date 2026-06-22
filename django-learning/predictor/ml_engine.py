import os
import joblib
import numpy as np
import pandas as pd
from django.utils import timezone
from sklearn.ensemble import RandomForestClassifier
from django.conf import settings

# Path to save/load the trained model
MODEL_DIR = os.path.join(settings.BASE_DIR, 'predictor')
MODEL_PATH = os.path.join(MODEL_DIR, 'student_model.pkl')

def get_student_features(student):
    """
    Extracts numerical features for a single student.
    Returns: numpy array of features
    """
    results = student.results.all()
    
    if results.exists():
        mid_avg = sum(r.mid_term_marks for r in results) / len(results)
        assign_avg = sum(r.assignments_marks for r in results) / len(results)
        final_avg = sum(r.final_exam_marks for r in results) / len(results)
        gpa_avg = sum(r.gpa for r in results) / len(results)
    else:
        # Default fallback values for students with no marks entered yet
        mid_avg = 15.0  # mid-point of 30
        assign_avg = 10.0  # mid-point of 20
        final_avg = 25.0  # mid-point of 50
        gpa_avg = 2.0  # mid-point of 4.0

    return np.array([
        student.attendance_pct,
        student.study_hours_per_week,
        mid_avg,
        assign_avg,
        final_avg,
        gpa_avg
    ])

def generate_synthetic_data(n_samples=1500):
    """
    Generates synthetic training data with realistic correlations.
    Features:
    0: attendance_pct (0 to 100)
    1: study_hours_per_week (1 to 30)
    2: mid_term_avg (0 to 30)
    3: assignments_avg (0 to 20)
    4: final_exam_avg (0 to 50)
    5: gpa_avg (0.0 to 4.0)
    """
    np.random.seed(42)
    
    # 1. Random distributions
    attendance = np.random.uniform(50, 100, n_samples)
    study_hours = np.random.uniform(2, 28, n_samples)
    
    # Mid-term marks (correlated with attendance and study hours)
    mid_term = 10 + 0.15 * attendance + 0.2 * study_hours + np.random.normal(0, 2.5, n_samples)
    mid_term = np.clip(mid_term, 0, 30)
    
    # Assignments (correlated with study hours and attendance)
    assignments = 5 + 0.08 * attendance + 0.25 * study_hours + np.random.normal(0, 1.5, n_samples)
    assignments = np.clip(assignments, 0, 20)
    
    # Final exams (correlated with all previous)
    final_exam = 10 + 0.25 * attendance + 0.5 * study_hours + 0.5 * mid_term + np.random.normal(0, 4.0, n_samples)
    final_exam = np.clip(final_exam, 0, 50)
    
    # GPA (computed based on total marks)
    total_avg = mid_term + assignments + final_exam
    gpa = np.zeros(n_samples)
    gpa[total_avg >= 85] = 4.0
    gpa[(total_avg >= 70) & (total_avg < 85)] = 3.0 + (total_avg[(total_avg >= 70) & (total_avg < 85)] - 70) / 15.0
    gpa[(total_avg >= 55) & (total_avg < 70)] = 2.0 + (total_avg[(total_avg >= 55) & (total_avg < 70)] - 55) / 15.0
    gpa[(total_avg >= 40) & (total_avg < 55)] = 1.0 + (total_avg[(total_avg >= 40) & (total_avg < 55)] - 40) / 15.0
    gpa = np.clip(gpa, 0.0, 4.0)

    # 2. Determine target class
    # 0 = Fail, 1 = At-Risk, 2 = Pass
    y = np.zeros(n_samples, dtype=int)
    
    for i in range(n_samples):
        score = (
            0.25 * (attendance[i] / 100.0) +
            0.15 * (study_hours[i] / 30.0) +
            0.60 * (total_avg[i] / 100.0)
        )
        
        # Add random noise to class boundaries
        noise = np.random.normal(0, 0.04)
        final_score = score + noise
        
        if final_score < 0.50 or attendance[i] < 60.0 or total_avg[i] < 45.0:
            y[i] = 0  # Fail
        elif final_score < 0.68 or attendance[i] < 72.0 or total_avg[i] < 60.0:
            y[i] = 1  # At-Risk
        else:
            y[i] = 2  # Pass

    df = pd.DataFrame({
        'attendance_pct': attendance,
        'study_hours': study_hours,
        'mid_avg': mid_term,
        'assign_avg': assignments,
        'final_avg': final_exam,
        'gpa_avg': gpa,
        'target': y
    })
    
    return df

def train_model(extra_db_students=None):
    """
    Trains the Random Forest model using synthetic data and saves it.
    Can merge real students from db if provided.
    """
    df = generate_synthetic_data(2000)
    
    X = df[['attendance_pct', 'study_hours', 'mid_avg', 'assign_avg', 'final_avg', 'gpa_avg']].values
    y = df['target'].values
    
    # Merge with real db students if there are enough labeled ones
    if extra_db_students:
        extra_X = []
        extra_y = []
        for s in extra_db_students:
            # Only use students that have a manually confirmed status or previous correct prediction
            if s.predicted_status in ['Pass', 'At-Risk', 'Fail']:
                feat = get_student_features(s)
                status_map = {'Fail': 0, 'At-Risk': 1, 'Pass': 2}
                extra_X.append(feat)
                extra_y.append(status_map[s.predicted_status])
        if len(extra_X) > 0:
            X = np.vstack([X, np.array(extra_X)])
            y = np.concatenate([y, np.array(extra_y)])

    # Initialize and train Random Forest
    clf = RandomForestClassifier(n_estimators=150, max_depth=10, random_state=42)
    clf.fit(X, y)
    
    # Save model
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(clf, MODEL_PATH)
    return clf

def get_predictor_model():
    """
    Loads model from file. If it doesn't exist, trains it first.
    """
    if not os.path.exists(MODEL_PATH):
        return train_model()
    try:
        return joblib.load(MODEL_PATH)
    except Exception:
        return train_model()

def predict_student_performance(student):
    """
    Runs prediction for a single student.
    Saves predictions back to the student model in the database.
    """
    clf = get_predictor_model()
    features = get_student_features(student).reshape(1, -1)
    
    pred_class = clf.predict(features)[0]
    probabilities = clf.predict_proba(features)[0]
    
    # Map predictions
    status_map = {0: 'Fail', 1: 'At-Risk', 2: 'Pass'}
    student.predicted_status = status_map[pred_class]
    student.prediction_confidence = float(probabilities[pred_class] * 100)
    student.prediction_date = timezone.now()
    student.save()
    
    return {
        'status': student.predicted_status,
        'confidence': student.prediction_confidence
    }
