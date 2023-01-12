###########################
# Backend Testing Section #
###########################


# Imports #
import os
import sys
import requests
import warnings
warnings.filterwarnings('ignore')


# Sys Path #
package_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(package_path)


# From #
from DB.db_connector import *


def requests_menu():
    """
    :explanations:
    - Get request type from user.
    - The options are - [POST, GET, GET_ALL, PUT, DELETE].

    :return: request_type (str).
    """
    print("\n################")
    print("# Request MENU #")
    print("################\n")
    while True:
        request_type = input("Please select the request type you want [POST, GET, GET_ALL, PUT, DELETE, PRINT_TABLE, EXIT] : ")
        request_type = request_type.upper()
        if request_type in ["POST", "GET", "GET_ALL", "PUT", "DELETE", "PRINT_TABLE", "EXIT"]: break
        else: print("\nError : Please enter input from one of the following - [POST, GET, GET_ALL, PUT, DELETE, PRINT_TABLE, EXIT] ...\n")

    return request_type


def generate_response_dict(requests_result, json_result, json_key, message):
    """
    :explanations:
    - Generate response in JSON format.

    :param requests_result: (requests).
    :param json_result: (JSON).
    :param json_key: (str).
    :param message: (str).

    :return: response_dict (dict).
    """
    return {
        "status"       : json_result.get("status"),
        json_key       : json_result.get(json_key),
        'status_code'  : requests_result.status_code,
        'message'      : message,
    }


def check_requests_result(request_title, user_id, requests_result, json_result, json_key):
    """
    :explanations:
    - Check the result after request.

    :param request_title: (str)
    :param user_id: (str).
    :param requests_result: (requests).
    :param json_result: (JSON).
    :param json_key: (str).

    :return: None.
    """
    if requests_result.ok:
        status_code     = requests_result.status_code
        jason_user_name = json_result.get(json_key)

        if status_code != 200:
            message = f"We get status code different then 200 , status_code = {status_code} ..."
            raise Exception(f"\n[{request_title}] Test Failed : " + str(generate_response_dict(requests_result, json_result, json_key, message)) + "\n")

        db_user_ids = get_user_ids_of_specific_user_name_from_users_table(jason_user_name)

        if request_title in ["POST", "GET", "PUT"]:
            if user_id not in db_user_ids:
                message = "`user_id` in Test not matched to `user_id` in DB, It means that `user_name` not contains the `user_id` we expected ..."
                raise Exception(f"\n[{request_title}] Test Failed : " + str(generate_response_dict(requests_result, json_result, json_key, message)) + "\n")

            message = "`user_id` in Test matched to `user_id` in DB, It means that `user_name` contains the same `user_id` ..."
            print(f"\n[{request_title}] Test Succeed : " + str(generate_response_dict(requests_result, json_result, json_key, message)) + "\n")

        elif request_title in ["DELETE"]:
            if user_id in db_user_ids:
                message = "`user_id` in Test exists in DB, It means that DELETE operation not works as expected ..."
                raise Exception(f"\n[{request_title}] Test Failed : " + str(generate_response_dict(requests_result, json_result, json_key, message)) + "\n")

            message = "`user_id` in Test not exists in DB, It means that DELETE operation works as expected ..."
            print(f"\n[{request_title}] Test Succeed : " + str(generate_response_dict(requests_result, json_result, json_key, message)) + "\n")

    else:
        message = "`requests_result.ok` is not `OK` ..."
        raise Exception(f"\n[{request_title}] Test Failed : " + str(generate_response_dict(requests_result, json_result, json_key, message)) + "\n")


def check_requests_result_for_get_all(request_title, requests_result, json_result, json_key):
    """
    :explanations:
    - Check the result after `GET_ALL` request.

    :param request_title: (str)
    :param requests_result: (requests).
    :param json_result: (JSON).
    :param json_key: (str).

    :return: None.
    """
    if requests_result.ok:
        status_code     = requests_result.status_code
        all_users_json  = json.dumps(json_result, indent=4)

        if status_code != 200:
            message = f"We get status code different then 200 , status_code = {status_code} ..."
            raise Exception(f"\n[{request_title}] Test Failed : {message}" + "\n")

        print(f"\n[{request_title}] Test Succeed : ", end="")
        print({'status_code': status_code})
        print(f"\n`{json_key}` --->")
        print(all_users_json)
        print()

    else:
        message = "`requests_result.ok` is not `OK` ..."
        raise Exception(f"\n[{request_title}] Test Failed : {message}" + "\n")


def send_post_request(user_name):
    """
    :explanations:
    - Send POST request.

    :param: user_name: (str).

    :return: None
    """
    print("\n##########")
    print("#  POST  #")
    print("##########\n")
    new_user_id     = get_new_user_id_from_users_table()
    url             = f"http://{get_rest_host()}:{get_rest_port()}/{get_db_users_table_name()}/{new_user_id}"
    requests_result = requests.post(url=url, json={"user_name": user_name})
    json_result     = requests_result.json()
    check_requests_result("POST", new_user_id, requests_result, json_result, "user_added")


def send_get_request(url, user_id):
    """
    :explanations:
    - Send GET request.

    :param: url: (str).
    :param: user_id: (str).

    :return: None
    """
    print("\n#########")
    print("#  GET  #")
    print("#########\n")
    requests_result = requests.get(url=url, json={"user_id": user_id})
    json_result     = requests_result.json()
    check_requests_result("GET", user_id, requests_result, json_result, "user_name")


