#########################
# Generals - DB Section #
#########################


# Imports #
import os
import sys
import time
import socket
import pymysql
import datetime
import itertools


# Sys Path #
package_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(package_path)


# From #
from Config.config  import *
from beautifultable import BeautifulTable
from pypika         import Schema, Query


###########################
# Connection - DB Section #
###########################
def wait_for_db(host, port):
    """
    :explanations:
    - Wait for connection to DB.

    :param: host: (string).
    :param: port: (string).

    :return: return True, when DB is connected.
    """
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
            return "Finish to Wait"

        except socket.error:
            time.sleep(1)


def create_connection_to_db(is_mysql_container, db_host = None):
    """
    :explanations:
    - Create connection to DB.

    :param: is_mysql_container: (str).
    :param: db_host: (str).

    :return: connection: (pymysql), cursor: (pymysql).
    """
    # Vars #
    schema_name = get_db_schema_name() if is_mysql_container == "False" else get_db_schema_name_container()
    if db_host is None:
        db_host = get_db_host() if is_mysql_container == "False" else get_db_host_container()

    if wait_for_db(db_host, get_db_port()) == "Finish to Wait":

        try:
            user_name = get_from_jenkins_arguments().user_name
            if user_name is None:
                user_name = get_db_user_name() if is_mysql_container == "False" else get_db_user_name_container()

            password = get_from_jenkins_arguments().password
            if password is None:
                password = get_db_password()

            connection = pymysql.connect(host=db_host, port=get_db_port(), user=user_name, passwd=password, db=schema_name)
            connection.autocommit(True)

            # Getting a cursor from DB #
            return connection, connection.cursor()

        except pymysql.Error as error_exception:
            print(f"\nError : {error_exception} ...\n")
            sys.exit(1)

        except TypeError as type_exception:
            print(f"\nError : {type_exception} ...\n")
            sys.exit(1)


def close_connection_of_db(connection, cursor):
    """
    :explanations:
    - Close connection of DB.

    :param: connection: (pymysql).
    :param: cursor: (pymysql).

    :return: None.
    """
    cursor.close()
    connection.close()


#########################
# Generals - DB Section #
#########################
def is_table_exist_in_db(table_name, is_mysql_container):
    """
    :explanations:
    - Check if table exist already in DB.

    :param: table_name: (str).
    :param: is_mysql_container: (str).

    :return: True - Table exist.
            False - Table not exist.
    """
    # Vars #
    is_table_exist = False
    db_tables_list = []

    # Establishing a connection to DB #
    connection, cursor = create_connection_to_db(is_mysql_container)
    sql_query          = "SHOW TABLES"
    cursor.execute(sql_query)

    if cursor.rowcount != 0:
        for table in [tables[0] for tables in cursor.fetchall()]:
            db_tables_list.append(table)

        if table_name not in db_tables_list:
            print(f"\nInfo : `{table_name}` table - Not Exist in DB ...\n")
        else:
            print(f"\nInfo : `{table_name}` table - Already Exist DB ...\n")
            is_table_exist = True

    # Close connection #
    close_connection_of_db(connection, cursor)

    return is_table_exist


def get_details_from_external_user_for_backend(request_type, test_name, is_mysql_container, is_k8s_url = "False"):
    """
    :explanations:
    - Get from external user some details.

    :param: request_type: (str).
    :param: test_name: (str).
    :param: is_mysql_container: (str).
    :param: is_k8s_url: (str).

    :return: [POST] user_name_backend_test (str).
             [GET, PUT, DELETE] url (str), user_id_backend_test (str).
             [GET_ALL] url (str).
    """
    # Vars #
    schema_name = get_db_schema_name() if is_mysql_container == "False" else get_db_schema_name_container()

    while True:
        if   request_type == "POST":
            user_name_backend_test = input("\nPlease enter `user name` : ")
            return user_name_backend_test

        elif request_type in ["GET", "PUT", "DELETE"]:
            user_id_backend_test = int(input("\nPlease enter `user id` : "))

            if is_k8s_url == "False":
                sql_query    = f"SELECT url "                                          \
                               f"FROM `{schema_name}`.`{get_db_config_table_name()}` " \
                               f"WHERE user_id = '{user_id_backend_test}';"
                query_result = run_sql_query(sql_query, is_mysql_container)
                query_result = list(itertools.chain(*query_result))

                if len(query_result) == 0:
                    print(f"\n[{test_name} Test] : (`user_id` = {user_id_backend_test}) not exist in `{get_db_config_table_name()}` table ...\n")
                    print(f"\n[{test_name} Test] : The `users_ids` that exists in the `{get_db_config_table_name()}` table are : {str(get_all_users_ids_from_config_table(is_mysql_container))} ...\n")
                    continue

                url = "".join(query_result)

            else:
                url = f"{get_k8s_url()}/{get_db_users_table_name()}/{user_id_backend_test}"

            return url, user_id_backend_test

        # GET_ALL #
        else:
            if is_k8s_url == "False":
                is_rest_api_container = get_from_jenkins_arguments().is_rest_api_container
                rest_host             = get_rest_host() if is_rest_api_container == "False" else get_rest_host_container()
                url                   = f"http://{rest_host}:{get_rest_port()}/{get_db_users_table_name()}/get_all_users"
            else:
                url                   = f"{get_k8s_url()}/{get_db_users_table_name()}/get_all_users"

            return url


