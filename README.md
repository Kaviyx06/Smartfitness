# AI-Powered Smart Fitness Tracking and Personalized Health Monitoring System

An academic **Software Configuration Management (SCM)** project that pairs a small
Flask + AI/ML fitness/health-monitoring web app with a complete Git → GitHub →
Jenkins → Docker CI/CD pipeline.

> **Disclaimer:** This project is for educational purposes only. The health-risk
> predictions and alerts are demo features built on a small synthetic dataset.
> **This is NOT a medical diagnosis system.** Always consult a qualified healthcare
> professional for real health concerns.

---

## 1. Abstract

The system simulates an intelligent fitness/health-monitoring application that reads
wearable-style metrics (heart rate, steps, calories, sleep, SpO2) and uses a simple
scikit-learn model to produce a demo health-risk category, plus rule-based
recommendations and threshold-based alerts. While the app itself is realistic, the
**primary academic goal of this project is to demonstrate SCM and DevOps practices**:
version control, branching, pull requests, CI pipelines, and containerized deployment.

## 2. Problem Statement

Manually tracking fitness and health metrics across multiple parameters is tedious,
and few student-accessible projects show *both* a working AI-enabled web app *and* a
realistic professional software delivery pipeline (Git/GitHub/Jenkins/Docker). This
project addresses both gaps in one buildable, demonstrable package.

## 3. Objectives

- Build a working Flask web application with a small ML-based demo feature.
- Demonstrate full SCM lifecycle: init → branch → commit → merge → tag → release.
- Automate testing and builds with Jenkins CI/CD.
- Containerize the application with Docker for portable deployment.
- Produce complete documentation suitable for a faculty/viva demonstration.

## 4. Features

- Home page, Dashboard, Activity logging, Health-risk prediction, Recommendations, Alerts
- SQLite-backed persistence (users, health_records, activities, recommendations, alerts)
- Demo ML model (RandomForestClassifier) trained on a synthetic dataset
- Rule-based alert thresholds and personalized recommendation engine
- Automated pytest test suite
- Dockerized deployment with `docker-compose`
- Jenkins declarative pipeline (Checkout → Install → Test → Build → Run/Validate)

## 5. Applications

- Personal fitness management · Healthcare monitoring (educational) · Sports/athletic
  training · Elderly health supervision (demo) · Preventive healthcare awareness

## 6. Technology Stack

| Layer      | Technology                          |
|------------|--------------------------------------|
| Frontend   | HTML, CSS, JavaScript, Bootstrap 5   |
| Backend    | Python, Flask                        |
| Database   | SQLite                               |
| AI/ML      | Python, scikit-learn, pandas, numpy  |
| SCM/DevOps | Git, GitHub, Jenkins, Docker         |

## 7. System Architecture

**Application flow:**

```
User
 ↓
Web Interface (HTML/CSS/JS + Bootstrap)
 ↓
Flask Backend (app.py)
 ↓
SQLite Database (data/health_monitor.db)
 ↓
ML Prediction Module (models/health_model.py)
 ↓
Recommendations / Alerts (rule-based logic in app.py)
 ↓
Dashboard (rendered back to the user)
```

**SCM / CI-CD flow:**

```
Developer
 ↓
Git (local commits, branches)
 ↓
GitHub (remote repository, pull requests)
 ↓
Jenkins (triggered on push / manually built)
 ↓
Automated Tests (pytest)
 ↓
Docker Build (Dockerfile)
 ↓
Docker Container (port 5000)
 ↓
Running Application
```

## 8. Project Structure

```
smart-fitness-health-monitor/
│
├── app.py                     # Main Flask application (routes, DB, alerts/recs logic)
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker build definition
├── docker-compose.yml         # Docker Compose service definition
├── Jenkinsfile                # Jenkins declarative CI/CD pipeline
├── README.md                  # This file
├── .gitignore                 # Git ignore rules
│
├── templates/                 # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   ├── activity.html
│   ├── prediction.html
│   ├── recommendations.html
│   └── alerts.html
│
├── static/
│   ├── css/style.css
│   └── js/script.js
│
├── models/
│   ├── __init__.py
│   └── health_model.py        # Demo scikit-learn risk-prediction model
│
├── data/
│   └── sample_health_data.csv # Synthetic training dataset (300 rows)
│
└── tests/
    └── test_app.py            # pytest test suite (13 tests)
```

## 9. Installation (Local)

**Prerequisites:** Python 3.10+ and pip installed, Git installed.

```powershell
git clone https://github.com/<your-username>/smart-fitness-health-monitor.git
cd smart-fitness-health-monitor
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## 10. How to Run Locally

```powershell
python app.py
```

Then open a browser at: `http://127.0.0.1:5000`

## 11. How to Run with Docker

```powershell
docker build -t smart-fitness-health .
docker run -d -p 5000:5000 --name smart-fitness-health-container smart-fitness-health
```

Or with Docker Compose:

```powershell
docker compose up --build
```

Visit `http://localhost:5000`.

## 12. Git Commands Used

