##################
# Config Section #
##################


# Imports #
import os
import sys
import json
import argparse


# Sys Path #
package_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(package_path)


# JSON #
json_file = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json"))
json_data = json.load(json_file)
json_file.close()


# Get JSON Data #
def get_web_host():
    return json_data["web_app.py"]["HOST_WEB"]


def get_web_port():
    return json_data["web_app.py"]["PORT_WEB"]


def get_rest_host():
    return json_data["rest_app.py"]["HOST_REST"]


def get_rest_port():
    return json_data["rest_app.py"]["PORT_REST"]


def get_db_host():
    return json_data["db_connector.py"]["HOST"]


def get_db_port():
    return json_data["db_connector.py"]["PORT"]


def get_db_schema_name():
    return json_data["db_connector.py"]["SCHEMA_NAME"]


def get_db_users_table_name():
    return json_data["db_connector.py"]["USERS_TABLE_NAME"]


def get_db_config_table_name():
    return json_data["db_connector.py"]["CONFIG_TABLE_NAME"]


def get_user_name_backend_test():
    return json_data["backend_testing.py"]["USER_NAME_BACKEND_TEST"]


def get_user_id_backend_test():
    return json_data["backend_testing.py"]["USER_ID_BACKEND_TEST"]


def get_new_user_name_backend_test():
    return json_data["backend_testing.py"]["NEW_USER_NAME_BACKEND_TEST"]


def get_user_id_frontend_test():
    return json_data["frontend_testing.py"]["USER_ID_FRONTEND_TEST"]


def get_user_name_combined_backend_test():
    return json_data["combined_testing.py"]["USER_NAME_COMBINED_BACKEND_TEST"]


def get_user_id_combined_backend_test():
    return json_data["combined_testing.py"]["USER_ID_COMBINED_BACKEND_TEST"]


def get_new_user_name_combined_backend_test():
    return json_data["combined_testing.py"]["NEW_USER_NAME_COMBINED_BACKEND_TEST"]


def get_user_id_combined_frontend_test():
    return json_data["combined_testing.py"]["USER_ID_COMBINED_FRONTEND_TEST"]


# List of Users #
def get_users_names_in_static_way():
    return ["Emily Smith"        , "Michael Johnson"  , "Joshua Williams"   , "Matthew Brown"   , "Olivia Jones"     ,
            "Nicholas Garcia"    , "Christopher Davis", "Samantha Rodriguez", "Joseph Martinez" , "Andrew Anderson"  ,
            "Emily Taylor"       , "David Thomas"     , "James Hernandez"   , "Ryan Moore"      , "Elizabeth Martin" ,
            "Kevin Jackson"      , "Joseph Thompson"  , "Sarah Garcia"      , "Anthony Martinez", "Jennifer Anderson",
            "Brandon Taylor"     , "Stephanie Thomas" , "Rebecca Hernandez" , "Elizabeth Perez" , "Donald Cox"       ,
            "Jennifer Richardson", "Steven Cox"       , "Anthony Howard"    , "Sarah Torres"    , "Joshua Peterson"  ,
            "Emma Watson"        , "Robert Downey Jr.", "Angelina Jolie"    , "Brad Pitt"       , "Michael Jackson"  ,
            "George Washington"  , "Albert Einstein"  , "Isaac Newton"      , "Nelson Mandela"  , "Abraham Lincoln"]


# Jenkins Arguments #
def get_from_jenkins_user_argument():
    """
    :explanations:
    - Get user argument from Jenkins.

    :return: jenkins_arguments.user_name (lst)
    """
    # Argument Parser #
    parser = argparse.ArgumentParser(description='Get `user_name` argument from Jenkins ...')
    parser.add_argument('-u', '--user_name', metavar='', required=True, help="User name for connecting to DB ...")
    jenkins_arguments = parser.parse_args()
    return jenkins_arguments.user_name


def get_from_jenkins_password_argument():
    """
    :explanations:
    - Get password argument from Jenkins.

    :return: jenkins_arguments.password (lst)
    """
    # Argument Parser #
    parser = argparse.ArgumentParser(description='Get `password` argument from Jenkins ...')
    parser.add_argument('-p', '--password', metavar='', required=True, help="Password for connecting to DB ...")
    jenkins_arguments = parser.parse_args()
    return jenkins_arguments.password


def get_from_jenkins_is_job_run():
    """
    :explanations:
    - Get `is_job_run` argument from Jenkins.

    :return: jenkins_arguments.is_job_run (str).
    """
    parser = argparse.ArgumentParser(description='Get `is_job_run` argument from Jenkins ...')
    parser.add_argument('-i', '--is_job_run', required=False, choices=["True", "False"], help="Flag that tells me if Jenkins job is running or not ...")
    jenkins_arguments = parser.parse_args()
    return jenkins_arguments.is_job_run


def get_from_jenkins_request_type():
    """
    :explanations:
    - Get `request_type` argument from Jenkins.

    :return: jenkins_arguments.request_type (str).
    """
    parser = argparse.ArgumentParser(description='Get `request_type` argument from Jenkins ...')
    parser.add_argument('-r', '--request_type', required=False, choices=["POST", "GET", "GET_ALL", "PUT", "DELETE", "PRINT_TABLE"], help="Request type for REST API Server ...")
    jenkins_arguments = parser.parse_args()
    return jenkins_arguments.request_type


def get_from_jenkins_test_side():
    """
    :explanations:
    - Get `test_side` argument from Jenkins.

    :return: jenkins_arguments.test_side (str).
    """
    parser = argparse.ArgumentParser(description='Get `test_side` argument from Jenkins ...')
    parser.add_argument('-t', '--test_side', required=False, choices=["Backend", "Frontend"], help="Test side for `combined_testing.py` ...")
    jenkins_arguments = parser.parse_args()
    return jenkins_arguments.test_side
