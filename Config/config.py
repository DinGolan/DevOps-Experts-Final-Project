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
def get_web_host_bind():
    return json_data["web_app.py"]["HOST_BIND_WEB"]


def get_web_host():
    return json_data["web_app.py"]["HOST_WEB"]


def get_web_port():
    return json_data["web_app.py"]["PORT_WEB"]


def get_rest_host_bind():
    return json_data["rest_app.py"]["HOST_BIND_REST"]


def get_rest_host():
    return json_data["rest_app.py"]["HOST_REST"]


def get_rest_port():
    return json_data["rest_app.py"]["PORT_REST"]


def get_db_host():
    return json_data["db_connector.py"]["HOST"]


def get_db_port():
    return json_data["db_connector.py"]["PORT"]


def get_db_user_name():
    return json_data["db_connector.py"]["USER_NAME"]


def get_db_password():
    return json_data["db_connector.py"]["PASSWORD"]


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
def get_from_jenkins_arguments():
    """
    :explanations:
    - Get arguments from Jenkins.

    :return: jenkins_arguments
    """
    # Argument Parser #
    parser = argparse.ArgumentParser(description='Get arguments from Jenkins ...')
    parser.add_argument('-u', '--user_name'   , required=False, metavar=''                                                        , help="User name for connecting to DB ...")
    parser.add_argument('-p', '--password'    , required=False, metavar=''                                                        , help="Password for connecting to DB ...")
    parser.add_argument('-i', '--is_job_run'  , required=False, choices=["True", "False"]                                         , help="Flag that tells me if Jenkins job is running or not ...")
    parser.add_argument('-r', '--request_type', required=False, choices=["POST", "GET", "GET_ALL", "PUT", "DELETE", "PRINT_TABLE"], help="Request type for REST API Server ...")
    parser.add_argument('-t', '--test_side'   , required=False, choices=["Backend", "Frontend"]                                   , help="Test side for `combined_testing.py` ...")
    parser.add_argument('-c', '--clean_server', required=False, choices=["REST_API", "WEB_APP"]                                   , help="Clean environment ...")
    jenkins_arguments = parser.parse_args()
    return jenkins_arguments
