####################
# REST API Section #
####################


# From #
from flask           import Flask, request
from DB.db_connector import *


# Create Flask Instance #
app = Flask(__name__)


@app.route("/users/<user_id>", methods=['GET', 'POST', 'PUT', 'DELETE'])
def rest_api_requests(user_id):
    if request.method == "POST":
        request_data  = request.json                        # Getting the JSON data payload from request #
        user_name     = request_data.get('user_name')       # Treating request_data as a dictionary to get a specific value from key #
        new_user_id   = get_new_user_id(user_id)
        creation_date = get_user_creation_date()
        insert_result = insert_new_user_to_table(new_user_id, user_name, creation_date)

        if insert_result is False:
            return {"status": "error", "reason": "ID Already Exists"}, 500

        return {"status": "OK", "user_added": user_name}, 200

    elif request.method == "GET":
        user_name = get_user_name_from_db(user_id)

        if user_name is None:
            return {"status": "error", "reason": "no such ID"}, 500

        return {"status": "OK", "user_name": user_name}, 200

    elif request.method == "PUT":
        request_data  = request.json                                # Getting the JSON data payload from request #
        new_user_name = request_data.get('new_user_name')           # Treating request_data as a dictionary to get a specific value from key #
        update_result = update_user_in_table(user_id, new_user_name, json_data['db_connector.py']['USERS_TABLE_NAME']) and update_user_in_table(user_id, new_user_name, json_data['db_connector.py']['CONFIG_TABLE_NAME'])

        if update_result is False:
            return {"status": "error", "reason": "no such id"}, 500

        return {"status": "OK", "user_updated": new_user_name}, 200

    elif request.method == "DELETE":
        delete_result = delete_user_from_table(user_id)

        if delete_result is False:
            return {"status": "error", "reason": "no such id"}, 500

        return {"status": "OK", "user_deleted": user_id}, 200


# Run Flask Application #
app.run(host=json_data['rest_api.py']['HOST_REST'], debug=True, port=json_data['rest_api.py']['PORT_REST'])
