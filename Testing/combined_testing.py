############################
# Combined Testing Section #
############################


# Imports #
import requests


# From #
from backend_testing import requests_menu, check_requests_result, send_get_request, send_put_request, send_delete_request
from fronted_testing import *


def send_post_request(url, user_id, user_name):
    """
    :explanations:
    - Send POST request.

    :param: url: (str).
    :param: user_id (str).
    :param: user_name: (str).

    :return: None
    """
    print("\n##########")
    print("#  POST  #")
    print("##########\n")
    requests_result = requests.post(url=url, json={"user_id": user_id, "user_name": user_name})
    json_result     = requests_result.json()
    check_requests_result("POST", user_id, requests_result, json_result, "user_added")


def test_side_menu():
    """
    :explanations:
    - Return `test_side` from user.
    - The options are - `Backend`, `Frontend`.

    :return: test_side (str).
    """
    print("\n#############")
    print("# Test MENU #")
    print("#############\n")
    while True:
        test_side = input("Please select the test you want [Backend, Fronted, Exit] : ")
        test_side = test_side.title()
        if test_side in ["Backend", "Frontend", "Exit"]: break
        else: print("\nError : Please enter input from one of the following - [Backend, Frontend] ...\n")

    return test_side


def combined_testing_function():
    """
    :explanations:
    - Make combined testing for Web Interface, REST API, DB Testing.

    :return: None.
    """
    print("\n-----------------")
    print("| Combined Test |")
    print("-----------------\n")

    print("##################")
    print("# Config Details #")
    print("##################\n")
    # Create config table inside MySQL DB #
    create_config_table()

    # Insert rows to config table inside MySQL DB #
    insert_rows_to_config_table()

    print("\n################")
    print("# User Details #")
    print("################")
    user_id_combined_test   = int(input("\nPlease enter `user id` : "))
    user_name_combined_test = input("\nPlease enter `user name` : ")

    sql_query               = f"SELECT url, browser "                         \
                              f"FROM {get_db_schema_name()}.{get_db_config_table_name()} "      \
                              f"WHERE (user_id = '{user_id_combined_test}') AND (user_name = '{user_name_combined_test}');"
    query_result            = run_sql_query(sql_query)
    query_result            = list(itertools.chain(*query_result))

    if len(query_result) == 0:
        raise Exception(f"\n[Combined Test] Test Failed : (`user_id` = {user_id_combined_test} , `user_name` = {user_name_combined_test}) not exist in `config` table ...\n")

    url, browser            = query_result
    browser                 = browser.lower()

    # Create users table inside MySQL DB #
    create_users_table_result = create_users_table()
    if create_users_table_result is False:
        raise Exception("\nTest Failed : Table `users` didn't generated in MySQL DB ...\n")

    while True:

        # Get `test_side` from user #
        test_side = test_side_menu()

        if test_side == "Backend":

            # Get `request_type` from user #
            request_type = requests_menu()

            # Send POST Request #
            if request_type == "POST":
                send_post_request(url, user_id_combined_test, user_name_combined_test)

            # Send GET Request #
            elif request_type == "GET":
                send_get_request(url, user_id_combined_test)

            # Send PUT Request #
            elif request_type == "PUT":
                send_put_request(url, user_id_combined_test)

            # Send DELETE Request #
            elif request_type == "DELETE":
                send_delete_request(url, user_id_combined_test)

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

        # Check Web Interface #
        elif test_side == "Frontend":
            open_chrome_web_browser(url, browser)

        # Exit from `test side` menu #
        else:
            break


if __name__ == "__main__":
    combined_testing_function()