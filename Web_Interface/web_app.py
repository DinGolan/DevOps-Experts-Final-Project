#########################
# WEB Interface Section #
#########################


# From #
from flask           import Flask
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
    user_name = get_user_name_from_db(user_id)

    if user_name is not None:
        return "<h1 id='user'>" + "`user name` is : " + user_name + "</h1>", 200
    else:
        return "<h1 id='error'>" + "No such `user id` : " + str(user_id) + "</h1>", 200


# Run Flask Application #
app.run(host=json_data['web_app.py']['HOST_WEB'], debug=True, port=json_data['web_app.py']['PORT_WEB'])
