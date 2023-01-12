pipeline {
    agent any
    stages {
        // Step 1 - Clone Git From GitHub //
        stage("Clone Git") {
            steps {
                script {
                    properties ([pipelineTriggers([pollSCM('H/30 * * * *')])])
                }
                git  credentialsId: 'github_credentials', url: 'https://github.com/DinGolan/DevOps-Experts-Final-Project.git', branch: 'main'
            }
        }

        // Step 2 - Install Pip Packages //
        stage("Run `pip install`") {
            steps {
                script {
                    def installed_packages = bat(script: 'pip freeze', returnStdout: true).trim().readLines().join(" ")
                    echo "installed_packages :\n${installed_packages}"

                    if (installed_packages.contains('PyMySQL')) {
                        echo 'pymysql - Already Exist ...'
                    } else {
                        bat 'pip install pymysql'
                    }

                    if (installed_packages.contains('requests')) {
                        echo 'requests - Already Exist ...'
                    } else {
                        bat 'pip install requests'
                    }

                    if (installed_packages.contains('selenium')) {
                        echo 'selenium - Already Exist ...'
                    } else {
                        bat 'pip install selenium'
                    }

                    if (installed_packages.contains('Flask')) {
                        echo 'flask - Already Exist ...'
                    } else {
                        bat 'pip install flask'
                    }

                    if (installed_packages.contains('prettytable')) {
                        echo 'prettytable - Already Exist ...'
                    } else {
                        bat 'pip install prettytable'
                    }

                    if (installed_packages.contains('PyPika')) {
                        echo 'pypika - Already Exist ...'
                    } else {
                        bat 'pip install pypika'
                    }

                    if (installed_packages.contains('psutil')) {
                        echo 'psutil - Already Exist ...'
                    } else {
                        bat 'pip install psutil'
                    }
                }
            }
        }

        // Step 3 - Run REST API //
        stage("Run `rest_app.py` (Backend)") {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'DB_USER_NAME', passwordVariable: 'DB_PASSWORD')]) {
                        bat 'start /min python REST_API\\rest_app.py -u %DB_USER_NAME% -p %DB_PASSWORD%'
                    }
                }
            }
        }

        // Step 4 - Run WEB APP  //
        stage("Run `web_app.py` (Frontend)") {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'DB_USER_NAME', passwordVariable: 'DB_PASSWORD')]) {
                        bat 'start /min python Web_Interface\\web_app.py -u %DB_USER_NAME% -p %DB_PASSWORD%'
                    }
                }
            }
        }

        // Step 5 - Run Backend Test //
        stage("Run `backend_testing.py` (Testing)") {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'DB_USER_NAME', passwordVariable: 'DB_PASSWORD')]) {
                        bat 'python Testing\\backend_testing.py -u %DB_USER_NAME% -p %DB_PASSWORD% -i %IS_JOB_RUN% -r %REQUEST_TYPE%'
                    }
                }
            }
        }

        // Step 6 - Run Frontend Test //
        stage("Run `frontend_testing.py` (Testing)") {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'DB_USER_NAME', passwordVariable: 'DB_PASSWORD')]) {
                        bat 'python Testing\\frontend_testing.py -u %DB_USER_NAME% -p %DB_PASSWORD% -i %IS_JOB_RUN%'
                    }
                }
            }
        }

        // Step 7 - Run Combined Test //
        stage("Run `combined_testing.py` (Testing)") {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'DB_USER_NAME', passwordVariable: 'DB_PASSWORD')]) {
                        bat 'python Testing\\combined_testing.py -u %DB_USER_NAME% -p %DB_PASSWORD% -i %IS_JOB_RUN% -r %REQUEST_TYPE% -t %TEST_SIDE%'
                    }
                }
            }
        }

        // Step 8 - Run Clean Environment //
        stage("Run `clean_environment.py` (Clean)") {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'DB_USER_NAME', passwordVariable: 'DB_PASSWORD')]) {
                        bat 'python Clean\\clean_environment.py -u %DB_USER_NAME% -p %DB_PASSWORD% -i %IS_JOB_RUN%'
                    }
                }
            }
        }
    }
}