def get_details_from_external_user_for_frontend(test_name, is_mysql_container, user_id_frontend_test = None):
    """
    :explanations:
    - Get from external user some details.

    :param: test_name: (str).
    :param: is_mysql_container: (str).
    :param: user_id_frontend_test: (str).

    :return: url (str), browser(str).
    """
    # Vars #
    schema_name = get_db_schema_name() if is_mysql_container == "False" else get_db_schema_name_container()

    while True:

        if user_id_frontend_test is None:
            user_id_frontend_test = int(input("\nPlease enter `user id` : "))

        sql_query    = f"SELECT url, browser "                                 \
                       f"FROM `{schema_name}`.`{get_db_config_table_name()}` " \
                       f"WHERE user_id = '{user_id_frontend_test}';"
        query_result = run_sql_query(sql_query, is_mysql_container)
        query_result = list(itertools.chain(*query_result))

        if len(query_result) == 0:
            print(f"\n[{test_name} Test] : (`user_id` = {user_id_frontend_test}) not exist in `{get_db_config_table_name()}` table ...\n")
            print(f"\n[{test_name} Test] : The `users_ids` that exists in the `{get_db_config_table_name()}` table are : {str(get_all_users_ids_from_config_table(is_mysql_container))} ...\n")
            continue

        url, browser = query_result
        browser      = browser.lower()
        return url, browser


def update_user_in_table(user_id, new_user_name, table_name, is_mysql_container):
    """
    :explanations:
    - Update current user from users table.

    :param: user_id: (str).
    :param: new_user_name: (str).
    :param: table_name: (str).
    :param: is_mysql_container: (str).

    :return: True: Succeed.
             False: Not Succeed.
    """

    # Establishing a connection to DB #
    connection, cursor = create_connection_to_db(is_mysql_container)

    try:
        # Update row in the table #
        schema_name        = get_db_schema_name() if is_mysql_container == "False" else get_db_schema_name_container()
        statementToExecute = f"UPDATE `{schema_name}`.`{table_name}` " \
                             f"SET user_name = '{new_user_name}' "     \
                             f"WHERE user_id = '{user_id}'"
        cursor.execute(statementToExecute)

    except pymysql.Error as error_exception:
        print(f"\nError : Row with Primary Key = `{user_id}` can't updated at `{table_name}` table because - {error_exception} ...\n")
        return False

    finally:
        # Close connection #
        close_connection_of_db(connection, cursor)

    # Update - Succeed #
    return True


def count_rows_from_table(table_name, is_mysql_container):
    """
    :explanations:
    - Count number of rows from users table.

    :param: is_mysql_container: (str).

    :return: cursor.rowcount (int).
    """
    # Establishing a connection to DB #
    connection, cursor = create_connection_to_db(is_mysql_container)

    # Column to search #
    column_table = "*"

    try:
        schema_name        = get_db_schema_name() if is_mysql_container == "False" else get_db_schema_name_container()
        statementToExecute = f"SELECT {column_table} " \
                             f"FROM `{schema_name}`.`{table_name}`;"
        cursor.execute(statementToExecute)

    except pymysql.Error as error_exception:
        print(f"\nError : Can't iterate on the table `{table_name}` table because - {error_exception} ...\n")
        return None

    finally:
        # Close connection #
        close_connection_of_db(connection, cursor)

    return cursor.rowcount


