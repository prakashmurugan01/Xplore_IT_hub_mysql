"""Lightweight ML predictor with safe fallbacks when numpy/scikit-learn are not installed."""
# Use dynamic imports so the module can be imported even when ML packages aren't installed.
import importlib
np = None
LinearRegression = None
try:
    np = importlib.import_module('numpy')
    skl = importlib.import_module('sklearn.linear_model')
    LinearRegression = getattr(skl, 'LinearRegression', None)
except Exception:
    np = None
    LinearRegression = None

from django.db.models import Avg
from .models import Attendance, Submission, Profile


class PerformancePredictor:
    """Lightweight predictor that uses a trained LinearRegression when available
    and a deterministic heuristic fallback otherwise. The fallback produces
    explainable scores based on attendance, average marks and assignment
    completion so the admin UI always has useful output even when ML
    dependencies are not installed.
    """
    def __init__(self):
        if LinearRegression is not None:
            self.model = LinearRegression()
        else:
            self.model = None
        # Was a real model successfully trained?
        self.trained = False

    def get_student_data(self, student_profile):
        # Attendance percentage
        total_attendance = Attendance.objects.filter(student=student_profile).count()
        present_count = Attendance.objects.filter(student=student_profile, status=True).count()
        attendance_percent = (present_count / total_attendance * 100) if total_attendance > 0 else 0

        # Average marks
        submissions = Submission.objects.filter(student=student_profile).exclude(marks_obtained__isnull=True)
        avg_marks = submissions.aggregate(Avg('marks_obtained'))['marks_obtained__avg'] or 0

        total_assignments = submissions.count()

        return {
            'attendance_percent': attendance_percent,
            'avg_marks': avg_marks,
            'assignments_completed': total_assignments,
        }

    def train_model(self):
        # If no ML libs available, skip training
        if self.model is None or np is None:
            self.trained = False
            return False

        students = Profile.objects.filter(role='student')
        X = []
        y = []

        for student in students:
            data = self.get_student_data(student)
            if data['assignments_completed'] > 0:
                X.append([data['attendance_percent'], data['avg_marks'], data['assignments_completed']])
                perf = (data['attendance_percent'] * 0.3) + (data['avg_marks'] * 0.7)
                y.append(perf)

        if len(X) > 5:
            X = np.array(X)
            y = np.array(y)
            try:
                self.model.fit(X, y)
                self.trained = True
                return True
            except Exception:
                self.trained = False
                return False
        # Not enough data to train a reliable model
        self.trained = False
        return False

    def predict_performance(self, student_profile):
        data = self.get_student_data(student_profile)
        # If we have a trained model, use it. Otherwise fall back to a
        # deterministic heuristic so the admin page always shows useful info.
        if self.model is not None and self.trained and np is not None:
            try:
                features = np.array([[data['attendance_percent'], data['avg_marks'], data['assignments_completed']]])
                prediction = float(self.model.predict(features)[0])
            except Exception:
                # fallback to heuristic on prediction failure
                prediction = None
        else:
            prediction = None

        if prediction is None:
            # Heuristic: weighted sum (attendance 30%, avg_marks 60%, assignments 10%)
            # Normalize so result is on a 0-100 scale. This is deterministic and
            # interpretable for admins.
            att = data['attendance_percent']
            marks = data['avg_marks']
            assigns = data['assignments_completed']
            # cap values defensively
            att = max(0.0, min(100.0, float(att)))
            marks = max(0.0, min(100.0, float(marks)))
            assigns_factor = min(assigns, 20) / 20.0  # treat 20+ assignments as full
            prediction = (att * 0.3) + (marks * 0.6) + (assigns_factor * 100 * 0.1)

        # Map numeric score to category and bootstrap UI color classes
        if prediction >= 85:
            category = 'Excellent'
            color = 'success'
        elif prediction >= 70:
            category = 'Good'
            color = 'primary'
        elif prediction >= 50:
            category = 'Average'
            color = 'warning'
        else:
            category = 'Needs Improvement'
            color = 'danger'

        return {
            'score': round(float(prediction), 2),
            'category': category,
            'color': color,
            'attendance': round(data['attendance_percent'], 2),
            'avg_marks': round(data['avg_marks'], 2),
            'method': 'trained' if self.trained else 'heuristic',
        }
