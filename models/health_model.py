"""
health_model.py
----------------
A small, self-contained DEMO machine-learning model used for the
"Health Risk Prediction" feature.

This model is trained on a small SYNTHETIC dataset (data/sample_health_data.csv)
using scikit-learn's RandomForestClassifier. It exists purely to demonstrate
an AI/ML component integrated into the SCM/DevOps pipeline.

DISCLAIMER: This is an educational demo model only. It must NEVER be used
for real medical decisions or real patient data.
"""

import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_PATH = os.path.join(BASE_DIR, "data", "sample_health_data.csv")

LABELS = ["Low", "Moderate", "High"]


class HealthRiskModel:
    """Wraps a scikit-learn classifier trained on demo health data."""

    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100, max_depth=6, random_state=42
        )
        self.feature_columns = [
            "age", "heart_rate", "spo2", "sleep_hours", "activity_level", "bmi"
        ]
        self.is_trained = False

    def train(self):
        """Train the model on the synthetic CSV dataset."""
        df = pd.read_csv(DATA_PATH)

        X = df[self.feature_columns]
        y = df["risk_label"]

        # A small train/test split just to demonstrate standard ML practice;
        # the whole dataset is synthetic and small by design.
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        self.model.fit(X_train, y_train)
        self.is_trained = True

        # Basic accuracy print for demo/console visibility (used in tests/logs).
        accuracy = self.model.score(X_test, y_test)
        print(f"[HealthRiskModel] Demo model trained. Test accuracy: {accuracy:.2f}")
        return accuracy

    def predict(self, age, heart_rate, spo2, sleep_hours, activity_level, bmi):
        """Predict a risk label ('Low' / 'Moderate' / 'High') for one sample."""
        if not self.is_trained:
            self.train()

        row = pd.DataFrame(
            [[age, heart_rate, spo2, sleep_hours, activity_level, bmi]],
            columns=self.feature_columns,
        )
        prediction = self.model.predict(row)[0]
        return prediction


if __name__ == "__main__":
    # Allows running `python models/health_model.py` standalone for a quick check.
    m = HealthRiskModel()
    m.train()
    sample = m.predict(age=45, heart_rate=110, spo2=93, sleep_hours=4, activity_level=0, bmi=29)
    print("Sample prediction:", sample)