def run_sql_query(sql_query, is_mysql_container):
    """
    :explanations:
    - Run MySQL Query.

    :param: sql_query: (str).
    :param: is_mysql_container: (str).

    :return: query_result: (list).
    """
    # Establishing a connection to DB #
    connection, cursor = create_connection_to_db(is_mysql_container)

    # Execute Query #
    cursor.execute(sql_query)
    query_result = list()

    for idx in range(cursor.rowcount):
        row = cursor.fetchone()
        query_result.append(row)

    # Close connection #
    close_connection_of_db(connection, cursor)

    return query_result


def print_table(table_name, is_mysql_container):
    """
    :explanations:
    - Print the content of table.

    :param: table_name: (str).
    :param: is_mysql_container: (str).

    :return: None.
    """
    # Establishing a connection to DB #
    connection, cursor = create_connection_to_db(is_mysql_container)

    schema_name = get_db_schema_name() if is_mysql_container == "False" else get_db_schema_name_container()
    sql_query   = f"SELECT * " \
                  f"FROM `{schema_name}`.`{table_name}`;"
    cursor.execute(sql_query)

    beautiful_table = BeautifulTable()
    beautiful_table.columns.header = ["user id", "user name", "creation date"] if table_name == "users" else ["url", "browser", "user id", "user name"]

    for row in cursor.fetchall():
        if type(row[2]) == datetime.datetime:
            beautiful_table.append_row((row[0], row[1], str(row[2])))
        else:
            beautiful_table.append_row(row)

    print("#" * 10 if table_name == "config" else "#" * 9)
    print(f"# {table_name} #")
    print("#" * 10 if table_name == "config" else "#" * 9)
    print()
    print(beautiful_table)
    print()

    # Close connection #
    close_connection_of_db(connection, cursor)


def delete_user_from_table(user_id, table_name, is_mysql_container):
    """
    :explanations:
    - Delete current user from table.

    :param: user_id: (str).
    :param: table_name: (str).
    :param: is_mysql_container: (str).

    :return: True: Succeed.
             False: Not Succeed.
    """
    # Establishing a connection to DB #
    connection, cursor = create_connection_to_db(is_mysql_container)

    try:
        # Delete row from table #
        schema_name        = get_db_schema_name() if is_mysql_container == "False" else get_db_schema_name_container()
        statementToExecute = f"DELETE FROM `{schema_name}`.`{table_name}` " \
                             f"WHERE user_id = '{user_id}'"
        cursor.execute(statementToExecute)

    except pymysql.Error as error_exception:
        print(f"\nError : Row with Primary Key = {user_id} can't deleted in `{table_name}` table because - {error_exception} ...\n")
        return False

    finally:
        # Close connection #
        close_connection_of_db(connection, cursor)

    # Delete - Succeed #
    return True


def drop_table(table_name, is_mysql_container):
    """
    :explanations:
    - Drop table from MySQL DB.

    :param: table_name: (str).
    :param: is_mysql_container: (str).

    :return: None.
    """
    # Establishing a connection to DB #
    connection, cursor = create_connection_to_db(is_mysql_container)

    try:
        schema_name = get_db_schema_name() if is_mysql_container == "False" else get_db_schema_name_container()
        print(f"\nDROP TABLE : `{schema_name}`.`{table_name}`" + "\n")
        sql_query = f"DROP TABLE IF EXISTS `{schema_name}`.`{table_name}`;"
        cursor.execute(sql_query)

    except  pymysql.Error as error_exception:
        print(f"\nError : You can't drop `{get_db_config_table_name()}` table because - {error_exception} ...\n")
        sys.exit(1)

    finally:
        # Close connection #
        close_connection_of_db(connection, cursor)


