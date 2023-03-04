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
        DOCKER_COMPOSE_FILE_1                 = "docker-compose-1.yml"
        DOCKER_COMPOSE_FILE_3                 = "docker-compose-3.yml"
        MYSQL_SCHEMA_NAME                     = "freedb_Din_Golan_Container"
        MYSQL_HOST_PORT                       = 3306
        MYSQL_GUEST_PORT                      = 3306
        MYSQL_CONTAINER_NAME                  = "mysql_container"
        REST_CONTAINER_NAME                   = "rest_api_container"
        DOCKER_BACKEND_TESTING_CONTAINER_NAME = "docker_backend_testing_container"
        MYSQL_HOST_NAME                       = "database"
        MYSQL_REMOTE_HOST_NAME                = "sql.freedb.tech"
        REST_HOST_NAME                        = "rest_api"
        DOCKER_BACKEND_TESTING_HOST_NAME      = "docker_backend_testing"
        IMAGE_TAG_1                           = "latest_1"
        IMAGE_TAG_2                           = "latest_2"
        IMAGE_TAG_3                           = "latest_3"
        MYSQL_TAG                             = "8.0.32"
        REST_TAG                              = "rest_api_version_"
        PY_TAG                                = "python_app_version_"
        REST_API_SERVICE_NAME                 = "rest-api-application-service"
        HELM_CHART_NAME                       = "helm-chart-testing"
        K8S_URL_FILE                          = "k8s_url.txt"
    }

    stages {
        // Step 1 - Clone Git From GitHub //
        stage("[Backend] Clone Git") {
            steps {
                script {
                    properties([pipelineTriggers([pollSCM('H/30 * * * *')])])
                }
                git  credentialsId: "github_credentials", url: "https://github.com/DinGolan/DevOps-Experts-Final-Project.git", branch: 'main'
            }
        }

        // Step 2 - Install Pip Packages //
        stage("[Backend] Run `pip install`") {
            steps {
                script {
                    if (checkPackages() == "Already Exists") {
                        echo '[pymysql, requests, selenium, flask, prettytable, pypika, psutil] - Already Exist ...'
                    } else {
                        if (checkOS() == "Windows") {
                            bat 'python -m pip install --ignore-installed --trusted-host pypi.python.org -r Packages\\requirements.txt'
                        } else {
                            sh "python -m pip install --ignore-installed --trusted-host pypi.python.org -r Packages/requirements.txt"
                        }
                    }
                }
            }
        }

        // Step 3 - Run REST API //
        stage("[Backend] Run `rest_app.py` (Backend)") {
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
        stage("[Backend] Run `backend_testing.py` (Testing)") {
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
        stage("[Backend] Run `clean_environment.py` (Clean)") {
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
        stage("[Docker] Update `.env` File") {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'container_root_database_credentials', usernameVariable: 'MYSQL_ROOT_USER', passwordVariable: 'MYSQL_ROOT_PASSWORD'),
                                     usernamePassword(credentialsId: 'container_database_credentials', usernameVariable: 'MYSQL_USER_NAME', passwordVariable: 'MYSQL_PASSWORD')]) {
                        setEnvFile()
                    }
                }
            }
        }

        // Step 7 - Login to Docker Hub //
        stage("[Docker] Login to Docker Hub") {
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
        stage("[Docker] Build & Up Docker Compose") {
            steps {
                script {
                    if (checkOS() == "Windows") {
                        bat 'docker-compose --env-file .env --file Dockerfiles\\%DOCKER_COMPOSE_FILE_1% up -d --build & docker ps -a'
                    } else {
                        sh "docker-compose --env-file .env --file Dockerfiles/${DOCKER_COMPOSE_FILE_1} up -d --build & docker ps -a"
                    }
                    sleep(time: 10, unit: "SECONDS")
                }
            }
        }

        // Step 9 - Push Docker Compose //
        stage("[Docker] Push Docker Compose") {
            steps {
                script {
                    if (checkOS() == "Windows") {
                        bat 'docker-compose --env-file .env --file Dockerfiles\\%DOCKER_COMPOSE_FILE_1% push'
                    } else {
                        sh "docker-compose --env-file .env --file Dockerfiles/${DOCKER_COMPOSE_FILE_1} push"
                    }
                }
            }
        }

        // Step 10 - Check Docker Service Healthy //
        stage("[Docker] Check Docker Compose Services Health") {
            steps {
                script {
                    if (checkOS() == "Windows") {
                        def servicesOutput = bat(script: 'docker-compose --env-file .env --file Dockerfiles\\%DOCKER_COMPOSE_FILE_1% ps --services', returnStdout: true).trim().readLines().drop(1)
                        for (def service : servicesOutput) {
                            def containers = bat(script: "docker-compose --env-file .env --file Dockerfiles\\%DOCKER_COMPOSE_FILE_1% ps -q --services ${service}", returnStdout: true).trim().readLines().drop(1)
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
                        def servicesOutput = sh(script: 'docker-compose --env-file .env --file Dockerfiles/${DOCKER_COMPOSE_FILE_1} ps --services', returnStdout: true).trim().readLines().drop(1)
                        for (def service : servicesOutput) {
                            def containers = sh(script: "docker-compose --env-file .env --file Dockerfiles/${DOCKER_COMPOSE_FILE_1} ps -q --services ${service}", returnStdout: true).trim().readLines().drop(1)
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

        // Step 11 - Run Backend Test (On Docker Compose Environments) //
        stage("[Docker] Run `docker_backend_testing.py` (Testing Docker Compose)") {
            steps {
                script {
                    if (checkOS() == "Windows") {
                        def containerId = bat(script: 'docker ps --filter "name=%REST_CONTAINER_NAME%" --format "{{.ID}}"', returnStdout: true).trim().readLines().drop(1).join(" ")
                        sleep(time: 2, unit: "SECONDS")
                        withCredentials([usernamePassword(credentialsId: 'container_database_credentials', usernameVariable: 'MYSQL_USER_NAME', passwordVariable: 'MYSQL_PASSWORD')]) {
                            bat "docker exec -i ${containerId} sh -c \"/usr/local/bin/python Testing/docker_backend_testing.py -u %MYSQL_USER_NAME% -p %MYSQL_PASSWORD% -i %IS_JOB_RUN% -r %REQUEST_TYPE% -s %IS_MYSQL_CONTAINER_FOR_DOCKER%\""
                        }
                    } else {
                        def containerId = sh(script: 'docker ps --filter "name=${REST_CONTAINER_NAME}" --format "{{.ID}}"', returnStdout: true).trim().readLines().drop(1).join(" ")
                        sleep(time: 2, unit: "SECONDS")
                        withCredentials([usernamePassword(credentialsId: 'container_database_credentials', usernameVariable: 'MYSQL_USER_NAME', passwordVariable: 'MYSQL_PASSWORD')]) {
                            sh "docker exec -i ${containerId} sh \"/usr/local/bin/python Testing/docker_backend_testing.py -u ${MYSQL_USER_NAME} -p ${MYSQL_PASSWORD} -i ${IS_JOB_RUN} -r ${REQUEST_TYPE} -s ${IS_MYSQL_CONTAINER_FOR_DOCKER}\""
                        }
                    }
                }
            }
        }

        // Step 12 - Docker App - Stop Flask Servers - Option 1 //
        stage("[Docker] Run `clean_environment.py` (Clean)") {
            steps {
                script {
                    if (checkOS() == "Windows") {
                        def containerId = bat(script: 'docker ps --filter "name=%REST_CONTAINER_NAME%" --format "{{.ID}}"', returnStdout: true).trim().readLines().drop(1).join(" ")
                        sleep(time: 2, unit: "SECONDS")
                        withCredentials([usernamePassword(credentialsId: 'container_database_credentials', usernameVariable: 'DB_USER_NAME', passwordVariable: 'DB_PASSWORD')]) {
                            bat "docker exec -i ${containerId} sh -c \"/usr/local/bin/python Clean/clean_environment.py -u %DB_USER_NAME% -p %DB_PASSWORD% -i %IS_JOB_RUN% -c %CLEAN_SERVER% -d %IS_REST_API_CONTAINER%\""
                        }
                    } else {
                        def containerId = sh(script: 'docker ps --filter "name=${REST_CONTAINER_NAME}" --format "{{.ID}}"', returnStdout: true).trim().readLines().drop(1).join(" ")
                        sleep(time: 2, unit: "SECONDS")
                        withCredentials([usernamePassword(credentialsId: 'container_database_credentials', usernameVariable: 'DB_USER_NAME', passwordVariable: 'DB_PASSWORD')]) {
                            sh "docker exec -i ${containerId} sh \"/usr/local/bin/python Clean/clean_environment.py -u ${DB_USER_NAME} -p ${DB_PASSWORD} -i ${IS_JOB_RUN} -c ${CLEAN_SERVER} -d ${IS_REST_API_CONTAINER}\""
                        }
                    }
                }
            }
        }

        // Step 12 - Docker App - Stop Flask Servers - Option 2 //
        /*
        stage("[Docker] Docker App - Stop Flask Servers") {
            steps {
                script {
                    if (checkOS() == "Windows") {
                        def containerId = bat(script: 'docker ps --filter "name=%REST_CONTAINER_NAME%" --format "{{.ID}}"', returnStdout: true).trim().readLines().drop(1).join(" ")
                        sleep(time: 2, unit: "SECONDS")
                        withCredentials([usernamePassword(credentialsId: 'container_database_credentials', usernameVariable: 'DB_USER_NAME', passwordVariable: 'DB_PASSWORD')]) {
                            bat "docker exec -i ${containerId} sh -c \"curl -i --connect-timeout 30 http://127.0.0.1:5000/stop_server\""
                        }
                    } else {
                        def containerId = sh(script: 'docker ps --filter "name=${REST_CONTAINER_NAME}" --format "{{.ID}}"', returnStdout: true).trim().readLines().drop(1).join(" ")
                        sleep(time: 2, unit: "SECONDS")
                        withCredentials([usernamePassword(credentialsId: 'container_database_credentials', usernameVariable: 'DB_USER_NAME', passwordVariable: 'DB_PASSWORD')]) {
                            sh "docker exec -i ${containerId} sh \"curl -i --connect-timeout 30 http://127.0.0.1:5000/stop_server\""
                        }
                    }
                }
            }
        }
        */

        // Step 13 - Clean & Remove Docker Images //
        stage("[Docker] Clean & Remove Docker Images") {
            steps {
                script {
                    if (checkOS() == "Windows") {
                        bat 'docker-compose --file Dockerfiles\\%DOCKER_COMPOSE_FILE_1% down --rmi all --volumes'
                    } else {
                        sh "docker-compose --file Dockerfiles/${DOCKER_COMPOSE_FILE_1} down --rmi all --volumes"
                    }
                }
            }
        }

        // Step 14 - Minikube Start //
        stage("[K8S] Minikube Start") {
            steps {
                script {
                    if (checkOS() == "Windows") {
                        bat 'minikube start'
                    } else {
                        sh 'minikube start'
                    }
                }
            }
        }

        // Step 15 - Build & Up Docker Compose //
        stage("[K8S] Build Docker Compose") {
            steps {
                script {
                    if (checkOS() == "Windows") {
                        bat 'docker-compose --env-file .env --file Dockerfiles\\%DOCKER_COMPOSE_FILE_3% build'
                    } else {
                        sh "docker-compose --env-file .env --file Dockerfiles/${DOCKER_COMPOSE_FILE_3} build"
                    }
                    sleep(time: 10, unit: "SECONDS")
                }
            }
        }

        // Step 16 - Push Docker Compose //
        stage("[K8S] Push Docker Compose") {
            steps {
                script {
                    if (checkOS() == "Windows") {
                        bat 'docker-compose --env-file .env --file Dockerfiles\\%DOCKER_COMPOSE_FILE_3% push'
                    } else {
                        sh "docker-compose --env-file .env --file Dockerfiles/${DOCKER_COMPOSE_FILE_3} push"
                    }
                }
            }
        }

        // Step 17 - Deploy HELM Chart with Passing Image //
        stage("[K8S] Deploy HELM Chart with Passing Image") {
            steps {
                script {
                    if (checkOS() == "Windows") {
                        bat 'helm upgrade -i %HELM_CHART_NAME% HELM\\ --set image.version=%DOCKER_REPOSITORY%:%REST_TAG%%IMAGE_TAG_3%'
                    } else {
                        sh 'helm upgrade -i ${HELM_CHART_NAME} HELM/ --set image.version=${DOCKER_REPOSITORY}:${REST_TAG}${IMAGE_TAG_3}'
                    }
                }
            }
        }

        // Step 18 - Write Service URL into `k8s_url.txt` - Option 1 //
        stage("[K8S] Write service URL into `k8s_url.txt`") {
            steps {
                script {
                    if (checkOS() == "Windows") {
                        bat 'start /B minikube service %REST_API_SERVICE_NAME% --url > Testing\\%K8S_URL_FILE%'
                    } else {
                        sh 'minikube service ${REST_API_SERVICE_NAME} --url > Testing/${K8S_URL_FILE} &'
                    }
                }
            }
        }

        // Step 18 - Write Service URL into `k8s_url.txt` - Option 2 //
        /*
        stage("[K8S] Write service URL into `k8s_url.txt`") {
            steps {
                script {
                    def result = false

                    while (result == false) {
                        result = storeUrlInFile()
                    }
                }
            }
        }
        */

        // Step 19 - Test Deployed Application //
        stage("[K8S] Test Deployed Application - `k8s_backend_testing.py`") {
            steps {
                script {
                    if (checkOS() == "Windows") {
                        sleep(time: 120, unit: "SECONDS")
                        withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'MYSQL_USER_NAME', passwordVariable: 'MYSQL_PASSWORD')]) {
                            bat 'python Testing\\k8s_backend_testing.py -u %MYSQL_USER_NAME% -p %MYSQL_PASSWORD% -i %IS_JOB_RUN% -r %REQUEST_TYPE% -s %IS_MYSQL_CONTAINER_FOR_K8S% -k %IS_K8S_URL%'
                        }
                    } else {
                        sleep(time: 120, unit: "SECONDS")
                        withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'MYSQL_USER_NAME', passwordVariable: 'MYSQL_PASSWORD')]) {
                           sh 'python Testing/k8s_backend_testing.py -u ${MYSQL_USER_NAME} -p ${MYSQL_PASSWORD} -i ${IS_JOB_RUN} -r ${REQUEST_TYPE} -s ${IS_MYSQL_CONTAINER_FOR_K8S} -k ${IS_K8S_URL}'
                        }
                    }
                }
            }
        }

        // Step 20 - Remove `k8s_url.txt` //
        stage("[K8S] Remove `k8s_url.txt`") {
            steps {
                script {
                    if (checkOS() == "Windows") {
                        if (fileExists('Testing\\%K8S_URL_FILE%')) {
                            bat 'del Testing\\%K8S_URL_FILE%'
                        }
                    } else {
                        if (fileExists('Testing/${K8S_URL_FILE}')) {
                            sh 'rm Testing/${K8S_URL_FILE}'
                        }
                    }
                }
            }
        }
    }

    // Step 21 - Clean HELM / Minikube / Docker Environment //
    post {
        always {
            script {
                if (checkOS() == "Windows") {
                    bat 'helm delete %HELM_CHART_NAME%'
                    bat 'minikube delete'
                    bat 'docker-compose --file Dockerfiles\\%DOCKER_COMPOSE_FILE_3% down --rmi all --volumes'
                } else {
                    sh 'helm delete %HELM_CHART_NAME%'
                    sh 'minikube delete'
                    sh "docker-compose --file Dockerfiles/${DOCKER_COMPOSE_FILE_3} down --rmi all --volumes"
                }
            }
        }
    }
}

