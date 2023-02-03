/* Pipeline */
pipeline {
    agent any

    // Environments //
    environment {
        DOCKER_REPOSITORY   = "dingolan/devops_experts_final_project"
        DOCKER_COMPOSE_FILE = "docker-compose.yml"
        DB_TAG              = "db_app"
        PY_TAG              = "py_app"
    }

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
                git  credentialsId: "github_credentials", url: "https://github.com/DinGolan/DevOps-Experts-Final-Project.git", branch: 'main'
            }
        }

        // Step 2 - Update `.env` File //
        stage("Update `.env` File") {
            steps {
                script {
                    if (checkOS() == "Windows") {
                        bat 'echo BUILD_NUMBER=%BUILD_NUMBER% > project_envs.env'
                        bat 'echo DB_TAG=%DB_TAG% >> project_envs.env'
                        bat 'echo PY_TAG=%PY_TAG% >> project_envs.env'
                    } else {
                        sh 'echo BUILD_NUMBER=${BUILD_NUMBER} > project_envs.env'
                        sh 'echo DB_TAG=${DB_TAG} >> project_envs.env'
                        sh 'echo PY_TAG=${PY_TAG} >> project_envs.env'
                    }
                }
            }
        }

        // Step 3 - Login to Docker Hub //
        stage("Login to Docker Hub") {
            steps {
                script {
                    if (checkOS() == "Windows") {
                        withCredentials([usernamePassword(credentialsId: 'docker_hub', passwordVariable: 'DOCKER_HUB_PASSWORD', usernameVariable: 'DOCKER_HUB_USERNAME')]) {
                            bat 'docker login --username "%DOCKER_HUB_PASSWORD%" --password "%DOCKER_HUB_USERNAME%"'
                        }
                    } else {
                        withCredentials([usernamePassword(credentialsId: 'docker_hub', passwordVariable: 'DOCKER_HUB_PASSWORD', usernameVariable: 'DOCKER_HUB_USERNAME')]) {
                            sh 'docker login --username "${DOCKER_HUB_PASSWORD}" --password "$DOCKER_HUB_USERNAME}"'
                        }
                    }
                }
            }
        }

        // Step 4 - Build Docker Compose YAML File //
        stage("Build Docker Compose") {
            steps {
                script {
                    if (checkOS() == "Windows") {
                        bat 'docker-compose --env-file Project_Vars\\project_vars.env --file %DOCKER_COMPOSE_FILE% build'
                    } else {
                        sh 'docker-compose --env-file Project_Vars/project_vars.env --file ${DOCKER_COMPOSE_FILE} build'
                    }
                }
            }
        }

        // Step 5 - Push Docker Compose //
        stage("Push Docker Compose") {
            steps {
                script {
                    if (checkOS() == "Windows") {
                        bat 'docker-compose push'
                    } else {
                        sh 'docker-compose push'
                    }
                }
            }
        }

        // Step 6 - Run Docker Compose //
        stage("Run Docker Compose") {
            steps {
                script {
                    if (checkOS() == "Windows") {
                        bat 'docker-compose --env-file Project_Vars\\project_vars.env --file %DOCKER_COMPOSE_FILE% up -d'
                    } else {
                        sh 'docker-compose --env-file Project_Vars/project_vars.env --file ${DOCKER_COMPOSE_FILE} up -d'
                    }
                }
            }
        }

        // Step 7 - Clean & Remove Docker Images Build & Push //
        post {
            always {
                if (checkOS() == "Windows") {
                    bat 'docker-compose --file %DOCKER_COMPOSE_FILE% down --volumes'
                    bat 'docker rmi -f %DOCKER_REPOSITORY%:%DB_TAG%%BUILD_NUMBER%'
                    bat 'docker rmi -f %DOCKER_REPOSITORY%:%PY_TAG%%BUILD_NUMBER%'
                } else {
                    sh 'docker-compose --file ${DOCKER_COMPOSE_FILE} down --volumes'
                    sh 'docker rmi -f ${DOCKER_REPOSITORY}:${DB_TAG}${BUILD_NUMBER}'
                    sh 'docker rmi -f ${DOCKER_REPOSITORY}:${PY_TAG}${BUILD_NUMBER}'
                }
            }
        }
    }
}

/* Functions */
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