def send_get_all_request(url):
    """
    :explanations:
    - Send GET_ALL request.

    :param: url: (str).

    :return: None
    """
    print("\n#############")
    print("#  GET ALL  #")
    print("#############\n")
    requests_result = requests.get(url=url)
    json_result     = requests_result.json()
    check_requests_result_for_get_all("GET_ALL", requests_result, json_result, "users_table")


def send_put_request(is_job_run, url, user_id, test_name):
    """
    :explanations:
    - Send PUT request.

    :param: is_job_run (Boolean).
    :param: url: (str).
    :param: user_id: (str).
    :param: test_name: (str).

    :return: None
    """
    print("\n#########")
    print("#  PUT  #")
    print("#########\n")

    # Vars #
    new_user_name = None

    if is_job_run:
        if   test_name == "Backend" : new_user_name = get_new_user_name_backend_test()
        elif test_name == "Combined": new_user_name = get_new_user_name_combined_backend_test()
    else:
        new_user_name = input("Please type new user name : ")

    requests_result = requests.put(url=url, json={"user_id": user_id, "new_user_name": new_user_name})
    json_result     = requests_result.json()
    check_requests_result("PUT", user_id, requests_result, json_result, "user_updated")


def send_delete_request(url, user_id):
    """
    :explanations:
    - Send DELETE request.

    :param: url: (str).
    :param: user_id: (str).

    :return: None
    """
    print("\n############")
    print("#  DELETE  #")
    print("############\n")
    requests_result = requests.delete(url=url, json={"user_id": user_id})
    json_result     = requests_result.json()
    check_requests_result("DELETE", user_id, requests_result, json_result, "user_deleted")


def backend_testing_function():
    """
    :explanations:
    - Test the backend side of the project.

    :return: None.
    """
    print("\n----------------")
    print("| Backend Test |")
    print("----------------\n")

    ###########################
    # Drop Tables (If Exists) #
    ###########################
    drop_table(get_db_config_table_name())
    drop_table(get_db_users_table_name())

    ###########
    # Jenkins #
    ###########
    is_job_run = get_from_jenkins_arguments().is_job_run

    ##################
    # Config Details #
    ##################
    # Create config table inside MySQL DB #
    create_config_table()

    # Insert rows to config table inside MySQL DB #
    insert_rows_to_config_table(is_job_run, "Backend")

    ################
    # User Details #
    ################
    # Create users table inside MySQL DB #
    create_users_table()

    # Insert rows to users table inside MySQL DB #
    insert_rows_to_users_table()


    if is_job_run:

        # Get `request_type` from Jenkins #
        request_type = get_from_jenkins_arguments().request_type

        # Jenkins - Parameters For Backend Testing #
        user_name_backend_test = get_user_name_backend_test()
        user_id_backend_test   = get_user_id_backend_test()
        url                    = f"http://{get_rest_host()}:{get_rest_port()}/{get_db_users_table_name()}/{user_id_backend_test}"

        print("\n############################################")
        print("# Jenkins - Parameters For Backend Testing #")
        print("############################################\n")
        print("[POST]             : " + str({'new_user_name': user_name_backend_test}))
        print("[GET, PUT, DELETE] : " + str({'user_id': user_id_backend_test, 'url': url}))

        if   request_type == "POST"       : send_post_request(user_name_backend_test)
        elif request_type == "GET"        : send_get_request(url, user_id_backend_test)
        elif request_type == "GET_ALL"    : send_get_all_request(url)
        elif request_type == "PUT"        : send_put_request(is_job_run, url, user_id_backend_test, "Backend")
        elif request_type == "DELETE"     : send_delete_request(url, user_id_backend_test)
        elif request_type == "PRINT_TABLE":
            print_table(get_db_users_table_name())
            print_table(get_db_config_table_name())

    else:

        while True:

            # Get `request_type` from user #
            request_type = requests_menu()

            # Send POST Request #
            if request_type == "POST":
                user_name_backend_test = get_details_from_external_user_for_backend("POST", "Backend")
                send_post_request(user_name_backend_test)

            # Send GET Request #
            elif request_type == "GET":
                url, user_id_backend_test = get_details_from_external_user_for_backend("GET", "Backend")
                send_get_request(url, user_id_backend_test)

            # Send GET_ALL Request #
            elif request_type == "GET_ALL":
                url = get_details_from_external_user_for_backend("GET_ALL", "Backend")
                send_get_all_request(url)

            # Send PUT Request #
            elif request_type == "PUT":
                url, user_id_backend_test = get_details_from_external_user_for_backend("PUT", "Backend")
                send_put_request(is_job_run, url, user_id_backend_test, "Backend")

            # Send DELETE Request #
            elif request_type == "DELETE":
                url, user_id_backend_test = get_details_from_external_user_for_backend("DELETE", "Backend")
                send_delete_request(url, user_id_backend_test)

            # Print Tables #
            elif request_type == "PRINT_TABLE":
                print("\n###############")
                print("# USERS TABLE #")
                print("###############\n")
                print_table(get_db_users_table_name())

                print("\n################")
                print("# CONFIG TABLE #")
                print("################\n")
                print_table(get_db_config_table_name())

            # Exit from `request type` menu #
            else:
                break


if __name__ == "__main__":
    backend_testing_function()
