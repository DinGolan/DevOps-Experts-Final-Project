#########################
# WEB Interface Section #
#########################


# Imports #
import os
import sys
import signal
import psutil


# Sys Path #
package_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(package_path)


# From #
from flask             import Flask, request
from DB.db_connector   import *


# Create Flask Instance #
app = Flask(__name__)


@app.route("/users/get_user_name/<user_id>")
def get_user_name(user_id):
    """
    :explanations:
    - Get `user_name` from DB by searching `user_id` in users table.

    :param user_id: (str).

    :return: HTML Format.
    """
    user_name = get_user_name_of_specific_user_id_from_users_table(user_id)

    if user_name is not None:
        return "<h1 id='user'>" + "`user name` is : " + user_name + "</h1>", 200
    else:
        return "<h1 id='error'>" + "No such `user id` : " + str(user_id) + "</h1>", 500


def kill_process():
    """
    :explanations:
    - Kill the current process.

    :return: True  - If process is still running.
             False - If process not running anymore.
    """
    # Vars #
    pid          = os.getpid()
    process      = psutil.Process(pid)
    process_name = process.name()

    if process_name in ["python.exe", "/usr/bin/python"]:
        os.kill(os.getpid(), signal.CTRL_C_EVENT)
        return True
    else:
        return False


@app.route('/stop_server', methods=['GET'])
def stop_web_app_server():
    """
    :explanations:
    - Stop running of WEB APP server.

    :return: response (Json), status_code (str)
    """
    if request.method == "GET":
        is_process_killed     = kill_process()
        response, status_code = (json.dumps({"status": "Server Stopped"}), 200) if is_process_killed is True else (json.dumps({"status": "Server Not Stopped"}), 500)
        return response, status_code


# Run Flask Application #
app.run(host=get_web_host(), debug=True, port=get_web_port())
