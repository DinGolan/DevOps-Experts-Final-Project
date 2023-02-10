####################
# REST API Section #
####################


# Imports #
import os
import re
import sys
import signal
import psutil
import platform


# Sys Path #
package_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(package_path)


# From #
from flask import Flask, make_response, request, send_file, jsonify
from DB.db_connector import *


# Create Flask Instance #
rest_app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "HTML_Files"))


@rest_app.route("/users/<user_id>", methods=['GET', 'POST', 'PUT', 'DELETE'])
def rest_api_requests(user_id):
    """
    :explanations:
    - Some types of requests - [GET, POST, PUT, DELETE].

    :param user_id: (str).

    :return: Json format.
    """
    if request.method == "POST":
        request_data  = request.json
        user_name     = request_data.get('user_name')
        isDocker      = "True" if request_data.get('isDocker') is not None else "False"
        creation_date = get_user_creation_date()
        insert_result = insert_new_user_to_users_table(user_id, user_name, creation_date, isDocker) and insert_new_user_to_config_table(user_id, user_name, isDocker)

        if insert_result is False:
            response    = make_response(jsonify({"status": "error", "reason": "ID Already Exists"}))
            status_code = 500
        else:
            response = make_response(jsonify({"status": "OK", "user_added": user_name}))
            status_code = 200

        response.headers['Content-Type'] = 'application/json'
        return response, status_code

    elif request.method == "GET":
        if request.is_json:
            request_data = request.json
            isDocker     = "True" if request_data.get('isDocker') is not None else "False"
        else:
            if   is_table_exist_in_db(get_db_users_table_name(), isDocker="True"):  isDocker = "True"
            elif is_table_exist_in_db(get_db_users_table_name(), isDocker="False"): isDocker = "False"
            else:
                response = make_response(jsonify({"status": "error", "reason": "Tables not exist in DB ---> No such ID - " + user_id}))
                status_code = 500
                return response, status_code

        user_name    = get_user_name_of_specific_user_id_from_users_table(user_id, isDocker)

        if user_name is None:
            response    = make_response(jsonify({"status": "error", "reason": "No such ID - " + user_id}))
            status_code = 500
        else:
            response    = make_response(jsonify({"status": "OK", "user_name": user_name}))
            status_code = 200

        response.headers['Content-Type'] = 'application/json'
        return response, status_code

    elif request.method == "PUT":
        request_data  = request.json
        new_user_name = request_data.get('new_user_name')
        isDocker      = "True" if request_data.get('isDocker') is not None else "False"
        update_result = update_user_in_table(user_id, new_user_name, get_db_users_table_name(), isDocker) and update_user_in_table(user_id, new_user_name, get_db_config_table_name(), isDocker)

        if update_result is False:
            response    = make_response(jsonify({"status": "error", "reason": f"No such ID - {user_id}"}))
            status_code = 500
        else:
            response    = make_response(jsonify({"status": "OK", "user_updated": new_user_name}))
            status_code = 200

        response.headers['Content-Type'] = 'application/json'
        return response, status_code

    elif request.method == "DELETE":
        request_data  = request.json
        isDocker      = "True" if request_data.get('isDocker') is not None else "False"
        delete_result = delete_user_from_table(user_id, get_db_users_table_name(), isDocker) and delete_user_from_table(user_id, get_db_config_table_name(), isDocker)

        if delete_result is False:
            response    = make_response(jsonify({"status": "error", "reason": f"No such ID - {user_id}"}))
            status_code = 500
        else:
            response    = make_response(jsonify({"status": "OK", "user_deleted": user_id}))
            status_code = 200

        response.headers['Content-Type'] = 'application/json'
        return response, status_code


@rest_app.route("/users/get_all_users", methods=['GET'])
def get_all_users_request():
    """
    :explanations:
    - Return json format of all users from `users` table.

    :return: Json format.
    """
    if request.method == "GET":
        request_data      = request.json
        isDocker          = "True" if request_data.get('isDocker') is not None else "False"
        all_users_as_json = get_all_users_as_json(isDocker)

        if all_users_as_json is not None:
            all_users_as_json = json.loads(all_users_as_json)
            response          = make_response(jsonify(all_users_as_json))
            status_code       = 200
        else:
            response    = make_response(jsonify({"status": "error", "reason": "no such Table or users don't exits in DB"}))
            status_code = 500

        response.headers['Content-Type'] = 'application/json'
        return response, status_code


def kill_process():
    """
    :explanations:
    - Kill the current process.

    :return: True  - If process is still running.
             False - If process not running anymore.
    """
    # Vars #
    pid          = os.getpid()
    process_name = psutil.Process(pid).name()
    print(f"The process name is : {process_name} ...")

    if re.search(r'python[0-9.]*[ex]*', process_name) or process_name in ["python.exe", "/usr/bin/python", "/usr/local/bin/python"]:
        if platform.system() == "Windows":
            os.kill(pid, signal.CTRL_C_EVENT)
        elif platform.system() == 'Darwin' or platform.system() == 'Linux':
            os.kill(pid, signal.SIGTERM)
        return True
    else:
        return False


@rest_app.route('/stop_server', methods=['GET'])
def stop_rest_api_server():
    """
    :explanations:
    - Stop running of REST API server.r

    :return: response (Json), status_code (str)
    """
    if request.method == "GET":
        is_process_killed = kill_process()
        response          = make_response(jsonify(json.dumps({"status": "Server Stopped"}))) if is_process_killed is True else make_response(jsonify(json.dumps({"status": "Server Not Stopped"})))
        status_code       = 200 if is_process_killed is True else 500
        response.headers['Content-Type'] = 'application/json'
        return response, status_code


@rest_app.errorhandler(404)
def page_not_found(exception):
    """
    :explanations:
    - Send error when endpoint (Web Page) is invalid.
    - The `error handler` is 404.

    :param exception: (str).

    :return: error_result (Json).
    """
    print(f"\n[Page Not Found] : {exception}")
    return send_file(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "HTML_Files", "error_handler_404.html")), 404


# Run Flask Application #
rest_app.run(host=get_rest_host_bind(), debug=True, port=get_rest_port())