def get_k8s_url():
    """
    :explanations:
    - Get K8S url.

    :return: k8s_url (str).
    """

    url_path   = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Testing", "k8s_url.txt")

    # Sleep Before Reading the File #
    time.sleep(10)

    if os.path.exists(url_path):
        """
        Notes :
        (1) From Jenkins - Need to remove `encoding="utf-16"` from `open` command.
        (2) From PyCharm - Need to add `encoding="utf-16"` to `open` command.
        """
        file_object = open(url_path, "r")
        all_lines   = [line_to_read for line_to_read in file_object.read().split("\n") if line_to_read != "" and line_to_read != "\n" and "#" not in line_to_read]
        file_object.close()

        # Return the most updated IP Address #
        if all_lines[-1].startswith("http") is True:
            return all_lines[-1]
        else:
            print("\nError : IP Address not exist in `k8s_url.txt`, please check it ..." + "\n")

            # Exit from program, we can't continue #
            exit(1)
    else:
        print("\nError : File not exist, You need to run the following commands :" + "\n" +
              "(1) minikube start"                                                 + "\n" +
              "(2) helm install helm-chart-testing .\\HELM\\ --set image.version=dingolan/devops_experts_final_project:rest_api_version_latest_3"             + "\n" +
              "(3) minikube service rest-api-application-service --url > Testing\\k8s_url.txt"                                                                + "\n" +
              "(4) python Testing\\k8s_backend_testing.py -u ${MYSQL_USER_NAME} -p ${MYSQL_PASSWORD} -i True -r GET -s ${IS_MYSQL_CONTAINER_FOR_K8S} -k ${IS_K8S_URL}" + "\n")

    # Exit from program, we can't continue #
    exit(1)


######################
# Users - DB Section #
######################
def create_users_table(is_mysql_container):
    """
    :explanations:
    - Create table in the DB.
    - Users table will have 3 columns :
    * user_id – primary key, int, not null.
    * user_name - varchar[50], not null.
    * creation_date – varchar[50] which will store user creation date (in any format).

    :param: is_mysql_container: (str).

    :return: True: Succeed.
             False: Not Succeed.
    """
    # Establishing a connection to DB #
    connection, cursor = create_connection_to_db(is_mysql_container)

    try:
        # Create Table #
        schema_name        = get_db_schema_name() if is_mysql_container == "False" else get_db_schema_name_container()
        statementToExecute = f"CREATE TABLE IF NOT EXISTS `{schema_name}`.`{get_db_users_table_name()}` " + \
                             f"(`user_id` INT NOT NULL, `user_name` VARCHAR(50) NOT NULL, `creation_date` DATETIME NOT NULL, PRIMARY KEY (`user_id`));"
        cursor.execute(statementToExecute)

    except pymysql.err.ProgrammingError as programming_exception:
        print(f"\nError : You can't create `{get_db_users_table_name()}` table because - {programming_exception} ...\n")
        sys.exit(1)

    except  pymysql.Error as error_exception:
        print(f"\nError : You can't create `{get_db_users_table_name()}` table because - {error_exception} ...\n")
        sys.exit(1)

    finally:
        # Close connection #
        close_connection_of_db(connection, cursor)


def insert_rows_to_users_table(is_mysql_container):
    """
    :explanations:
    - Insert new rows to users table.

    :param: is_mysql_container: (str).

    :return: None.
    """
    # Vars #
    users_ids      = []
    users_names    = []
    creation_dates = []

    # Establishing a connection to DB #
    connection, cursor = create_connection_to_db(is_mysql_container)

    # Column to search #
    column_table = "*"

    schema_name        = get_db_schema_name() if is_mysql_container == "False" else get_db_schema_name_container()
    statementToExecute = f"SELECT {column_table} " \
                         f"FROM `{schema_name}`.`{get_db_config_table_name()}`;"
    cursor.execute(statementToExecute)

    # Get `user_id`, `user_name` from `config` table #
    for row in cursor:
        user_id, user_name, creation_date = row[2], row[3], get_user_creation_date()
        users_ids.append(user_id)
        users_names.append(user_name)
        creation_dates.append(creation_date)

    # Close connection #
    close_connection_of_db(connection, cursor)

    # Establishing a connection to DB #
    connection, cursor = create_connection_to_db(is_mysql_container)

    for user_id, user_name, creation_date in zip(users_ids, users_names, creation_dates):
        try:
            statementToExecute = f"INSERT into `{schema_name}`.`{get_db_users_table_name()}` " \
                                 f"(user_id, user_name, creation_date) "                       \
                                 f"VALUES ('{user_id}', '{user_name}', '{creation_date}')"
            cursor.execute(statementToExecute)
        except pymysql.err.IntegrityError:
            continue # Raw with PK Already Exists #

    # Close connection #
    close_connection_of_db(connection, cursor)


