/* Pipeline */
pipeline {
    agent any

    // Log Rotator //
    options {
        buildDiscarder(logRotator(daysToKeepStr: '5', numToKeepStr: '20'))
    }

    stages {
        // Step 1 - Clone Git From GitHub //
        stage("Clone Git") {
            steps {
                script {
                    properties([pipelineTriggers([pollSCM('H/30 * * * *')])])
                }
                git  credentialsId: 'github_credentials', url: 'https://github.com/DinGolan/DevOps-Experts-Final-Project.git', branch: 'main'
            }
        }

        // Step 2 - Install Pip Packages //
        stage("Run `pip install`") {
            steps {
                script {
                    if (checkPackages() == "Already Exists") {
                        echo '[pymysql, requests, selenium, flask, prettytable, pypika, psutil] - Already Exist ...'
                    } else {
                        if (checkOS() == "Windows") {
                            bat 'pip install --ignore-installed pymysql requests selenium flask prettytable pypika psutil'
                        } else {
                            sh 'pip install --ignore-installed pymysql requests selenium flask prettytable pypika psutil'
                        }
                    }
                }
            }
        }

        // Step 3 - Run REST API //
        stage("Run `rest_app.py` (Backend)") {
            steps {
                script {
                    if (checkOS() == "Windows") {
                        withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'DB_USER_NAME', passwordVariable: 'DB_PASSWORD')]) {
                            bat 'start /min python REST_API\\rest_app.py -u %DB_USER_NAME% -p %DB_PASSWORD%'
                        }
                    } else {
                        withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'DB_USER_NAME', passwordVariable: 'DB_PASSWORD')]) {
                            sh 'start /min python REST_API\\rest_app.py -u %DB_USER_NAME% -p %DB_PASSWORD%'
                        }
                    }
                }
            }
        }

        // Step 4 - Run WEB APP  //
        stage("Run `web_app.py` (Frontend)") {
            steps {
                script {
                    if (checkOS() == "Windows") {
                        withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'DB_USER_NAME', passwordVariable: 'DB_PASSWORD')]) {
                            bat 'start /min python Web_Interface\\web_app.py -u %DB_USER_NAME% -p %DB_PASSWORD%'
                        }
                    } else {
                        withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'DB_USER_NAME', passwordVariable: 'DB_PASSWORD')]) {
                            sh 'start /min python Web_Interface\\web_app.py -u %DB_USER_NAME% -p %DB_PASSWORD%'
                        }
                    }
                }
            }
        }

        // Step 5 - Run Backend Test //
        stage("Run `backend_testing.py` (Testing)") {
            steps {
                script {
                    if (checkOS() == "Windows") {
                        withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'DB_USER_NAME', passwordVariable: 'DB_PASSWORD')]) {
                            bat 'python Testing\\backend_testing.py -u %DB_USER_NAME% -p %DB_PASSWORD% -i %IS_JOB_RUN% -r %REQUEST_TYPE%'
                        }
                    } else {
                        withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'DB_USER_NAME', passwordVariable: 'DB_PASSWORD')]) {
                            sh 'python Testing\\backend_testing.py -u %DB_USER_NAME% -p %DB_PASSWORD% -i %IS_JOB_RUN% -r %REQUEST_TYPE%'
                        }
                    }
                }
            }
        }

        // Step 6 - Run Frontend Test //
        stage("Run `frontend_testing.py` (Testing)") {
            steps {
                script {
                    if (checkOS() == "Windows") {
                        withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'DB_USER_NAME', passwordVariable: 'DB_PASSWORD')]) {
                            bat 'python Testing\\frontend_testing.py -u %DB_USER_NAME% -p %DB_PASSWORD% -i %IS_JOB_RUN%'
                        }
                    } else {
                        withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'DB_USER_NAME', passwordVariable: 'DB_PASSWORD')]) {
                            sh 'python Testing\\frontend_testing.py -u %DB_USER_NAME% -p %DB_PASSWORD% -i %IS_JOB_RUN%'
                        }
                    }
                }
            }
        }

        // Step 7 - Run Combined Test //
        stage("Run `combined_testing.py` (Testing)") {
            steps {
                script {
                    if (checkOS() == "Windows") {
                        withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'DB_USER_NAME', passwordVariable: 'DB_PASSWORD')]) {
                            bat 'python Testing\\combined_testing.py -u %DB_USER_NAME% -p %DB_PASSWORD% -i %IS_JOB_RUN% -r %REQUEST_TYPE% -t %TEST_SIDE%'
                        }
                    } else {
                        withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'DB_USER_NAME', passwordVariable: 'DB_PASSWORD')]) {
                            sh 'python Testing\\combined_testing.py -u %DB_USER_NAME% -p %DB_PASSWORD% -i %IS_JOB_RUN% -r %REQUEST_TYPE% -t %TEST_SIDE%'
                        }
                    }
                }
            }
        }

        // Step 8 - Run Clean Environment //
        stage("Run `clean_environment.py` (Clean)") {
            steps {
                script {
                    if (checkOS() == "Windows") {
                        withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'DB_USER_NAME', passwordVariable: 'DB_PASSWORD')]) {
                            bat 'python Clean\\clean_environment.py -u %DB_USER_NAME% -p %DB_PASSWORD% -i %IS_JOB_RUN%'
                        }
                    } else {
                        withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'DB_USER_NAME', passwordVariable: 'DB_PASSWORD')]) {
                            sh 'python Clean\\clean_environment.py -u %DB_USER_NAME% -p %DB_PASSWORD% -i %IS_JOB_RUN%'
                        }
                    }
                }
            }
        }
    }
}

/* Functions */
String checkPackages() {

    /* Vars */
    def installed_packages

    if (checkOS() == "Windows") {
        installed_packages = bat(script: 'pip freeze', returnStdout: true).trim().readLines().drop(1).join(" ")
    } else {
        installed_packages = sh(script: 'pip freeze', returnStdout: true).trim().readLines().drop(1).join(" ")
    }
    echo "installed_packages :\n${installed_packages}"

    if (installed_packages.contains('PyMySQL') && installed_packages.contains('requests') && installed_packages.contains('selenium') && installed_packages.contains('Flask') && installed_packages.contains('prettytable') && installed_packages.contains('PyPika') && installed_packages.contains('psutil')) {
        return "Already Exists"
    } else {
        return "Not Exist"
    }
}

def checkOS() {
    if (isUnix()) {
        def uname = sh script: 'uname', returnStdout: true
        if (uname.startsWith("Darwin")) {
            return "Macos"
        } else {
            return "Linux"
        }
    } else {
        return "Windows"
    }
}