/* Functions */
def storeUrlInFile() {
    def url  = ''
    def file = ''

    if (checkOS() == "Windows") {
        url  = bat(script: 'start /B minikube service %REST_API_SERVICE_NAME% --url', returnStdout: true).trim().readLines().join(" ").replaceAll("\'","")
        file = 'Testing\\%K8S_URL_FILE%'
    } else {
        url  = sh(script: 'minikube service ${REST_API_SERVICE_NAME} --url &', returnStdout: true).trim().readLines().join(" ").replaceAll("\'","")
        file = 'Testing/${K8S_URL_FILE}'
    }

    if (url == '') {
        return false
    }

    writeFile file: file, text: url
    return readFile(file) == url
}

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

def setEnvFile() {
    // Note - We can write also the following IMAGE_TAG : IMAGE_TAG=%BUILD_NUMBER% / IMAGE_TAG=${BUILD_NUMBER} //
    if (checkOS() == 'Windows') {
        bat 'echo DOCKER_REPOSITORY=%DOCKER_REPOSITORY%                                          > .env'
        bat 'echo MYSQL_ROOT_USER=%MYSQL_ROOT_USER%                                             >> .env'
        bat 'echo MYSQL_ROOT_PASSWORD=%MYSQL_ROOT_PASSWORD%                                     >> .env'
        bat 'echo MYSQL_USER=%MYSQL_USER_NAME%                                                  >> .env'
        bat 'echo MYSQL_PASSWORD=%MYSQL_PASSWORD%                                               >> .env'
        bat 'echo MYSQL_SCHEMA_NAME=%MYSQL_SCHEMA_NAME%                                         >> .env'
        bat 'echo MYSQL_HOST_PORT=%MYSQL_HOST_PORT%                                             >> .env'
        bat 'echo MYSQL_GUEST_PORT=%MYSQL_GUEST_PORT%                                           >> .env'
        bat 'echo MYSQL_CONTAINER_NAME=%MYSQL_CONTAINER_NAME%                                   >> .env'
        bat 'echo REST_CONTAINER_NAME=%REST_CONTAINER_NAME%                                     >> .env'
        bat 'echo DOCKER_BACKEND_TESTING_CONTAINER_NAME=%DOCKER_BACKEND_TESTING_CONTAINER_NAME% >> .env'
        bat 'echo MYSQL_HOST_NAME=%MYSQL_HOST_NAME%                                             >> .env'
        bat 'echo MYSQL_REMOTE_HOST_NAME=%MYSQL_REMOTE_HOST_NAME%                               >> .env'
        bat 'echo REST_HOST_NAME=%REST_HOST_NAME%                                               >> .env'
        bat 'echo DOCKER_BACKEND_TESTING_HOST_NAME=%DOCKER_BACKEND_TESTING_HOST_NAME%           >> .env'
        bat 'echo IMAGE_TAG_1=%IMAGE_TAG_1%                                                     >> .env'
        bat 'echo IMAGE_TAG_2=%IMAGE_TAG_2%                                                     >> .env'
        bat 'echo IMAGE_TAG_3=%IMAGE_TAG_3%                                                     >> .env'
        bat 'echo MYSQL_TAG=%MYSQL_TAG%                                                         >> .env'
        bat 'echo REST_TAG=%REST_TAG%                                                           >> .env'
        bat 'echo PY_TAG=%PY_TAG%                                                               >> .env'
    } else {
        sh 'echo DOCKER_REPOSITORY=${DOCKER_REPOSITORY}                                          > .env'
        sh 'echo MYSQL_ROOT_USER=${MYSQL_ROOT_USER}                                             >> .env'
        sh 'echo MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}                                     >> .env'
        sh 'echo MYSQL_USER=${MYSQL_USER_NAME}                                                  >> .env'
        sh 'echo MYSQL_PASSWORD=${MYSQL_PASSWORD}                                               >> .env'
        sh 'echo MYSQL_SCHEMA_NAME=${MYSQL_SCHEMA_NAME}                                         >> .env'
        sh 'echo MYSQL_HOST_PORT=${MYSQL_HOST_PORT}                                             >> .env'
        sh 'echo MYSQL_GUEST_PORT=${MYSQL_GUEST_PORT}                                           >> .env'
        sh 'echo MYSQL_CONTAINER_NAME=${MYSQL_CONTAINER_NAME}                                   >> .env'
        sh 'echo REST_CONTAINER_NAME=${REST_CONTAINER_NAME}                                     >> .env'
        sh 'echo DOCKER_BACKEND_TESTING_CONTAINER_NAME=${DOCKER_BACKEND_TESTING_CONTAINER_NAME} >> .env'
        sh 'echo MYSQL_HOST_NAME=${MYSQL_HOST_NAME}                                             >> .env'
        sh 'echo MYSQL_REMOTE_HOST_NAME=${MYSQL_REMOTE_HOST_NAME}                               >> .env'
        sh 'echo REST_HOST_NAME=${REST_HOST_NAME}                                               >> .env'
        sh 'echo DOCKER_BACKEND_TESTING_HOST_NAME=${DOCKER_BACKEND_TESTING_HOST_NAME}           >> .env'
        sh 'echo IMAGE_TAG_1=${IMAGE_TAG_1}                                                     >> .env'
        sh 'echo IMAGE_TAG_2=${IMAGE_TAG_2}                                                     >> .env'
        sh 'echo IMAGE_TAG_3=${IMAGE_TAG_3}                                                     >> .env'
        sh 'echo MYSQL_TAG=${MYSQL_TAG}                                                         >> .env'
        sh 'echo REST_TAG=${REST_TAG}                                                           >> .env'
        sh 'echo PY_TAG=${PY_TAG}                                                               >> .env'
    }
}
