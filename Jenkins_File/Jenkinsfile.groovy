pipeline {
    agent any

    parameters {
        choice(name: 'User_Choice', choices: ['1', '2', '3'], description: "The ${User} need to choose a number : \n" + "1 - In case the int value is 1 – only frontend_testing.py will run.\n 2 - In case the int value is 2 – only backend_testing.py will run.\n 3 - In case the int value is 3 – only combined_testing.py will run.\n")
    }
    stages {
        // Step 1 - Clone Git From GitHub //
        // Note   - This section is deprecated because of the 'Extra' section //
        /*
        stage("Clone Git") {
            steps {
                script {
                    properties([pipelineTriggers([pollSCM('H/30 * * * *')])])
                }
                git "https://github.com/DinGolan/DevOps-Experts-Final-Project.git"
            }
        }
        */

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

        // Step 4 - Run Testings //
        stage("Testing") {
            steps {
                script {
                    if (User_Choice == '1') {
                        bat 'echo Run `backend_testing.py` (Testing)'
                        bat 'python backend_testing.py'
                    } else if (User_Choice == '2') {
                        bat 'echo Run `frontend_testing.py` (Testing)'
                        bat 'python frontend_testing.py'
                    } else if (User_Choice == '3') {
                        bat 'echo Run `combined_testing.py` (Testing)'
                        bat 'python combined_testing.py'
                    }
                }

            }
        }

        // Step 5 - Run Clean Environment //
        stage("Run `clean_environment.py` (Clean)") {
            steps {
                bat 'python clean_environment.py'
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