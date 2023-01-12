############################
# Combined Testing Section #
############################


# From #
from backend_testing  import *
from frontend_testing import *


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
        test_side = input("Please select the test you want [Backend, Frontend, Exit] : ")
        test_side = test_side.title()
        if test_side in ["Backend", "Frontend", "Exit"]: break
        else: print("\nError : Please enter input from one of the following - [Backend, Frontend, Exit] ...\n")

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
    insert_rows_to_config_table(is_job_run, "Combined")

    ################
    # User Details #
    ################
    # Create users table inside MySQL DB #
    create_users_table()

    # Insert rows to users table inside MySQL DB #
    insert_rows_to_users_table()

    if is_job_run:

        # Get `test_side` from Jenkins #
        test_side    = get_from_jenkins_arguments().test_side

        if test_side == "Backend":

            # Get `request_type` from Jenkins #
            request_type = get_from_jenkins_arguments().request_type

            # Parameters For Combined Testing #
            user_name_combined_test = get_user_name_combined_backend_test()
            user_id_combined_test   = get_user_id_combined_backend_test()
            url                     = f"http://{get_rest_host()}:{get_rest_port()}/{get_db_users_table_name()}/{user_id_combined_test}"

            print("\n#############################################")
            print("# Jenkins - Parameters For Combined Testing #")
            print("#############################################")
            print("[POST]             : " + str({'new_user_name': user_name_combined_test}))
            print("[GET, PUT, DELETE] : " + str({'user_id': user_id_combined_test, 'url': url}) + "\n")

            if   request_type == "POST"   : send_post_request(user_name_combined_test)
            elif request_type == "GET"    : send_get_request(url, user_id_combined_test)
            elif request_type == "GET_ALL": send_get_all_request(url)
            elif request_type == "PUT"    : send_put_request(is_job_run, url, user_id_combined_test, "Combined")
            elif request_type == "DELETE" : send_delete_request(url, user_id_combined_test)
            elif request_type == "PRINT_TABLE":
                print_table(get_db_users_table_name())
                print_table(get_db_config_table_name())

        elif test_side == "Frontend":
            url, browser = get_details_from_external_user_for_frontend("Frontend", user_id_frontend_test=get_user_id_combined_frontend_test())

            print("\n#############################################")
            print("# Jenkins - Parameters For Combined Testing #")
            print("#############################################")
            print("[GET] : " + str({'user_id': get_user_id_frontend_test(), 'url': url, 'browser': browser}) + "\n")

            open_chrome_web_browser(url, browser)

    else:

        while True:

            # Get `test_side` from user #
            test_side = test_side_menu()

            if test_side == "Backend":

                # Get `request_type` from user #
                request_type = requests_menu()

                # Send POST Request #
                if request_type == "POST":
                    user_name_combined_test = get_details_from_external_user_for_backend("POST", "Combined")
                    send_post_request(user_name_combined_test)

                # Send GET Request #
                elif request_type == "GET":
                    url, user_id_combined_test = get_details_from_external_user_for_backend("GET", "Combined")
                    send_get_request(url, user_id_combined_test)

                elif request_type == "GET_ALL":
                    url = get_details_from_external_user_for_backend("GET_ALL", "Combined")
                    send_get_all_request(url)

                # Send PUT Request #
                elif request_type == "PUT":
                    url, user_id_combined_test = get_details_from_external_user_for_backend("PUT", "Combined")
                    send_put_request(is_job_run, url, user_id_combined_test, "Combined")

                # Send DELETE Request #
                elif request_type == "DELETE":
                    url, user_id_combined_test = get_details_from_external_user_for_backend("DELETE", "Combined")
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
                url, browser = get_details_from_external_user_for_frontend("Frontend")
                open_chrome_web_browser(url, browser)

            # Exit from `test side` menu #
            else:
                break


if __name__ == "__main__":
    combined_testing_function()