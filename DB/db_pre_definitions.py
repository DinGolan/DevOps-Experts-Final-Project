#########################
# Generals - DB Section #
#########################


# Imports #
import os
import sys


# Sys Path #
package_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(package_path)


# From #
from Config.config import *
from db_connector  import drop_table, create_config_table, is_table_exist_in_db, insert_rows_to_config_table, create_users_table, insert_rows_to_users_table


def db_pre_definitions():

    # Vars #
    is_config_table_exist = is_table_exist_in_db(table_name=get_db_config_table_name(), isDocker="True")
    is_users_table_exist  = is_table_exist_in_db(table_name=get_db_users_table_name() , isDocker="True")

    ###########################
    # Drop Tables (If Exists) #
    ###########################
    if is_config_table_exist is True: drop_table(table_name=get_db_config_table_name(), isDocker="True")
    if is_users_table_exist  is True: drop_table(table_name=get_db_users_table_name() , isDocker="True")

    ##################
    # Config Details #
    ##################
    # Create config table inside MySQL DB #
    create_config_table(isDocker="True")

    # Insert rows to config table inside MySQL DB #
    insert_rows_to_config_table(is_job_run="True", test_name="Backend", isDocker="True")

    ################
    # User Details #
    ################
    # Create users table inside MySQL DB #
    create_users_table(isDocker="True")

    # Insert rows to users table inside MySQL DB #
    insert_rows_to_users_table(isDocker="True")


if __name__ == "__main__":
    db_pre_definitions()
