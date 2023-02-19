#########################
# WEB Interface Section #
#########################


# Imports #
import os
import sys
import signal
import psutil
import platform


# Sys Path #
package_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(package_path)


# From #
from flask           import Flask, request, send_file, make_response, jsonify
from DB.db_connector import *


# Create Flask Instance #
web_app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "HTML_Files"))


@web_app.route("/users/get_user_name/<user_id>")
def get_user_name(user_id):
    """
    :explanations:
    - Get `user_name` from DB by searching `user_id` in users table.

    :param user_id: (str).

    :return: HTML Format.
    """
    is_mysql_container = get_from_jenkins_arguments().is_mysql_container
    user_name          = get_user_name_of_specific_user_id_from_users_table(user_id, is_mysql_container)

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
        if platform.system() == "Windows":
            os.kill(pid, signal.CTRL_C_EVENT)
        elif platform.system() == 'Darwin' or platform.system() == 'Linux':
            os.kill(pid, signal.SIGTERM)
        return True
    else:
        return False


@web_app.route('/stop_server', methods=['GET'])
def stop_web_app_server():
    """
    :explanations:
    - Stop running of WEB APP server.

    :return: response (Json), status_code (str)
    """
    if request.method == "GET":
        is_process_killed = kill_process()
        response          = make_response(jsonify(json.dumps({"status": "Server Stopped"}))) if is_process_killed is True else make_response(jsonify(json.dumps({"status": "Server Not Stopped"})))
        status_code       = 200 if is_process_killed is True else 500
        response.headers['Content-Type'] = 'application/json'
        return response, status_code


@web_app.errorhandler(404)
def page_not_found(exception):
    """
    :explanations:
    - Send error when endpoint is invalid.
    - The `error handler` is 404.

    :param exception: (str).

    :return: error_result (Json).
    """
    print(f"\n[Page Not Found] : {exception}")
    return send_file(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "HTML_Files", "error_handler_404.html")), 404


# Run Flask Application #
web_app.run(host=get_web_host_bind(), debug=True, port=get_web_port())
