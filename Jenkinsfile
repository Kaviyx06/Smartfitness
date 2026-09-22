// ---------------------------------------------------------------------
// Jenkinsfile - CI/CD pipeline for the Smart Fitness Health Monitor
//
// Stages: Checkout -> Install Dependencies -> Run Tests -> Build Docker
//         Image -> Run/Validate Docker Container -> (optional) Push to
//         Docker Hub
//
// Docker Hub credentials must be configured in Jenkins as a
// "Username with password" credential (Manage Jenkins > Credentials)
// with the ID referenced below (DOCKERHUB_CREDENTIALS). No secrets are
// ever hard-coded in this file.
// ---------------------------------------------------------------------

pipeline {
    agent any

    environment {
        IMAGE_NAME        = "smart-fitness-health"
        CONTAINER_NAME     = "smart-fitness-health-container"
        DOCKERHUB_REPO     = "yourdockerhubusername/smart-fitness-health" // update before use
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')      // Jenkins credential ID
    }

    options {
        timestamps()
        skipDefaultCheckout(false)
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out source code from GitHub...'
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Setting up Python virtual environment and installing dependencies...'
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Running automated pytest test suite...'
                sh '''
                    . venv/bin/activate
                    pytest --junitxml=test-results.xml
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'test-results.xml'
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                sh 'docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} -t ${IMAGE_NAME}:latest .'
            }
        }

        stage('Run/Validate Docker Container') {
            steps {
                echo 'Running container and validating health-check endpoint...'
                sh '''
                    docker rm -f ${CONTAINER_NAME} || true
                    docker run -d -p 5000:5000 --name ${CONTAINER_NAME} ${IMAGE_NAME}:latest
                    sleep 8
                    curl -f http://localhost:5000/api/health-check
                '''
            }
        }

        stage('Push to Docker Hub') {
            when {
                expression { return env.PUSH_TO_DOCKERHUB == 'true' }
            }
            steps {
                echo 'Logging into Docker Hub securely using Jenkins credentials...'
                sh '''
                    echo "$DOCKERHUB_CREDENTIALS_PSW" | docker login -u "$DOCKERHUB_CREDENTIALS_USR" --password-stdin
                    docker tag ${IMAGE_NAME}:latest ${DOCKERHUB_REPO}:latest
                    docker push ${DOCKERHUB_REPO}:latest
                '''
            }
        }
    }

    post {
        always {
            echo 'Cleaning up dangling containers/images (demo cleanup)...'
            sh 'docker rm -f ${CONTAINER_NAME} || true'
        }
        success {
            echo '✅ Pipeline completed successfully.'
        }
        failure {
            echo '❌ Pipeline failed. Check the console output above.'
        }
    }
}