def insert_new_user_to_users_table(user_id, user_name, creation_date, is_mysql_container):
    """
    :explanations:
    - Insert new row to users table.

    :param: user_id: (str).
    :param: user_name: (str).
    :param: creation_date: (str).
    :param: is_mysql_container: (str)

    :return: True: Succeed.
             False: Not Succeed.
    """
    # Establishing a connection to DB #
    connection, cursor = create_connection_to_db(is_mysql_container)

    try:
        # Inserting data into table #
        schema_name        = get_db_schema_name() if is_mysql_container == "False" else get_db_schema_name_container()
        statementToExecute = f"INSERT into `{schema_name}`.`{get_db_users_table_name()}` " \
                             f"(user_id, user_name, creation_date) "                       \
                             f"VALUES ('{user_id}', '{user_name}', '{creation_date}')"
        cursor.execute(statementToExecute)

    except pymysql.err.IntegrityError as integrity_exception:
        print(f"\nError : Row with Primary Key = {user_id} already exists in the `{get_db_users_table_name()}` table, you can't insert because - {integrity_exception} ...\n")
        return False

    finally:
        # Close connection #
        close_connection_of_db(connection, cursor)

    # Insert - Succeed #
    return True


def get_user_name_of_specific_user_id_from_users_table(user_id, is_mysql_container, db_host = None):
    """
    :explanations:
    - Get `user_name` from DB by searching `user_id` in users table.

    :param: user_id: (str).
    :param: is_mysql_container: (str).
    :param: db_host: (str).

    :return: user_name: (str).
             None: Not Succeed.
    """
    # Establishing a connection to DB #
    connection, cursor = create_connection_to_db(is_mysql_container, db_host)

    # Column to search #
    column_table = "user_name"

    try:
        schema_name        = get_db_schema_name() if is_mysql_container == "False" else get_db_schema_name_container()
        statementToExecute = f"SELECT {column_table} "                              \
                             f"FROM `{schema_name}`.`{get_db_users_table_name()}` " \
                             f"WHERE user_id = '{user_id}';"
        cursor.execute(statementToExecute)
        user_name = cursor.fetchone()[0]

    except pymysql.Error as error_exception:
        print(f"\nError : Can't iterate on the `{get_db_users_table_name()}` table because - {error_exception} ...\n")
        return None

    finally:
        # Close connection #
        close_connection_of_db(connection, cursor)

    return user_name


def get_user_ids_of_specific_user_name_from_users_table(user_name, is_mysql_container):
    """
    :explanations:
    - Get `user_id` from DB by searching `user_name` in users table.

    :param: user_name: (str).
    :param: is_mysql_container: (str).

    :return: user_ids: (str).
             None: Not Succeed.
    """
    # Establishing a connection to DB #
    connection, cursor = create_connection_to_db(is_mysql_container)

    # Column to search #
    column_table = "user_id"

    try:
        schema_name        = get_db_schema_name() if is_mysql_container == "False" else get_db_schema_name_container()
        statementToExecute = f"SELECT {column_table} "                              \
                             f"FROM `{schema_name}`.`{get_db_users_table_name()}` " \
                             f"WHERE user_name = '{user_name}';"
        cursor.execute(statementToExecute)
        user_ids = cursor.fetchall()
        user_ids = [user_tuple[0] for user_tuple in user_ids]

    except pymysql.Error as error_exception:
        print(f"\nError : Can't iterate on the `{get_db_users_table_name()}` table because - {error_exception} ...\n")
        return None

    finally:
        # Close connection #
        close_connection_of_db(connection, cursor)

    return user_ids


def get_user_creation_date():
    """
    :explanations:
    - Create date and return it.

    :return: creation_date (datetime.datetime).
    """
    date_format          = "%Y-%m-%d %H:%M:%S"
    creation_date_string = datetime.datetime.now().strftime(date_format)
    creation_date        = datetime.datetime.strptime(creation_date_string, date_format)
    return creation_date


def get_new_user_id_from_users_table(is_mysql_container):
    """
    :explanations:
    - Return new `user_id` for new `user_name`.

    :param: is_mysql_container: (str).

    :return: new_user_id (int).
    """
    schema_name        = get_db_schema_name() if is_mysql_container == "False" else get_db_schema_name_container()
    sql_query          = f"SELECT user_id " \
                         f"FROM `{schema_name}`.`{get_db_users_table_name()}`;"
    query_result       = run_sql_query(sql_query, is_mysql_container)
    query_result       = list(itertools.chain(*query_result))

    # Default Value #
    new_user_id = None

    if len(query_result) > 0:
        for idx in range(1, max(query_result)):
            if idx not in query_result:
                new_user_id = idx
                break
        else:
            new_user_id = max(query_result) + 1

    return new_user_id


