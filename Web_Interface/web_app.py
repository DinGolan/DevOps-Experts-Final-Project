#########################
# WEB Interface Section #
#########################


# Imports #
import os
import sys
import signal
package_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(package_path)


# From #
from flask           import Flask, make_response
from DB.db_connector import *


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


@app.route('/stop_server')
def stop_server():
    """
    :explanations:
    - Stop running of WEB APP server.

    :return: response (Json), 200 (Status code)
    """
    os.kill(os.getpid(), signal.CTRL_C_EVENT)
    response = json.dumps({"status": "Server Stopped"})
    return response, 200


# Run Flask Application #
app.run(host=get_web_host(), debug=True, port=get_web_port())
