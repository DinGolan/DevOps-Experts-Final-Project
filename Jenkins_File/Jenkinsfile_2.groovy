pipeline {
    agent any

    stages {
        // Step 1 - Clone Git From GitHub //
        stage("Clone Git") {
            steps {
                git  credentialsId: "github_credentials", url: "https://github.com/DinGolan/DevOps-Experts-Final-Project.git", branch: 'main'
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

        // Step 5 - Run Testings //
        stage("Testing") {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'DB_USER_NAME', passwordVariable: 'DB_PASSWORD')]) {
                        def user_choice=${User_Choice}
                        echo "user_choice : ${user_choice}"

                        if (user_choice == "1") {
                            bat 'echo Run `backend_testing.py` (Testing)'
                            bat 'python Testing\\backend_testing.py -u %DB_USER_NAME% -p %DB_PASSWORD% -i %IS_JOB_RUN% -r %REQUEST_TYPE%'
                        } else if (user_choice == "2") {
                            bat 'echo Run `frontend_testing.py` (Testing)'
                            bat 'python Testing\\frontend_testing.py -u %DB_USER_NAME% -p %DB_PASSWORD% -i %IS_JOB_RUN%'
                        } else if (user_choice == "3") {
                            bat 'echo Run `combined_testing.py` (Testing)'
                            bat 'python Testing\\combined_testing.py -u %DB_USER_NAME% -p %DB_PASSWORD% -i %IS_JOB_RUN% -r %REQUEST_TYPE% -t %TEST_SIDE%'
                        } else {
                            bat 'echo \'User_Choice\' must to be between - [1, 2, 3] ...'
                        }
                    }
                }
            }
        }

        // Step 6 - Run Clean Environment //
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
