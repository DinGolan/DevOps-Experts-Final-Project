#############################
# Clean Environment Section #
#############################


# Imports #
import os
import sys
import time
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

    while True:
        try:
            proxies         = {"http": f"http://{get_rest_host()}:{get_rest_port()}/{STOP_SERVER}", "https": f"http://{get_rest_host()}:{get_rest_port()}/{STOP_SERVER}"}
            headers         = {
                                'user-agent'     : "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.125 Mobile Safari/537.36",
                                'Connection'     : "keep-alive",
                                'Accept-Encoding': "*",
                                'method'         : "GET"
                            }
            requests_result = requests.get(url, headers=headers, proxies=proxies)

            if requests_result.ok:
                json_result = requests_result.json()
                message     = "REST API server stopped successfully ..." if json_result.get("status") == "Server Stopped" else "REST API server didn't stopped ..."
            else:
                message     = "REST API server didn't stopped ..."

            print("\n[Clear Environment] : " + str({'message': message, 'url': url, 'status code': requests_result.status_code}) + "\n")

            break

        except (ConnectionError, TimeoutError) as exception_error:
            print(f"\n[Clear Environment] : REST API server didn't stopped. Exception is - {exception_error}\n")

        except Exception as exception_error:
            print(f"\n[Clear Environment] : REST API server didn't stopped. Exception is - {exception_error}\n")

        # Going to Sleep for 1 Second #
        time.sleep(1)


def clean_web_app_environment():
    """
    :explanations:
    - Clean WEB APP environment.

    :return: None
    """
    url = f"http://{get_web_host()}:{get_web_port()}/{STOP_SERVER}"

    while True:
        try:
            proxies         = {"http": f"http://{get_web_host()}:{get_web_port()}/{STOP_SERVER}", "https": f"http://{get_web_host()}:{get_web_port()}/{STOP_SERVER}"}
            headers         = {
                                'user-agent': "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.125 Mobile Safari/537.36",
                                'Connection':"keep-alive",
                                'Accept-Encoding': "*",
                                'method'    :"GET"
                            }
            requests_result = requests.get(url, headers=headers, proxies=proxies)

            if requests_result.ok:
                json_result = requests_result.json()
                message     = "WEB APP server stopped successfully ..." if json_result.get("status") == "Server Stopped" else "WEB APP server didn't stopped ..."
            else:
                message     = "WEB APP server didn't stopped ..."

            print("\n[Clear Environment] : " + str({'message': message, 'url': url, 'status code': requests_result.status_code}) + "\n")

            break

        except (ConnectionError, TimeoutError) as exception_error:
            print(f"\n[Clear Environment] : WEB APP server didn't stopped. Exception is - {exception_error}")

        except Exception as exception_error:
            print(f"\n[Clear Environment] : WEB APP server didn't stopped. Exception is - {exception_error}")

        # Going to Sleep for 1 Second #
        time.sleep(1)



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
