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
                            bat 'pip install --ignore-installed pymysql requests selenium flask prettytable pypika psutil'
                        } else {
                            sh 'pip install --ignore-installed pymysql requests selenium flask prettytable pypika psutil'
                        }
                    }
                }
            }
        }

        // Step 3 - Run Testings //
        stage("Upload Servers + Testing") {
            steps {
                script {
                    if (checkOS() == "Windows") {
                        withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'DB_USER_NAME', passwordVariable: 'DB_PASSWORD')]) {
                            def user_choice = bat(script: 'echo %User_Choice%', returnStdout: true).trim().readLines().drop(1).join("")
                            echo "`user_choice` : ${user_choice}"

                            if (user_choice == "1") {
                                bat 'echo Run `frontend_testing.py` (Testing)'
                                bat 'start /min python Web_Interface\\web_app.py -u %DB_USER_NAME% -p %DB_PASSWORD%'
                                bat 'python Testing\\frontend_testing.py -u %DB_USER_NAME% -p %DB_PASSWORD% -i %IS_JOB_RUN%'

                            } else if (user_choice == "2") {
                                bat 'echo Run `backend_testing.py` (Testing)'
                                bat 'start /min python REST_API\\rest_app.py -u %DB_USER_NAME% -p %DB_PASSWORD%'
                                bat 'python Testing\\backend_testing.py -u %DB_USER_NAME% -p %DB_PASSWORD% -i %IS_JOB_RUN% -r %REQUEST_TYPE%'

                            } else if (user_choice == "3") {
                                bat 'echo Run `combined_testing.py` (Testing)'

                                def test_side = bat(script: 'echo %TEST_SIDE%', returnStdout: true).trim().readLines().drop(1).join("")
                                echo "`test_side` : ${test_side}"

                                if (test_side == "Backend") {
                                    bat 'start /min python REST_API\\rest_app.py -u %DB_USER_NAME% -p %DB_PASSWORD%'
                                } else if (test_side == "Frontend") {
                                    bat 'start /min python Web_Interface\\web_app.py -u %DB_USER_NAME% -p %DB_PASSWORD%'
                                }
                                bat 'python Testing\\combined_testing.py -u %DB_USER_NAME% -p %DB_PASSWORD% -i %IS_JOB_RUN% -r %REQUEST_TYPE% -t %TEST_SIDE%'

                            } else {
                                bat 'echo `User_Choice` must to be between - [1, 2, 3] ...'
                            }
                        }
                    } else {
                        withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'DB_USER_NAME', passwordVariable: 'DB_PASSWORD')]) {
                            def user_choice = sh(script: 'echo %User_Choice%', returnStdout: true).trim().readLines().drop(1).join("")
                            echo "`user_choice` : ${user_choice}"

                            if (user_choice == "1") {
                                sh 'echo Run `frontend_testing.py` (Testing)'
                                sh 'start /min python Web_Interface\\web_app.py -u %DB_USER_NAME% -p %DB_PASSWORD%'
                                sh 'python Testing\\frontend_testing.py -u %DB_USER_NAME% -p %DB_PASSWORD% -i %IS_JOB_RUN%'

                            } else if (user_choice == "2") {
                                sh 'echo Run `backend_testing.py` (Testing)'
                                sh 'start /min python REST_API\\rest_app.py -u %DB_USER_NAME% -p %DB_PASSWORD%'
                                sh 'python Testing\\backend_testing.py -u %DB_USER_NAME% -p %DB_PASSWORD% -i %IS_JOB_RUN% -r %REQUEST_TYPE%'

                            } else if (user_choice == "3") {
                                sh 'echo Run `combined_testing.py` (Testing)'

                                def test_side = sh(script: 'echo %TEST_SIDE%', returnStdout: true).trim().readLines().drop(1).join("")
                                echo "`test_side` : ${test_side}"

                                if (test_side == "Backend") {
                                    sh 'start /min python REST_API\\rest_app.py -u %DB_USER_NAME% -p %DB_PASSWORD%'
                                } else if (test_side == "Frontend") {
                                    sh 'start /min python Web_Interface\\web_app.py -u %DB_USER_NAME% -p %DB_PASSWORD%'
                                }
                                sh 'python Testing\\combined_testing.py -u %DB_USER_NAME% -p %DB_PASSWORD% -i %IS_JOB_RUN% -r %REQUEST_TYPE% -t %TEST_SIDE%'

                            } else {
                                sh 'echo `User_Choice` must to be between - [1, 2, 3] ...'
                            }
                        }
                    }
                }
            }
        }

        // Step 4 - Run Clean Environment //
        stage("Run `clean_environment.py` (Clean)") {
            steps {
                script {
                    if (checkOS() == "Windows") {
                        withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'DB_USER_NAME', passwordVariable: 'DB_PASSWORD')]) {
                            bat 'python Clean\\clean_environment.py -u %DB_USER_NAME% -p %DB_PASSWORD% -i %IS_JOB_RUN% -c %CLEAN_SERVER%'
                        }
                    } else {
                        withCredentials([usernamePassword(credentialsId: 'database_credentials', usernameVariable: 'DB_USER_NAME', passwordVariable: 'DB_PASSWORD')]) {
                            sh 'python Clean\\clean_environment.py -u %DB_USER_NAME% -p %DB_PASSWORD% -i %IS_JOB_RUN% -c %CLEAN_SERVER%'
                        }
                    }
                }
            }
        }
    }

    // Step - Sending Mail //
    // Note - This section is not supported because I've Two Factor Authentication For Gmail //
    /*
    post {
        always {
            echo 'Pipeline done, checking if any failure for sending an email ...'
        }
        success {
            echo 'successfully done, no need to send email, see you next time ...'
        }
        failure {
            mail to: "$DEFAULT_RECIPIENTS",
            subject: "DevOps Experts - Final Project - Mail Updates",
            body: 'Job name: '  + "${env.JOB_NAME}"  + ' pipeline<br>' +
                  'Build URL: ' + "${env.BUILD_URL}" + '<br>'
            attachLog: true
        }
        unstable {
            echo 'run was marked as unstable ...'
        }
        changed {
            echo 'Pipeline was changed from last run, please follow logs ...'
        }
    }
    */
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