def get_all_users_as_json(is_mysql_container, db_host):
    """
    :explanations:
    - Get all users from `users` table, and return them in Json format.

    :param: is_mysql_container: (str).
    :param: db_host: (str).

    :return: users_as_json : (Json).
             None          : If we can't iterate over the table.
    """
    # Vars #
    all_users_as_json  = []
    schema_name        = get_db_schema_name() if is_mysql_container == "False" else get_db_schema_name_container()

    # Establishing a connection to DB #
    connection, cursor = create_connection_to_db(is_mysql_container, db_host)

    # PyPika SELECT #
    pypika_query = Query.from_(Schema(schema_name).users).select('*')
    pypika_query = pypika_query.get_sql()
    pypika_query = pypika_query.replace('"', '')

    try:
        cursor.execute(pypika_query)

        if cursor.rowcount >= 1:
            query_result = cursor.fetchall()

            for row in query_result:
                all_users_as_json.append({"user_id": row[0], "user_name": row[1], "creation_date": str(row[2])})

            # Convert List to Json #
            return json.dumps(all_users_as_json)

        else:
            return None

    except pymysql.err.IntegrityError as integrity_exception:
        print(f"\nError : You can't iterate over `{get_db_users_table_name()}` table, because - {integrity_exception} ...\n")
        return None

    finally:
        # Close connection #
        close_connection_of_db(connection, cursor)


#######################
# Config - DB Section #
#######################
def create_config_table(is_mysql_container):
    """
    :explanations:
    - Create another table (in DB) and call it config, the table will contain :
      * The API gateway URL (e.g: 127.0.0.1:5000/users/1)
      * The browser to test on (e.g: Chrome).
      * user id.
      * user name to be inserted.

    :param: is_mysql_container: (str).

    :return: True: Succeed.
             False: Not Succeed.
    """

    # Establishing a connection to DB #
    connection, cursor = create_connection_to_db(is_mysql_container)

    try:
        # Create Table #
        schema_name        = get_db_schema_name() if is_mysql_container == "False" else get_db_schema_name_container()
        statementToExecute = f"CREATE TABLE IF NOT EXISTS `{schema_name}`.`{get_db_config_table_name()}` " \
                             f"(`url` VARCHAR(50) NOT NULL, `browser` VARCHAR(50) NOT NULL, `user_id` INT NOT NULL, `user_name` VARCHAR(50) NOT NULL, PRIMARY KEY (`user_id`));"
        cursor.execute(statementToExecute)

    except pymysql.err.ProgrammingError as programming_exception:
        print(f"\nError : You can't create `{get_db_config_table_name()}` table because - {programming_exception} ...\n")
        sys.exit(1)

    except  pymysql.Error as error_exception:
        print(f"\nError : You can't create `{get_db_config_table_name()}` table because - {error_exception} ...\n")
        sys.exit(1)

    finally:
        # Close connection #
        close_connection_of_db(connection, cursor)


