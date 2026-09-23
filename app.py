"""
AI-Powered Smart Fitness Tracking and Personalized Health Monitoring System
----------------------------------------------------------------------------
Main Flask application.

IMPORTANT DISCLAIMER:
This application is an ACADEMIC / EDUCATIONAL project built primarily to
demonstrate Software Configuration Management (SCM) and DevOps practices
(Git, GitHub, Jenkins, Docker). The health-risk prediction and alerts are
DEMO features built on a small synthetic dataset. They are NOT a medical
diagnosis system and must never be used for real clinical decisions.
"""

import os
import sqlite3
import cv2
import mediapipe as mp
import math
from datetime import datetime

from flask import Flask, render_template, request, jsonify, g, Response
from models.health_model import HealthRiskModel

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "health_monitor.db")

app = Flask(__name__)
app.config["DATABASE"] = DB_PATH

# Train (or load) the demo ML model once at startup.
health_model = HealthRiskModel()
health_model.train()
# ----------------------------------------------------------------------
# Camera / Squat Detection
# ----------------------------------------------------------------------

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

pose = mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

camera = None
squat_count = 0
squat_position = "UP"
knee_angle = 0


def calculate_angle(a, b, c):
    """Calculate angle ABC."""

    angle = math.degrees(
        math.atan2(c[1] - b[1], c[0] - b[0])
        -
        math.atan2(a[1] - b[1], a[0] - b[0])
    )

    angle = abs(angle)

    if angle > 180:
        angle = 360 - angle

    return angle


