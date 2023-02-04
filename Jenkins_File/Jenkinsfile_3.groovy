/* Pipeline */
pipeline {
    agent any

    // Log Rotator //
    options {
        buildDiscarder(logRotator(daysToKeepStr: '5', numToKeepStr: '20'))
    }

    // Environments //
    environment {
        DOCKER_REPOSITORY   = "dingolan/devops_experts_final_project"
        DOCKER_COMPOSE_FILE = "docker-compose.yml"
        DB_TAG              = "db_app_version_"
        PY_TAG              = "py_app_version_"
        MYSQL_SCHEMA_NAME   = "freedb_Din_Golan"
    }

    stages {
        // Step 1 - Clone Git From GitHub //
        stage("Clone Git") {
            steps {
                script {
                    properties([pipelineTriggers([pollSCM('H/30 * * * *')])])
                }
                git  credentialsId: "github_credentials", url: "https://github.com/DinGolan/DevOps-Experts-Final-Project.git", branch: 'main'
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
                            bat 'python -m pip install --ignore-installed --trusted-host pypi.python.org -r Packages\\requirements.txt'
                        } else {
                            sh '/usr/local/bin/python -m pip install --ignore-installed --trusted-host pypi.python.org -r Packages/requirements.txt'
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
                            sh 'start /min python REST_API/rest_app.py -u ${DB_USER_NAME} -p ${DB_PASSWORD}'
                        }
                    }
                }
            }
        }

        // Step 4 - Run Backend Test //
        stage("Run `backend_testing.py` (Testing)") {
            steps {
                script {
                    if (checkOS() == "Windows") {
                        withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'DB_USER_NAME', passwordVariable: 'DB_PASSWORD')]) {
                            bat 'python Testing\\backend_testing.py -u %DB_USER_NAME% -p %DB_PASSWORD% -i %IS_JOB_RUN% -r %REQUEST_TYPE%'
                        }
                    } else {
                        withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'DB_USER_NAME', passwordVariable: 'DB_PASSWORD')]) {
                            sh 'python Testing/backend_testing.py -u ${DB_USER_NAME} -p ${DB_PASSWORD} -i ${IS_JOB_RUN} -r ${REQUEST_TYPE}'
                        }
                    }
                }
            }
        }

        // Step 5 - Run Clean Environment //
        stage("Run `clean_environment.py` (Clean)") {
            steps {
                script {
                    if (checkOS() == "Windows") {
                        withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'DB_USER_NAME', passwordVariable: 'DB_PASSWORD')]) {
                            bat 'python Clean\\clean_environment.py -u %DB_USER_NAME% -p %DB_PASSWORD% -i %IS_JOB_RUN%'
                        }
                    } else {
                        withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'DB_USER_NAME', passwordVariable: 'DB_PASSWORD')]) {
                            sh 'python Clean/clean_environment.py -u ${DB_USER_NAME} -p ${DB_PASSWORD} -i ${IS_JOB_RUN}'
                        }
                    }
                }
            }
        }

        // Step 6 - Update `.env` File //
        stage("Update `.env` File") {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'DB_USER_NAME', passwordVariable: 'DB_PASSWORD')]) {
                        setEnvFile()
                    }
                }
            }
        }

        // Step 7 - Login to Docker Hub //
        stage("Login to Docker Hub") {
            steps {
                script {
                    if (checkOS() == "Windows") {
                        withCredentials([usernamePassword(credentialsId: 'docker_hub', passwordVariable: 'DOCKER_HUB_PASSWORD', usernameVariable: 'DOCKER_HUB_USERNAME')]) {
                            bat 'docker login --username "%DOCKER_HUB_PASSWORD%" --password "%DOCKER_HUB_USERNAME%"'
                        }
                    } else {
                        withCredentials([usernamePassword(credentialsId: 'docker_hub', passwordVariable: 'DOCKER_HUB_PASSWORD', usernameVariable: 'DOCKER_HUB_USERNAME')]) {
                            sh 'docker login --username "${DOCKER_HUB_PASSWORD}" --password "${DOCKER_HUB_USERNAME}"'
                        }
                    }
                }
            }
        }

        // Step 8 - Build Docker Compose YAML File //
        stage("Build Docker Compose") {
            steps {
                script {
                    if (checkOS() == "Windows") {
                        bat 'docker-compose --env-file .env --file Dockerfiles\\%DOCKER_COMPOSE_FILE% build'
                    } else {
                        sh 'docker-compose --env-file .env --file Dockerfiles/${DOCKER_COMPOSE_FILE} build'
                    }
                }
            }
        }

        // Step 9 - Push Docker Compose //
        stage("Push Docker Compose") {
            steps {
                script {
                    if (checkOS() == "Windows") {
                        bat 'docker-compose --env-file .env --file Dockerfiles\\%DOCKER_COMPOSE_FILE% push'
                    } else {
                        sh 'docker-compose --env-file .env --file Dockerfiles/${DOCKER_COMPOSE_FILE} push'
                    }
                }
            }
        }

        // Step 10 - Run Docker Compose //
        stage("Run Docker Compose") {
            steps {
                script {
                    if (checkOS() == "Windows") {
                        bat 'docker-compose --env-file .env --file Dockerfiles\\%DOCKER_COMPOSE_FILE% up -d'
                    } else {
                        sh 'docker-compose --env-file .env --file Dockerfiles/${DOCKER_COMPOSE_FILE} up -d'
                    }
                }
            }
        }

        // Step 11 - Clean & Remove Docker Images Build & Push //
        post {
            always {
                if (checkOS() == "Windows") {
                    bat 'docker-compose --file Dockerfiles\\%DOCKER_COMPOSE_FILE% down --volumes'
                    bat 'docker rmi -f %DOCKER_REPOSITORY%:%DB_TAG%%BUILD_NUMBER%'
                    bat 'docker rmi -f %DOCKER_REPOSITORY%:%PY_TAG%%BUILD_NUMBER%'
                } else {
                    sh 'docker-compose --file Dockerfiles/${DOCKER_COMPOSE_FILE} down --volumes'
                    sh 'docker rmi -f ${DOCKER_REPOSITORY}:${DB_TAG}${BUILD_NUMBER}'
                    sh 'docker rmi -f ${DOCKER_REPOSITORY}:${PY_TAG}${BUILD_NUMBER}'
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

def setEnvFile() {
    if (checkOs() == 'Windows') {
        bat 'echo BUILD_NUMBER=%BUILD_NUMBER% > .env'
        bat 'echo PY_TAG=%PY_TAG% >> .env'
        bat 'echo MYSQL_SCHEMA_NAME=%MYSQL_SCHEMA_NAME% >> .env'
        bat 'echo MYSQL_USER_NAME=%DB_USER_NAME% >> .env'
        bat 'echo MYSQL_PASSWORD=%DB_PASSWORD% >> .env'
    } else {
        sh 'echo BUILD_NUMBER=${BUILD_NUMBER} > .env'
        sh 'echo PY_TAG=${PY_TAG} >> .env'
        sh 'echo MYSQL_DATABASE=${MYSQL_DATABASE} >> .env'
        sh 'echo MYSQL_USER_NAME=${DB_USER_NAME} >> .env'
        sh 'echo MYSQL_PASSWORD=${DB_PASSWORD} >> .env'
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