```bash
git init
git add .
git commit -m "Initial project setup"
git branch develop
git remote add origin https://github.com/<your-username>/smart-fitness-health-monitor.git
git push -u origin main
```

## 13. GitHub Setup

1. Create a new empty repository on GitHub (no README/license, since we already have local files).
2. Copy the repository URL (HTTPS or SSH).
3. Add it as a remote: `git remote add origin <url>`
4. Push: `git push -u origin main`
5. To clone elsewhere: `git clone <url>`

## 14. Branching Strategy

```
main
│
├── develop
│
├── feature/dashboard
├── feature/health-prediction
├── feature/recommendations
└── feature/alerts
```

- **main** — stable, release-ready code (tagged releases live here, e.g. `v1.0.0`).
- **develop** — integration branch where completed features are merged before a release.
- **feature/\*** — one branch per feature, created off `develop`, merged back via pull
  request once complete. This keeps unfinished work isolated from stable code and
  makes code review straightforward.

**Typical feature workflow:**

```bash
git checkout develop
git checkout -b feature/dashboard
# ... make changes ...
git add .
git commit -m "Add fitness dashboard"
git push -u origin feature/dashboard
# Open a Pull Request: feature/dashboard -> develop
# After review/approval, merge the PR
git checkout develop
git pull
git branch -d feature/dashboard
```

**Conflict resolution:** if Git reports a merge conflict, open the affected file(s),
resolve the `<<<<<<<` / `=======` / `>>>>>>>` markers manually, then:

```bash
git add <resolved-file>
git commit
```

## 15. Version Control Practices Demonstrated

Example meaningful commit history:

```
Initial project setup
Add fitness dashboard
Add health monitoring
Add health risk prediction
Add personalized recommendations
Add alert system
Add automated testing
Add Docker support
Add Jenkins CI pipeline
```

Useful commands:

```bash
git log --oneline --graph --all
git status
git diff
git tag -a v1.0.0 -m "First stable release"
git push origin v1.0.0
```

## 16. Jenkins Setup

1. Install Jenkins (with the "Pipeline" and "Git" plugins).
2. In Jenkins, create a **New Item → Pipeline**.
3. Under **Pipeline**, choose "Pipeline script from SCM", select **Git**, and enter
   the GitHub repository URL and branch (e.g. `main`).
4. Set the **Script Path** to `Jenkinsfile` (already at the project root).
5. If pushing to Docker Hub, go to **Manage Jenkins → Credentials** and add a
   "Username with password" credential with the ID `dockerhub-credentials`
   (matches `DOCKERHUB_CREDENTIALS` in the Jenkinsfile). **Never hard-code
   credentials directly in the Jenkinsfile.**
6. Click **Build Now** to run the pipeline manually, or configure a GitHub webhook
   for automatic builds on push.

## 17. CI/CD Pipeline (Jenkinsfile stages)

1. **Checkout** — pulls the latest code from GitHub.
2. **Install Dependencies** — creates a virtual environment and installs
   `requirements.txt`.
3. **Run Tests** — executes the pytest suite and publishes JUnit results.
4. **Build Docker Image** — builds `smart-fitness-health:<build-number>` and `:latest`.
5. **Run/Validate Docker Container** — runs the image and curls the
   `/api/health-check` endpoint to confirm it started correctly.
6. **Push to Docker Hub** *(optional, gated by `PUSH_TO_DOCKERHUB` build parameter)* —
   logs in using the Jenkins credential and pushes the image.

## 18. Testing

Run the automated test suite from the project root:

```powershell
pytest
```

The suite (`tests/test_app.py`) covers: the home page, dashboard, activity logging,
health-risk prediction (low and high risk), alert generation, recommendations,
the JSON health-check endpoint, database table creation, and the ML model directly.

## 19. SCM Practices Used in This Project

- Distributed version control with Git
- Centralized collaboration via GitHub
- Feature-branch workflow with pull requests and code review
- Meaningful, descriptive commit messages
- Semantic version tagging (`v1.0.0`)
- Configuration-as-code (`Dockerfile`, `docker-compose.yml`, `Jenkinsfile`)
- Automated testing integrated into the CI pipeline
- Continuous Integration via Jenkins
- Containerization and reproducible builds via Docker

## 20. Future Enhancements

- Real wearable-device / IoT sensor integration (e.g. Bluetooth Low Energy)
- User authentication and multi-user support
- More advanced ML models trained on larger, ethically-sourced datasets
- Real-time notifications (email/SMS/push) for alerts
- Kubernetes-based orchestration for scaling
- Automatic deployment stage (Continuous Deployment) to a cloud host

## 21. Limitations

- The ML model is trained on a small **synthetic** dataset — it is illustrative, not
  clinically validated.
- No real sensor/wearable hardware integration.
- Single-user demo data model (no authentication).
- Alert thresholds are simplified fixed values, not adaptive or condition-specific.

## 22. Disclaimer

This project is an **academic SCM/DevOps demonstration**. The health-risk prediction,
alerts, and recommendations are **for educational purposes only** and **do not
constitute medical advice or diagnosis**. Do not use this application for real
healthcare decisions.