# ----------------------------------------------------------------------
# Database helpers
# ----------------------------------------------------------------------
def get_db():
    """Open a new database connection for the current request context."""
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create all required tables if they do not already exist."""
    os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS health_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            heart_rate INTEGER,
            spo2 INTEGER,
            sleep_hours REAL,
            steps INTEGER,
            calories_burned REAL,
            bmi REAL,
            recorded_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );

        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            activity_type TEXT,
            duration_minutes INTEGER,
            calories_burned REAL,
            logged_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );

        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            category TEXT,
            recommendation_text TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );

        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            alert_type TEXT,
            message TEXT,
            severity TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
        """
    )

    # Seed one demo user + a sample health record so the dashboard is
    # never empty on first run.
    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO users (name, age) VALUES (?, ?)", ("Demo User", 24)
        )
        user_id = cur.lastrowid
        cur.execute(
            """INSERT INTO health_records
               (user_id, heart_rate, spo2, sleep_hours, steps, calories_burned, bmi)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_id, 78, 97, 6.5, 6400, 320.0, 22.5),
        )
        cur.execute(
            """INSERT INTO activities (user_id, activity_type, duration_minutes, calories_burned)
               VALUES (?, ?, ?, ?)""",
            (user_id, "Walking", 35, 150.0),
        )

    conn.commit()
    conn.close()


# ----------------------------------------------------------------------
# Demo alert-threshold logic
# ----------------------------------------------------------------------
def generate_alerts(heart_rate, spo2, sleep_hours):
    """Return a list of demo alert dicts based on simple fixed thresholds.

    These thresholds are illustrative only and are NOT clinically validated.
    """
    alerts = []
    if heart_rate is not None:
        if heart_rate > 130:
            alerts.append(
                {"type": "Heart Rate", "message": "Very high heart rate detected.", "severity": "High"}
            )
        elif heart_rate < 45:
            alerts.append(
                {"type": "Heart Rate", "message": "Unusually low heart rate detected.", "severity": "High"}
            )

    if spo2 is not None and spo2 < 92:
        alerts.append(
            {"type": "SpO2", "message": "Low blood oxygen (SpO2) level detected.", "severity": "High"}
        )

    if sleep_hours is not None and sleep_hours < 4:
        alerts.append(
            {"type": "Sleep", "message": "Very low sleep duration detected.", "severity": "Moderate"}
        )

    return alerts


def generate_recommendations(activity_level, sleep_hours, bmi):
    """Very simple rule-based demo recommendations (not medical advice)."""
    recs = {"exercise": [], "diet": [], "sleep": [], "daily_activity": []}

    if activity_level == "low":
        recs["exercise"].append("Add a 20-30 minute brisk walk to your day.")
        recs["daily_activity"].append("Try to reach at least 6,000 steps/day.")
    elif activity_level == "moderate":
        recs["exercise"].append("Consider adding one extra cardio session per week.")
        recs["daily_activity"].append("Aim for 8,000-10,000 steps/day.")
    else:
        recs["exercise"].append("Great activity level — keep mixing cardio and strength training.")
        recs["daily_activity"].append("Maintain your current activity routine.")

    if sleep_hours is not None and sleep_hours < 6:
        recs["sleep"].append("Try to increase sleep to 7-8 hours for better recovery.")
    else:
        recs["sleep"].append("Your sleep duration looks healthy — keep it consistent.")

    if bmi is not None and bmi >= 25:
        recs["diet"].append("Consider more fiber-rich foods and reduce refined sugar intake.")
    elif bmi is not None and bmi < 18.5:
        recs["diet"].append("Consider a slightly higher calorie intake with balanced nutrients.")
    else:
        recs["diet"].append("Your BMI is in a healthy range — maintain a balanced diet.")

    return recs

def generate_camera_frames():

    global camera
    global squat_count
    global squat_position
    global knee_angle

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Camera could not be opened.")
        return

    while True:

        success, frame = camera.read()

        if not success:
            break

        # Flip camera horizontally
        frame = cv2.flip(frame, 1)

        # Convert BGR → RGB
        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        # Detect pose
        results = pose.process(rgb_frame)

        if results.pose_landmarks:

            landmarks = results.pose_landmarks.landmark

            hip = landmarks[
                mp_pose.PoseLandmark.RIGHT_HIP
            ]

            knee = landmarks[
                mp_pose.PoseLandmark.RIGHT_KNEE
            ]

            ankle = landmarks[
                mp_pose.PoseLandmark.RIGHT_ANKLE
            ]

            hip_point = (
                int(hip.x * frame.shape[1]),
                int(hip.y * frame.shape[0])
            )

            knee_point = (
                int(knee.x * frame.shape[1]),
                int(knee.y * frame.shape[0])
            )

            ankle_point = (
                int(ankle.x * frame.shape[1]),
                int(ankle.y * frame.shape[0])
            )

            angle = calculate_angle(
                hip_point,
                knee_point,
                ankle_point
            )

            knee_angle = int(angle)

            # --------------------------------
            # Squat detection
            # --------------------------------

            if angle > 160:
                squat_position = "UP"

            elif angle < 90 and squat_position == "UP":
                squat_position = "DOWN"
                squat_count += 1

            # --------------------------------
            # Draw pose
            # --------------------------------

            mp_drawing.draw_landmarks(
                frame,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS
            )

            cv2.putText(
                frame,
                f"Squats: {squat_count}",
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.2,
                (0, 255, 0),
                3
            )

            cv2.putText(
                frame,
                f"Knee Angle: {knee_angle}",
                (30, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 0),
                2
            )

            cv2.putText(
                frame,
                f"Position: {squat_position}",
                (30, 130),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 200, 255),
                2
            )

        else:

            cv2.putText(
                frame,
                "No person detected",
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2
            )

        # Convert frame to JPEG
        ret, buffer = cv2.imencode(
            ".jpg",
            frame
        )

        if not ret:
            continue

        frame_bytes = buffer.tobytes()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + frame_bytes
            + b"\r\n"
        )

    camera.release()

# ----------------------------------------------------------------------
# Routes
# ----------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    db = get_db()
    record = db.execute(
        "SELECT * FROM health_records ORDER BY id DESC LIMIT 1"
    ).fetchone()
    activities = db.execute(
        "SELECT * FROM activities ORDER BY id DESC LIMIT 5"
    ).fetchall()
    return render_template("dashboard.html", record=record, activities=activities)

@app.route("/camera")
def camera_page():
    return render_template("dashboard.html")


@app.route("/video_feed")
def video_feed():
    return Response(
        generate_camera_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/squat_data")
def squat_data():

    return jsonify({
        "squats": squat_count,
        "angle": knee_angle,
        "position": squat_position
    })


@app.route("/reset_squats")
def reset_squats():

    global squat_count
    global squat_position
    global knee_angle

    squat_count = 0
    squat_position = "UP"
    knee_angle = 0

    return jsonify({
        "status": "reset",
        "squats": 0
    })
@app.route("/activity", methods=["GET", "POST"])
def activity():
    db = get_db()
    message = None
    if request.method == "POST":
        activity_type = request.form.get("activity_type", "Walking")
        duration = int(request.form.get("duration_minutes", 0) or 0)
        # Simple demo calorie estimate (MET-based approximation).
        met_values = {"Walking": 3.5, "Running": 8.0, "Cycling": 6.0, "Other": 4.0}
        met = met_values.get(activity_type, 4.0)
        calories = round(met * 3.5 * 70 / 200 * duration, 1)  # approx, 70kg demo weight

        db.execute(
            """INSERT INTO activities (user_id, activity_type, duration_minutes, calories_burned)
               VALUES (1, ?, ?, ?)""",
            (activity_type, duration, calories),
        )
        db.commit()
        message = f"Logged {duration} min of {activity_type} (~{calories} kcal)."

    activities = db.execute(
        "SELECT * FROM activities ORDER BY id DESC LIMIT 10"
    ).fetchall()
    return render_template("activity.html", activities=activities, message=message)


@app.route("/predict", methods=["GET", "POST"])
def predict():
    result = None
    input_values = None
    if request.method == "POST":
        try:
            age = float(request.form.get("age", 30))
            heart_rate = float(request.form.get("heart_rate", 75))
            spo2 = float(request.form.get("spo2", 97))
            sleep_hours = float(request.form.get("sleep_hours", 7))
            bmi = float(request.form.get("bmi", 22))
            activity_level_map = {"low": 0, "moderate": 1, "high": 2}
            activity_level_label = request.form.get("activity_level", "moderate")
            activity_level = activity_level_map.get(activity_level_label, 1)

            input_values = {
                "age": age, "heart_rate": heart_rate, "spo2": spo2,
                "sleep_hours": sleep_hours, "bmi": bmi,
                "activity_level": activity_level_label,
            }

            risk_label = health_model.predict(
                age, heart_rate, spo2, sleep_hours, activity_level, bmi
            )
            result = risk_label

            db = get_db()
            alerts = generate_alerts(heart_rate, spo2, sleep_hours)
            for a in alerts:
                db.execute(
                    """INSERT INTO alerts (user_id, alert_type, message, severity)
                       VALUES (1, ?, ?, ?)""",
                    (a["type"], a["message"], a["severity"]),
                )
            db.commit()
        except ValueError:
            result = "Invalid input"

    return render_template("prediction.html", result=result, input_values=input_values)


@app.route("/recommendations", methods=["GET", "POST"])
def recommendations():
    recs = None
    if request.method == "POST":
        activity_level = request.form.get("activity_level", "moderate")
        sleep_hours = float(request.form.get("sleep_hours", 7) or 7)
        bmi = float(request.form.get("bmi", 22) or 22)

        recs = generate_recommendations(activity_level, sleep_hours, bmi)

        db = get_db()
        for category, items in recs.items():
            for text in items:
                db.execute(
                    """INSERT INTO recommendations (user_id, category, recommendation_text)
                       VALUES (1, ?, ?)""",
                    (category, text),
                )
        db.commit()
    else:
        recs = generate_recommendations("moderate", 7, 22)

    return render_template("recommendations.html", recs=recs)


@app.route("/alerts")
def alerts_page():
    db = get_db()
    all_alerts = db.execute(
        "SELECT * FROM alerts ORDER BY id DESC LIMIT 20"
    ).fetchall()
    return render_template("alerts.html", alerts=all_alerts)


@app.route("/api/health-check")
def health_check():
    """Simple JSON health-check endpoint, also useful for Docker/Jenkins checks."""
    return jsonify({"status": "ok", "time": datetime.utcnow().isoformat()})


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
else:
    # Ensure DB exists when imported (e.g. by pytest or gunicorn).
    init_db()
