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
                script {
                    withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'DB_USER_NAME', passwordVariable: 'DB_PASSWORD')]) {
                        bat 'start /min python rest_app.py -u ${DB_USER_NAME} -p ${DB_PASSWORD}'
                    }
                }
            }
        }

        // Step 3 - Run WEB APP  //
        stage("Run `web_app.py` (Frontend)") {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'DB_USER_NAME', passwordVariable: 'DB_PASSWORD')]) {
                        bat 'start /min python web_app.py -u ${DB_USER_NAME} -p ${DB_PASSWORD}'
                    }
                }
            }
        }

        // Step 4 - Run Backend Test //
        stage("Run `backend_testing.py` (Testing)") {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'DB_USER_NAME', passwordVariable: 'DB_PASSWORD')]) {
                        bat 'python backend_testing.py -u ${DB_USER_NAME} -p ${DB_PASSWORD}'
                    }
                }
            }
        }

        // Step 5 - Run Frontend Test //
        stage("Run `frontend_testing.py` (Testing)") {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'DB_USER_NAME', passwordVariable: 'DB_PASSWORD')]) {
                        bat 'python frontend_testing.py -u ${DB_USER_NAME} -p ${DB_PASSWORD}'
                    }
                }
            }
        }

        // Step 6 - Run Combined Test //
        stage("Run `combined_testing.py` (Testing)") {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'DB_USER_NAME', passwordVariable: 'DB_PASSWORD')]) {
                        bat 'python combined_testing.py -u ${DB_USER_NAME} -p ${DB_PASSWORD}'
                    }
                }
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