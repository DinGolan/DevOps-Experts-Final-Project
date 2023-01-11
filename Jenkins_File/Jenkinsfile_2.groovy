pipeline {
    agent any

    stages {
        // Step 1 - Clone Git From GitHub //
        stage("Clone Git") {
            steps {
                git  credentialsId: "github_credentials", url: "https://github.com/DinGolan/DevOps-Experts-Final-Project.git"
            }
        }

        // Step 2 - Install Pip Packages //
        stage("Run `pip install`") {
            steps {
                script {
                    bat 'pip install --ignore-installed pymysql requests selenium flask prettytable pypika psutil'
                }
            }
        }

        // Step 3 - Run REST API //
        stage("Run `rest_app.py` (Backend)") {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'DB_USER_NAME', passwordVariable: 'DB_PASSWORD')]) {
                        bat 'start /min python REST_API\\rest_app.py -u ${DB_USER_NAME} -p ${DB_PASSWORD}'
                    }
                }
            }
        }

        // Step 4 - Run WEB APP  //
        stage("Run `web_app.py` (Frontend)") {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'DB_USER_NAME', passwordVariable: 'DB_PASSWORD')]) {
                        bat 'start /min Web_Interface\\python web_app.py -u ${DB_USER_NAME} -p ${DB_PASSWORD}'
                    }
                }
            }
        }

        // Step 5 - Run Testings //
        stage("Testing") {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'DB_USER_NAME', passwordVariable: 'DB_PASSWORD')]) {
                        if (${User_Choice} == '1') {
                            bat 'echo Run `backend_testing.py` (Testing)'
                            bat 'python Testing\\backend_testing.py -u ${DB_USER_NAME} -p ${DB_PASSWORD} -i ${IS_JOB_RUN} -r ${REQUEST_TYPE}'
                        } else if (${User_Choice} == '2') {
                            bat 'echo Run `frontend_testing.py` (Testing)'
                            bat 'python Testing\\frontend_testing.py -u ${DB_USER_NAME} -p ${DB_PASSWORD} -i ${IS_JOB_RUN}'
                        } else if (${User_Choice} == '3') {
                            bat 'echo Run `combined_testing.py` (Testing)'
                            bat 'python Testing\\combined_testing.py -u ${DB_USER_NAME} -p ${DB_PASSWORD} -i ${IS_JOB_RUN} -r ${REQUEST_TYPE} -t ${TEST_SIDE}'
                        } else {
                            bat 'echo \'User_Choice\' must to be between - [1, 2, 3]'
                        }
                    }
                }
            }
        }

        // Step 6 - Run Clean Environment //
        stage("Run `clean_environment.py` (Clean)") {
            steps {
                bat 'python Clean\\clean_environment.py -i ${IS_JOB_RUN}'
            }
        }
    }

    // Step - Sending Mail //
    // Note - This section is not supported because I've Two Factor Authentication Gmail //
    /*
    post {
        failure {
            mail to: "dingolan100@gmail.com",
            subject: "DevOps Experts - Final Project - Updates",
            body: "${currentBuild.currentResult} : Job ${env.JOB_NAME}\nMore Info can be found here : ${env.BUILD_URL}\n"
            attachLog: true
        }
    }
    */
}
