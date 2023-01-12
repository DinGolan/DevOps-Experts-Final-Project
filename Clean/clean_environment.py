#############################
# Clean Environment Section #
#############################


# Imports #
import os
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


def clean_rest_api_environment():
    """
    :explanations:
    - Clean REST API environment.

    :return: None
    """
    url = f"http://{get_rest_host()}:{get_rest_port()}/{STOP_SERVER}"

    try:
        proxies         = {"http": f"http://{get_rest_host()}:{get_rest_port()}/{STOP_SERVER}", "https": f"http://{get_rest_host()}:{get_rest_port()}/{STOP_SERVER}"}
        requests_result = requests.get(url, proxies=proxies)

        if requests_result.ok:
            json_result = requests_result.json()

            if json_result.get("status") == "Server Stopped":
                message = "REST API server stopped successfully ..."
                print(f"\n[Clear Environment] : {message}\n")
            else:
                print(f"\n[Clear Environment] : REST API server didn't stopped. Server returned status : {json_result.get('status')}")
        else:
            print(f"\n[Clear Environment] : REST API server didn't stopped. Server returned status code : {requests_result.status_code}")

    except (ConnectionError, TimeoutError) as exception_error:
        print(f"\n[Clear Environment] : REST API server didn't stopped. Exception is - {exception_error}\n")

    except Exception as exception_error:
        print(f"\n[Clear Environment] : REST API server didn't stopped. Exception is - {exception_error}\n")


def clean_web_app_environment():
    """
    :explanations:
    - Clean WEB APP environment.

    :return: None
    """
    url = f"http://{get_web_host()}:{get_web_port()}/{STOP_SERVER}"

    try:
        proxies         = {"http": f"http://{get_web_host()}:{get_web_port()}/{STOP_SERVER}", "https": f"http://{get_web_host()}:{get_web_port()}/{STOP_SERVER}"}
        requests_result = requests.get(url, proxies=proxies)

        if requests_result.ok:
            json_result = requests_result.json()

            if json_result.get("status") == "Server Stopped":
                message = "WEB APP server stopped successfully ..."
                print(f"\n[Clear Environment] : {message}\n")
            else:
                print(f"\n[Clear Environment] : WEB APP server didn't stopped. Server returned status : {json_result.get('status')}")
        else:
            print(f"\n[Clear Environment] : WEB APP server didn't stopped. Server returned status code : {requests_result.status_code}")

    except (ConnectionError, TimeoutError) as exception_error:
        print(f"\n[Clear Environment] : WEB APP server didn't stopped. Exception is - {exception_error}")

    except Exception as exception_error:
        print(f"\n[Clear Environment] : WEB APP server didn't stopped. Exception is - {exception_error}")


def main():
    print("\n--------------------------")
    print("| Clean Environment Test |")
    print("--------------------------\n")

    ###########
    # Jenkins #
    ###########
    is_job_run = get_from_jenkins_arguments().is_job_run

    if is_job_run:
        clean_rest_api_environment()
        clean_web_app_environment()

    else:
        server_type = servers_menu()
        if   server_type == "REST_API": clean_rest_api_environment()
        elif server_type == "WEB_APP" : clean_web_app_environment()


if __name__ == "__main__":
    main()
