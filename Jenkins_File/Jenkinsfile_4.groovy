/* Imports */
import groovy.json.JsonSlurper

/* Pipeline */
pipeline {
    agent any

    // Log Rotator //
    options {
        buildDiscarder(logRotator(daysToKeepStr: '5', numToKeepStr: '20'))
    }

    // Environments //
    environment {
        DOCKER_REPOSITORY                     = "dingolan/devops_experts_final_project"
        DOCKER_COMPOSE_FILE                   = "docker-compose-2.yml"
        MYSQL_SCHEMA_NAME                     = "freedb_Din_Golan"
        MYSQL_CONTAINER_NAME                  = "mysql_container"
        REST_CONTAINER_NAME                   = "rest_api_container"
        DOCKER_BACKEND_TESTING_CONTAINER_NAME = "docker_backend_testing_container"
        REST_HOST_NAME                        = "rest_api"
        DOCKER_BACKEND_TESTING_HOST_NAME      = "docker_backend_testing"
        IMAGE_TAG_1                           = "latest_1"
        IMAGE_TAG_2                           = "latest_2"
        MYSQL_TAG                             = "8.0.32"
        REST_TAG                              = "rest_api_version_"
        PY_TAG                                = "python_app_version_"
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
                            sh "/usr/local/bin/python -m pip install --ignore-installed --trusted-host pypi.python.org -r Packages/requirements.txt"
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
                        withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'MYSQL_USER_NAME', passwordVariable: 'MYSQL_PASSWORD')]) {
                            bat 'start /min python REST_API\\rest_app.py -u %MYSQL_USER_NAME% -p %MYSQL_PASSWORD%'
                        }
                    } else {
                        withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'MYSQL_USER_NAME', passwordVariable: 'MYSQL_PASSWORD')]) {
                            sh "start /min python REST_API/rest_app.py -u ${MYSQL_USER_NAME} -p ${MYSQL_PASSWORD}"
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
                        withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'MYSQL_USER_NAME', passwordVariable: 'MYSQL_PASSWORD')]) {
                            bat 'python Testing\\backend_testing.py -u %MYSQL_USER_NAME% -p %MYSQL_PASSWORD% -i %IS_JOB_RUN% -r %REQUEST_TYPE%'
                        }
                    } else {
                        withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'MYSQL_USER_NAME', passwordVariable: 'MYSQL_PASSWORD')]) {
                            sh "python Testing/backend_testing.py -u ${MYSQL_USER_NAME} -p ${MYSQL_PASSWORD} -i ${IS_JOB_RUN} -r ${REQUEST_TYPE}"
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
                        withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'MYSQL_USER_NAME', passwordVariable: 'MYSQL_PASSWORD')]) {
                            bat 'python Clean\\clean_environment.py -u %MYSQL_USER_NAME% -p %MYSQL_PASSWORD% -i %IS_JOB_RUN% -c %CLEAN_SERVER%'
                        }
                    } else {
                        withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'MYSQL_USER_NAME', passwordVariable: 'MYSQL_PASSWORD')]) {
                            sh "python Clean/clean_environment.py -u ${MYSQL_USER_NAME} -p ${MYSQL_PASSWORD} -i ${IS_JOB_RUN} -c ${CLEAN_SERVER}"
                        }
                    }
                }
            }
        }

        // Step 6 - Update `.env` File //
        stage("Update `.env` File") {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'docker_database_credentials', usernameVariable: 'MYSQL_ROOT_USER', passwordVariable: 'MYSQL_ROOT_PASSWORD'),
                                     usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'MYSQL_USER_NAME', passwordVariable: 'MYSQL_PASSWORD')]) {
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
                        withCredentials([usernamePassword(credentialsId: 'docker_hub', usernameVariable: 'DOCKER_HUB_USERNAME', passwordVariable: 'DOCKER_HUB_PASSWORD')]) {
                            bat 'docker login --username "%DOCKER_HUB_USERNAME%" --password "%DOCKER_HUB_PASSWORD%"'
                        }
                    } else {
                        withCredentials([usernamePassword(credentialsId: 'docker_hub', usernameVariable: 'DOCKER_HUB_USERNAME', passwordVariable: 'DOCKER_HUB_PASSWORD')]) {
                            sh "docker login --username ${DOCKER_HUB_USERNAME} --password ${DOCKER_HUB_PASSWORD}"
                        }
                    }
                }
            }
        }

        // Step 8 - Build & Up Docker Compose //
        stage("Build & Up Docker Compose") {
            steps {
                script {
                    if (checkOS() == "Windows") {
                        bat 'docker-compose --env-file .env --file Dockerfiles\\%DOCKER_COMPOSE_FILE% up -d --build & docker ps -a'
                    } else {
                        sh "docker-compose --env-file .env --file Dockerfiles/${DOCKER_COMPOSE_FILE} up -d --build & docker ps -a"
                    }
                    sleep(time: 10, unit: "SECONDS")
                }
            }
        }

        // Step 9 - Push Docker Compose //
        /*
         stage("Push Docker Compose") {
             steps {
                 script {
                     if (checkOS() == "Windows") {
                         bat 'docker-compose --env-file .env --file Dockerfiles\\%DOCKER_COMPOSE_FILE% push'
                     } else {
                         sh "docker-compose --env-file .env --file Dockerfiles/${DOCKER_COMPOSE_FILE} push"
                     }
                 }
             }
         }
         */

        // Step 10 - Check Docker Service Healthy //
        stage("Check Docker Compose Services Health") {
            steps {
                script {
                    if (checkOS() == "Windows") {
                        def servicesOutput = bat(script: 'docker-compose --env-file .env --file Dockerfiles\\%DOCKER_COMPOSE_FILE% ps --services', returnStdout: true).trim().readLines().drop(1)
                        for (def service : servicesOutput) {
                            def containers = bat(script: "docker-compose --env-file .env --file Dockerfiles\\%DOCKER_COMPOSE_FILE% ps -q --services ${service}", returnStdout: true).trim().readLines().drop(1)
                            for (def container : containers) {
                                def inspectStateStatusOutput = bat(script: "docker inspect ${container} --format '{{.State.Status}}'", returnStdout: true).trim().readLines().drop(1).join(" ").replaceAll("\'","")
                                def inspectHealthStatusOutput = bat(script: "docker inspect ${container} --format '{{.State.Health.Status}}'", returnStdout: true).trim().readLines().drop(1).join(" ").replaceAll("\'","")
                                if (inspectStateStatusOutput != "running" || inspectStateStatusOutput == null || inspectStateStatusOutput == "") {
                                    error("Container id: ${container} from Service name: ${service} Has State status: ${inspectStateStatusOutput}")
                                    return
                                } else if (inspectHealthStatusOutput != "healthy" || inspectHealthStatusOutput == null || inspectHealthStatusOutput == "") {
                                    error("Service ${service} is not healthy. Container id: ${container} has health status: ${inspectHealthStatusOutput}")
                                    return
                                } else {
                                    echo "Service name : ${service} is in state : ${inspectStateStatusOutput} , Container id : ${container} has health status : ${inspectHealthStatusOutput}"
                                }
                            }
                        }
                    } else {
                        def servicesOutput = sh(script: "docker-compose --env-file .env --file Dockerfiles/${DOCKER_COMPOSE_FILE} ps --services", returnStdout: true).trim().readLines().drop(1)
                        for (def service : servicesOutput) {
                            def containers = sh(script: "docker-compose --env-file .env --file Dockerfiles/${DOCKER_COMPOSE_FILE} ps -q --services ${service}", returnStdout: true).trim().readLines().drop(1)
                            for (def container : containers) {
                                def inspectStateStatusOutput = sh(script: "docker inspect ${container} --format '{{.State.Status}}'", returnStdout: true).trim().readLines().drop(1).join(" ").replaceAll("\'","")
                                def inspectHealthStatusOutput = sh(script: "docker inspect ${container} --format '{{.State.Health.Status}}'", returnStdout: true).trim().readLines().drop(1).join(" ").replaceAll("\'","")
                                if (inspectStateStatusOutput != "running" || inspectStateStatusOutput == null) {
                                    error("Container id: ${container} from Service name: ${service} Has State status: ${inspectStateStatusOutput}")
                                    return
                                } else if (inspectHealthStatusOutput != "healthy" || inspectHealthStatusOutput == null) {
                                    error("Service ${service} is not healthy. Container id: ${container} has health status: ${inspectHealthStatusOutput}")
                                    return
                                } else {
                                    echo "Service name : ${service} is in state : ${inspectStateStatusOutput} , Container id : ${container} has health status : ${inspectHealthStatusOutput}"
                                }
                            }
                        }
                    }
                }
            }
        }

        // Step 11 - Docker App - Stop Flask Servers - Option 1 //
        stage("[Docker] Docker App - Stop Flask Servers") {
            steps {
                script {
                    if (checkOS() == "Windows") {
                        def containerId = bat(script: 'docker ps --filter "name=%REST_CONTAINER_NAME%" --format "{{.ID}}"', returnStdout: true).trim().readLines().drop(1).join(" ")
                        sleep(time: 2, unit: "SECONDS")
                        withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'DB_USER_NAME', passwordVariable: 'DB_PASSWORD')]) {
                            bat "docker exec -i ${containerId} sh -c \"curl -i -m 60 http://127.0.0.1:5000/stop_server \""
                        }
                    } else {
                        def containerId = sh(script: 'docker ps --filter "name=${REST_CONTAINER_NAME}" --format "{{.ID}}"', returnStdout: true).trim().readLines().drop(1).join(" ")
                        sleep(time: 2, unit: "SECONDS")
                        withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'DB_USER_NAME', passwordVariable: 'DB_PASSWORD')]) {
                            sh "docker exec -i ${containerId} sh \"curl -i -m 60 http://127.0.0.1:5000/stop_server\""
                        }
                    }
                }
            }
        }

        // Step 11 - Docker App - Stop Flask Servers - Option 2 //
        /*
        stage("[Docker] Run `clean_environment.py` (Clean)") {
            steps {
                script {
                    if (checkOS() == "Windows") {
                        def containerId = bat(script: 'docker ps --filter "name=%REST_CONTAINER_NAME%" --format "{{.ID}}"', returnStdout: true).trim().readLines().drop(1).join(" ")
                        sleep(time: 2, unit: "SECONDS")
                        withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'DB_USER_NAME', passwordVariable: 'DB_PASSWORD')]) {
                            bat "docker exec -i ${containerId} sh -c \"/usr/local/bin/python Clean/clean_environment.py -u %DB_USER_NAME% -p %DB_PASSWORD% -i %IS_JOB_RUN% -c %CLEAN_SERVER%\""
                        }
                    } else {
                        def containerId = sh(script: 'docker ps --filter "name=${REST_CONTAINER_NAME}" --format "{{.ID}}"', returnStdout: true).trim().readLines().drop(1).join(" ")
                        sleep(time: 2, unit: "SECONDS")
                        withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'DB_USER_NAME', passwordVariable: 'DB_PASSWORD')]) {
                           sh "docker exec -i ${containerId} sh \"/usr/local/bin/python Clean/clean_environment.py -u ${DB_USER_NAME} -p ${DB_PASSWORD} -i ${IS_JOB_RUN} -c ${CLEAN_SERVER}\""
                        }
                    }
                }
            }
        }
        */


        // Step 12 - Clean & Remove Docker Images Build & Push //
        stage ('Clean Docker Environment') {
            steps {
                script {
                    if (checkOS() == "Windows") {
                        bat 'docker-compose --file Dockerfiles\\%DOCKER_COMPOSE_FILE% down --rmi all --volumes'
                    } else {
                        sh "docker-compose --file Dockerfiles/${DOCKER_COMPOSE_FILE} down --rmi all --volumes"
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
        installed_packages = sh(script: "pip freeze", returnStdout: true).trim().readLines().drop(1).join(" ")
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

def setEnvFile() {
    // Note - We can write also the following IMAGE_TAG : IMAGE_TAG=%BUILD_NUMBER% / IMAGE_TAG=${BUILD_NUMBER} //
    if (checkOS() == 'Windows') {
        bat 'echo MYSQL_ROOT_USER=%MYSQL_ROOT_USER%                                              > .env'
        bat 'echo MYSQL_ROOT_PASSWORD=%MYSQL_ROOT_PASSWORD%                                     >> .env'
        bat 'echo MYSQL_USER_NAME=%MYSQL_USER_NAME%                                             >> .env'
        bat 'echo MYSQL_PASSWORD=%MYSQL_PASSWORD%                                               >> .env'
        bat 'echo MYSQL_SCHEMA_NAME=%MYSQL_SCHEMA_NAME%                                         >> .env'
        bat 'echo MYSQL_CONTAINER_NAME=%MYSQL_CONTAINER_NAME%                                   >> .env'
        bat 'echo REST_CONTAINER_NAME=%REST_CONTAINER_NAME%                                     >> .env'
        bat 'echo DOCKER_BACKEND_TESTING_CONTAINER_NAME=%DOCKER_BACKEND_TESTING_CONTAINER_NAME% >> .env'
        bat 'echo REST_HOST_NAME=%REST_HOST_NAME%                                               >> .env'
        bat 'echo DOCKER_BACKEND_TESTING_HOST_NAME=%DOCKER_BACKEND_TESTING_HOST_NAME%           >> .env'
        bat 'echo IMAGE_TAG_1=%IMAGE_TAG_1%                                                     >> .env'
        bat 'echo IMAGE_TAG_2=%IMAGE_TAG_2%                                                     >> .env'
        bat 'echo MYSQL_TAG=%MYSQL_TAG%                                                         >> .env'
        bat 'echo REST_TAG=%REST_TAG%                                                           >> .env'
        bat 'echo PY_TAG=%PY_TAG%                                                               >> .env'
    } else {
        sh 'echo MYSQL_ROOT_USER=${MYSQL_ROOT_USER}                                              > .env'
        sh 'echo MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}                                     >> .env'
        sh 'echo MYSQL_USER_NAME=${MYSQL_USER_NAME}                                             >> .env'
        sh 'echo MYSQL_PASSWORD=${MYSQL_PASSWORD}                                               >> .env'
        sh 'echo MYSQL_SCHEMA_NAME=${MYSQL_SCHEMA_NAME}                                         >> .env'
        sh 'echo MYSQL_CONTAINER_NAME=${MYSQL_CONTAINER_NAME}                                   >> .env'
        sh 'echo REST_CONTAINER_NAME=${REST_CONTAINER_NAME}                                     >> .env'
        sh 'echo DOCKER_BACKEND_TESTING_CONTAINER_NAME=${DOCKER_BACKEND_TESTING_CONTAINER_NAME} >> .env'
        sh 'echo REST_HOST_NAME=${REST_HOST_NAME}                                               >> .env'
        sh 'echo DOCKER_BACKEND_TESTING_HOST_NAME=${DOCKER_BACKEND_TESTING_HOST_NAME}           >> .env'
        sh 'echo IMAGE_TAG_1=${IMAGE_TAG_1}                                                     >> .env'
        sh 'echo IMAGE_TAG_2=${IMAGE_TAG_2}                                                     >> .env'
        sh 'echo MYSQL_TAG=${MYSQL_TAG}                                                         >> .env'
        sh 'echo REST_TAG=${REST_TAG}                                                           >> .env'
        sh 'echo PY_TAG=${PY_TAG}                                                               >> .env'
    }
}