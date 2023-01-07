##################
# Config Section #
##################


# Imports #
import os
import sys
import json


# Sys Path #
package_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(package_path)


# JSON #
json_file = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json"))
json_data = json.load(json_file)
json_file.close()


# Get JSON Data #
def get_web_host()            : return json_data["web_app.py"]["HOST_WEB"]
def get_web_port()            : return json_data["web_app.py"]["PORT_WEB"]
def get_rest_host()           : return json_data["rest_app.py"]["HOST_REST"]
def get_rest_port()           : return json_data["rest_app.py"]["PORT_REST"]
def get_db_host()             : return json_data["db_connector.py"]["HOST"]
def get_db_port()             : return json_data["db_connector.py"]["PORT"]
def get_db_user()             : return json_data["db_connector.py"]["USER"]
def get_db_password()         : return json_data["db_connector.py"]["PASSWORD"]
def get_db_schema_name()      : return json_data["db_connector.py"]["SCHEMA_NAME"]
def get_db_users_table_name() : return json_data["db_connector.py"]["USERS_TABLE_NAME"]
def get_db_config_table_name(): return json_data["db_connector.py"]["CONFIG_TABLE_NAME"]
