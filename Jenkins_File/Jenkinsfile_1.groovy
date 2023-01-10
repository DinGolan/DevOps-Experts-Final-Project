pipeline {
    agent any
    stages {
        // Step 1 - Clone Git From GitHub //
        stage("Clone Git") {
            steps {
                git "https://github.com/DinGolan/DevOps-Experts-Final-Project.git"
            }
        }

        // Step 2 - Run REST API //
        stage("Run `rest_app.py` (Backend)") {
            steps {
                bat 'start /min python rest_app.py'
            }
        }

        // Step 3 - Run WEB APP  //
        stage("Run `web_app.py` (Frontend)") {
            steps {
                bat 'start /min python web_app.py'
            }
        }

        // Step 4 - Run Backend Test //
        stage("Run `backend_testing.py` (Testing)") {
            steps {
                bat 'python backend_testing.py'
            }
        }

        // Step 5 - Run Frontend Test //
        stage("Run `frontend_testing.py` (Testing)") {
            steps {
                bat 'python frontend_testing.py'
            }
        }

        // Step 6 - Run Combined Test //
        stage("Run `combined_testing.py` (Testing)") {
            steps {
                bat 'python combined_testing.py'
            }
        }

        // Step 7 - Run Clean Environment //
        stage("Run `clean_environment.py` (Clean)") {
            steps {
                bat 'python clean_environment.py'
            }
        }
    }
}