def insert_rows_to_config_table(is_job_run, test_name, is_mysql_container, is_k8s_url = "False"):
    """
    :explanations:
    - Insert new rows to config table.

    :param: is_job_run: (Boolean).
    :param: test_name: (str).
    :param: is_mysql_container: (str).
    :param: is_k8s_url: (str).

    :return: None.
    """
    # Vars #
    idx        = 0
    user_names = []
    browser    = "Chrome"

    # Get Names of Users #
    if is_job_run == "True":
        if   test_name == "Backend" : user_names = get_users_names_in_static_way()[:10]
        elif test_name == "Frontend": user_names = get_users_names_in_static_way()[10:20]
        elif test_name == "Combined": user_names = get_users_names_in_static_way()[20:40]

    else:
        while True:
            user_name = input("\nPlease enter `user name` to `config` table. To stop enter details please enter `-1` : ")
            if user_name == "-1": break
            user_names.append(user_name)
            print()

    # Get number of rows from config table #
    number_of_rows = count_rows_from_table(get_db_config_table_name(), is_mysql_container)

    # Establishing a connection to DB #
    connection, cursor = create_connection_to_db(is_mysql_container)

    user_id               = number_of_rows + 1
    schema_name           = get_db_schema_name() if is_mysql_container == "False" else get_db_schema_name_container()
    is_rest_api_container = get_from_jenkins_arguments().is_rest_api_container
    rest_host             = get_rest_host() if is_rest_api_container == "False" else get_rest_host_container()

    while idx < len(user_names):
        if is_k8s_url == "False":
            url = f"http://{rest_host}:{get_rest_port()}/{get_db_users_table_name()}/{user_id}"
        else:
            url = f"{get_k8s_url()}/{get_db_users_table_name()}/{user_id}"

        try:
            # Inserting data into table #
            statementToExecute = f"INSERT into `{schema_name}`.`{get_db_config_table_name()}` " \
                                 f"(url, browser, user_id, user_name) "                         \
                                 f"VALUES ('{url}', '{browser}', '{user_id}', '{user_names[idx]}')"
            cursor.execute(statementToExecute)
            idx            += 1
            number_of_rows += 1

        except pymysql.err.IntegrityError as integrity_exception:
            print(f"\nError : Row with Primary Key = `{user_id}` already exists in `{get_db_config_table_name()}`, you can't insert because - {integrity_exception} ...\n")

        # Update `user_id` for next row #
        user_id += 1

    # Close connection #
    close_connection_of_db(connection, cursor)

    # Extreme Case - If `config` table is empty #
    if number_of_rows == 0:
        raise Exception(f"\nError : `{get_db_config_table_name()}` table can't be empty ...\n")


def insert_new_user_to_config_table(user_id, user_name, is_mysql_container, url):
    """
    :explanations:
    - Insert new row to config table.

    :param: user_id: (str).
    :param: user_name: (str).
    :param: is_mysql_container: (str).
    :param: url: (str).

    :return: True: Succeed.
             False: Not Succeed.
    """
    # Establishing a connection to DB #
    connection, cursor = create_connection_to_db(is_mysql_container)

    try:
        # Inserting data into table #
        browser               = "Chrome"
        schema_name           = get_db_schema_name() if is_mysql_container == "False" else get_db_schema_name_container()
        statementToExecute    = f"INSERT into `{schema_name}`.`{get_db_config_table_name()}` " \
                                f"(url, browser, user_id, user_name) "                         \
                                f"VALUES ('{url}', '{browser}', '{user_id}', '{user_name}')"
        cursor.execute(statementToExecute)

    except pymysql.err.IntegrityError as integrity_exception:
        print(f"\nError : Row with Primary Key = {user_id} already exists in the `{get_db_config_table_name()}` table, you can't insert because - {integrity_exception} ...\n")
        return False

    finally:
        # Close connection #
        close_connection_of_db(connection, cursor)

    # Insert - Succeed #
    return True


def get_all_users_ids_from_config_table(is_mysql_container):
    """
    :explanations:
    - Return all users id's.

    :param: is_mysql_container: (str).

    :return: user_ids (list).
    """
    # Establishing a connection to DB #
    connection, cursor = create_connection_to_db(is_mysql_container)

    # Column to search #
    column_table       = "user_id"
    schema_name        = get_db_schema_name() if is_mysql_container == "False" else get_db_schema_name_container()
    statementToExecute = f"SELECT {column_table} " \
                         f"FROM `{schema_name}`.`{get_db_config_table_name()}`;"
    cursor.execute(statementToExecute)
    user_ids = cursor.fetchall()
    user_ids = list(itertools.chain(*user_ids))

    # Close connection #
    close_connection_of_db(connection, cursor)

    return user_ids


def get_all_users_ids_and_users_names_from_config_table(is_mysql_container):
    """
    :explanations:
    - Return all users details (user_id, user_name).

    :param: is_mysql_container: (str).

    :return: users_details (list).
    """

    # Establishing a connection to DB #
    connection, cursor = create_connection_to_db(is_mysql_container)

    schema_name        = get_db_schema_name() if is_mysql_container == "False" else get_db_schema_name_container()
    statementToExecute = f"SELECT user_id, user_name " \
                         f"FROM `{schema_name}`.`{get_db_config_table_name()}`;"
    cursor.execute(statementToExecute)
    users_details = cursor.fetchall()
    users_details = list(itertools.chain(*users_details))

    # Close connection #
    close_connection_of_db(connection, cursor)

    return users_details
