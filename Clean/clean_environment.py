#############################
# Clean Environment Section #
#############################


# Imports #
import os
import ast
import sys
import requests


# Sys Path #
package_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(package_path)


# From #
from Config.config   import *


# Global Vars #
STOP_SERVER = "stop_server"


def servers_menu():
    """
    :explanations:
    - Get server type from user.
    - The options are - [REST_API, WEB_APP].

    :return: server_type (str).
    """
    print("\n################")
    print("# Servers MENU #")
    print("################\n")
    while True:
        server_type = input("Please select the server type you want [REST_API, WEB_APP] : ")
        server_type = server_type.upper()
        if server_type in ["REST_API", "WEB_APP"]: break
        else: print("\nError : Please enter input from one of the following - [REST_API, WEB_APP] ...\n")

    return server_type


def clean_rest_api_environment(is_rest_api_container):
    """
    :explanations:
    - Clean REST API environment.

    :param: is_rest_api_container (str).

    :return: None
    """
    rest_host = get_rest_host() if (is_rest_api_container is None or is_rest_api_container == "False") else get_rest_host_container()
    url       = f"http://{rest_host}:{get_rest_port()}/{STOP_SERVER}"

    try:
        proxies         = {"http": url, "https": url}
        headers         = {
                            'user-agent'     : "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.125 Mobile Safari/537.36",
                            'Connection'     : "keep-alive",
                            'accept'         : "application/json",
                            'Accept-Encoding': "*",
                            'method'         : "GET"
                        }
        requests_result = requests.get(url, headers=headers, proxies=proxies)

        if requests_result.ok:
            requests_result.raise_for_status()
            json_result = ast.literal_eval(requests_result.json())
            message     = "REST API server stopped successfully ..." if json_result.get("status") == "Server Stopped" else "REST API server didn't stopped ..."
        else:
            message     = "REST API server didn't stopped ..."

        print("\n[Clear Environment] : " + str({'message': message, 'url': url, 'status code': requests_result.status_code}) + "\n")

    except requests.exceptions.RequestException as exception_error:
        print(f"\n[Clear Environment] : REST API server stopped successfully, but an error occurred while making the request. Exception is - {exception_error}\n")

    except ValueError as exception_error:
        print(f"\n[Clear Environment] : REST API server stopped successfully, but an error occurred while parsing the response. Exception is - {exception_error}\n")

    except (ConnectionError, TimeoutError) as exception_error:
        if "ConnectionResetError" in str(exception_error):
            message     = "REST API server stopped successfully ..."
            status_code = 200
            print("\n[Clear Environment] : " + str({'message': message, 'url': url, 'status code': status_code}) + "\n")
        else:
            print(f"\n[Clear Environment] : An error occurred. Exception is - {exception_error}\n")


def clean_web_app_environment():
    """
    :explanations:
    - Clean WEB APP environment.

    :return: None
    """
    url = f"http://{get_web_host()}:{get_web_port()}/{STOP_SERVER}"

    try:
        proxies         = {"http": url, "https": url}
        headers         = {
                            'user-agent'     : "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.125 Mobile Safari/537.36",
                            'Connection'     : "keep-alive",
                            'accept'         : "application/json",
                            'Accept-Encoding': "*",
                            'method'         : "GET"
                        }
        requests_result = requests.get(url, headers=headers, proxies=proxies)

        if requests_result.ok:
            requests_result.raise_for_status()
            json_result = ast.literal_eval(requests_result.json())
            message     = "WEB APP server stopped successfully ..." if json_result.get("status") == "Server Stopped" else "WEB APP server didn't stopped ..."
        else:
            message     = "WEB APP server didn't stopped ..."

        print("\n[Clear Environment] : " + str({'message': message, 'url': url, 'status code': requests_result.status_code}) + "\n")

    except requests.exceptions.RequestException as exception_error:
        print(f"\n[Clear Environment] : WEB APP server stopped successfully, but an error occurred while making the request. Exception is - {exception_error}\n")

    except ValueError as exception_error:
        print(f"\n[Clear Environment] : WEB APP server stopped successfully, but an error occurred while parsing the response. Exception is - {exception_error}\n")

    except (ConnectionError, TimeoutError) as exception_error:
        if "ConnectionResetError" in str(exception_error):
            message     = "WEB APP server stopped successfully ..."
            status_code = 200
            print("\n[Clear Environment] : " + str({'message': message, 'url': url, 'status code': status_code}) + "\n")
        else:
            print(f"\n[Clear Environment] : An error occurred. Exception is - {exception_error}")


def main():
    print("\n--------------------------")
    print("| Clean Environment Test |")
    print("--------------------------\n")

    ###########
    # Jenkins #
    ###########
    jenkins_arguments     = get_from_jenkins_arguments()
    is_job_run            = jenkins_arguments.is_job_run
    is_rest_api_container = jenkins_arguments.is_rest_api_container
    clean_server          = jenkins_arguments.clean_server

    if is_job_run == "True":
        # Jenkins File - 1 #
        if clean_server is None:
            clean_rest_api_environment(is_rest_api_container)
            clean_web_app_environment()

        # Jenkins File - 2 / 3 #
        elif clean_server == "REST_API": clean_rest_api_environment(is_rest_api_container)
        elif clean_server == "WEB_APP" : clean_web_app_environment()

    else:
        server_type = servers_menu()
        if   server_type == "REST_API": clean_rest_api_environment(is_rest_api_container)
        elif server_type == "WEB_APP" : clean_web_app_environment()


if __name__ == "__main__":
    main()
