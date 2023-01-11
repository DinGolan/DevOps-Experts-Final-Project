#########################
# Generals - DB Section #
#########################


# Imports #
import os
import sys
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
def create_connection_to_db():
    """
    :explanations:
    - Create connection to DB.

    :return: connection: (pymysql), cursor: (pymysql).
    """
    try:
        connection = pymysql.connect(host=get_db_host(), port=get_db_port(), user=get_from_jenkins_arguments().user_name, passwd=get_from_jenkins_arguments().password, db=get_db_schema_name())
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
def get_details_from_external_user_for_backend(request_type, test_name):
    """
    :explanations:
    - Get from external user some details.

    :param: request_type (str).
    :param: test_name (str).

    :return: [POST] user_name_backend_test (str).
             [GET, PUT, DELETE] url (str), user_id_backend_test (str).
             [GET_ALL] url (str).
    """
    while True:
        if   request_type == "POST":
            user_name_backend_test = input("\nPlease enter `user name` : ")
            return user_name_backend_test

        elif request_type in ["GET", "PUT", "DELETE"]:
            user_id_backend_test = int(input("\nPlease enter `user id` : "))
            sql_query               = f"SELECT url "                                                   \
                                      f"FROM `{get_db_schema_name()}`.`{get_db_config_table_name()}` " \
                                      f"WHERE user_id = '{user_id_backend_test}';"
            query_result            = run_sql_query(sql_query)
            query_result            = list(itertools.chain(*query_result))

            if len(query_result) == 0:
                print(f"\n[{test_name} Test] : (`user_id` = {user_id_backend_test}) not exist in `{get_db_config_table_name()}` table ...\n")
                print(f"\n[{test_name} Test] : The `users_ids` that exists in the `{get_db_config_table_name()}` table are : {str(get_all_users_ids_from_config_table())} ...\n")
                continue

            url = "".join(query_result)
            return url, user_id_backend_test

        # GET_ALL #
        else:
            url = f"http://{get_rest_host()}:{get_rest_port()}/{get_db_users_table_name()}/get_all_users"
            return url


def get_details_from_external_user_for_frontend(test_name, user_id_frontend_test = None):
    """
    :explanations:
    - Get from external user some details.

    :param: test_name (str).
    :param: user_id_frontend_test (str).

    :return: url (str), browser(str).
    """
    while True:

        if user_id_frontend_test is None:
            user_id_frontend_test = int(input("\nPlease enter `user id` : "))

        sql_query               = f"SELECT url, browser "                                          \
                                  f"FROM `{get_db_schema_name()}`.`{get_db_config_table_name()}` " \
                                  f"WHERE user_id = '{user_id_frontend_test}';"
        query_result            = run_sql_query(sql_query)
        query_result            = list(itertools.chain(*query_result))

        if len(query_result) == 0:
            print(f"\n[{test_name} Test] : (`user_id` = {user_id_frontend_test}) not exist in `{get_db_config_table_name()}` table ...\n")
            print(f"\n[{test_name} Test] : The `users_ids` that exists in the `{get_db_config_table_name()}` table are : {str(get_all_users_ids_from_config_table())} ...\n")
            continue

        url, browser = query_result
        browser      = browser.lower()
        return url, browser


def update_user_in_table(user_id, new_user_name, table_name):
    """
    :explanations:
    - Update current user from users table.

    :param user_id: (str).
    :param new_user_name: (str).
    :param table_name: (str).

    :return: True: Succeed.
             False: Not Succeed.
    """

    # Establishing a connection to DB #
    connection, cursor = create_connection_to_db()

    try:
        # Update row in the table #
        statementToExecute = f"UPDATE `{get_db_schema_name()}`.`{table_name}` " \
                             f"SET user_name = '{new_user_name}' " \
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


def count_rows_from_table(table_name):
    """
    :explanations:
    - Count number of rows from users table.

    :return: cursor.rowcount (int).
    """
    # Establishing a connection to DB #
    connection, cursor = create_connection_to_db()

    # Column to search #
    column_table = "*"

    try:
        statementToExecute = f"SELECT {column_table} " \
                             f"FROM `{get_db_schema_name()}`.`{table_name}`;"
        cursor.execute(statementToExecute)

    except pymysql.Error as error_exception:
        print(f"\nError : Can't iterate on the table `{table_name}` table because - {error_exception} ...\n")
        return None

    finally:
        # Close connection #
        close_connection_of_db(connection, cursor)

    return cursor.rowcount


def run_sql_query(sql_query):
    """
    :explanations:
    - Run MySQL Query.

    :param sql_query: (str).

    :return: query_result (list).
    """
    # Establishing a connection to DB #
    connection, cursor = create_connection_to_db()

    # Execute Query #
    cursor.execute(sql_query)
    query_result = list()

    for idx in range(cursor.rowcount):
        row = cursor.fetchone()
        query_result.append(row)

    # Close connection #
    close_connection_of_db(connection, cursor)

    return query_result


def print_table(table_name):
    """
    :explanations:
    - Print the content of table.

    :param table_name: (str)

    :return: None.
    """
    # Establishing a connection to DB #
    connection, cursor = create_connection_to_db()

    sql_query = f"SELECT * " \
                f"FROM `{get_db_schema_name()}`.`{table_name}`;"
    cursor.execute(sql_query)

    beautiful_table = BeautifulTable()
    beautiful_table.columns.header = ["user id", "user name", "creation date"] if table_name == "users" else ["url", "browser", "user id", "user name"]

    for row in cursor.fetchall():
        if type(row[2]) == datetime.datetime:
            beautiful_table.append_row((row[0], row[1], str(row[2])))
        else:
            beautiful_table.append_row(row)

    print(beautiful_table)

    # Close connection #
    close_connection_of_db(connection, cursor)


def delete_user_from_table(user_id, table_name):
    """
    :explanations:
    - Delete current user from table.

    :param: user_id: (str).
    :param: table_name (str).

    :return: True: Succeed.
             False: Not Succeed.
    """
    # Establishing a connection to DB #
    connection, cursor = create_connection_to_db()

    try:
        # Delete row from table #
        statementToExecute = f"DELETE FROM `{get_db_schema_name()}`.`{table_name}` " \
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


def drop_table(table_name):
    """
    :explanations:
    - Drop table from MySQL DB.

    :param table_name: (str).

    :return: None.
    """
    # Establishing a connection to DB #
    connection, cursor = create_connection_to_db()

    try:
        sql_query = f"DROP TABLE IF EXISTS `{get_db_schema_name()}`.`{table_name}`;"
        cursor.execute(sql_query)

    except  pymysql.Error as error_exception:
        print(f"\nError : You can't drop `{get_db_config_table_name()}` table because - {error_exception} ...\n")
        sys.exit(1)

    finally:
        # Close connection #
        close_connection_of_db(connection, cursor)


######################
# Users - DB Section #
######################
def create_users_table():
    """
    :explanations:
    - Create table in the DB.
    - Users table will have 3 columns :
    * user_id – primary key, int, not null.
    * user_name - varchar[50], not null.
    * creation_date – varchar[50] which will store user creation date (in any format).

    :return: True: Succeed.
             False: Not Succeed.
    """
    # Establishing a connection to DB #
    connection, cursor = create_connection_to_db()

    try:
        # Create Table #
        statementToExecute = f"CREATE TABLE IF NOT EXISTS `{get_db_schema_name()}`.`{get_db_users_table_name()}` " + \
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


def insert_rows_to_users_table():
    """
    :explanations:
    - Insert new rows to users table.

    :return: None.
    """
    # Vars #
    users_ids      = []
    users_names    = []
    creation_dates = []

    # Establishing a connection to DB #
    connection, cursor = create_connection_to_db()

    # Column to search #
    column_table = "*"

    statementToExecute = f"SELECT {column_table} " \
                         f"FROM `{get_db_schema_name()}`.`{get_db_config_table_name()}`;"
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
    connection, cursor = create_connection_to_db()

    for user_id, user_name, creation_date in zip(users_ids, users_names, creation_dates):
        try:
            statementToExecute = f"INSERT into `{get_db_schema_name()}`.`{get_db_users_table_name()}` " \
                                 f"(user_id, user_name, creation_date) "                                \
                                 f"VALUES ('{user_id}', '{user_name}', '{creation_date}')"
            cursor.execute(statementToExecute)
        except pymysql.err.IntegrityError:
            continue # Raw with PK Already Exists #

    # Close connection #
    close_connection_of_db(connection, cursor)


def insert_new_user_to_users_table(user_id, user_name, creation_date):
    """
    :explanations:
    - Insert new row to users table.

    :param user_id: (str).
    :param user_name: (str).
    :param creation_date (str).

    :return: True: Succeed.
             False: Not Succeed.
    """
    # Establishing a connection to DB #
    connection, cursor = create_connection_to_db()

    try:
        # Inserting data into table #
        statementToExecute = f"INSERT into `{get_db_schema_name()}`.`{get_db_users_table_name()}` " \
                             f"(user_id, user_name, creation_date) "                                \
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


def get_user_name_of_specific_user_id_from_users_table(user_id):
    """
    :explanations:
    - Get `user_name` from DB by searching `user_id` in users table.

    :param user_id: (str).

    :return: user_name: (str).
             None: Not Succeed.
    """
    # Establishing a connection to DB #
    connection, cursor = create_connection_to_db()

    # Column to search #
    column_table = "user_name"

    try:
        statementToExecute = f"SELECT {column_table} "                                       \
                             f"FROM `{get_db_schema_name()}`.`{get_db_users_table_name()}` " \
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


def get_user_ids_of_specific_user_name_from_users_table(user_name):
    """
    :explanations:
    - Get `user_id` from DB by searching `user_name` in users table.

    :param: user_name (str).

    :return: user_ids: (str).
             None: Not Succeed.
    """
    # Establishing a connection to DB #
    connection, cursor = create_connection_to_db()

    # Column to search #
    column_table = "user_id"

    try:
        statementToExecute = f"SELECT {column_table} "                                       \
                             f"FROM `{get_db_schema_name()}`.`{get_db_users_table_name()}` " \
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


def get_new_user_id_from_users_table():
    """
    :explanations:
    - Return new `user_id` for new `user_name`.

    :return: new_user_id (int).
    """
    sql_query    = f"SELECT user_id " \
                   f"FROM `{get_db_schema_name()}`.`{get_db_users_table_name()}`;"
    query_result = run_sql_query(sql_query)
    query_result = list(itertools.chain(*query_result))

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


def get_all_users_as_json():
    """
    :explanations:
    - Get all users from `users` table, and return them in Json format.

    :return: users_as_json : (Json).
             None          : If we can't iterate over the table.
    """
    # Vars #
    all_users_as_json = []

    # Establishing a connection to DB #
    connection, cursor = create_connection_to_db()

    # PyPika SELECT #
    pypika_query = Query.from_(Schema(get_db_schema_name()).users).select('*')
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
def create_config_table():
    """
    :explanations:
    - Create another table (in DB) and call it config, the table will contain :
      * The API gateway URL (e.g: 127.0.0.1:5000/users)
      * The browser to test on (e.g: Chrome).
      * user id.
      * user name to be inserted.

    :return: True: Succeed.
             False: Not Succeed.
    """

    # Establishing a connection to DB #
    connection, cursor = create_connection_to_db()

    try:
        # Create Table #
        statementToExecute = f"CREATE TABLE IF NOT EXISTS `{get_db_schema_name()}`.`{get_db_config_table_name()}` " \
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


def insert_rows_to_config_table(is_job_run, test_name):
    """
    :explanations:
    - Insert new rows to config table.

    :param: is_job_run: (Boolean).
    :param: test_name: (str).

    :return: None.
    """
    # Vars #
    idx        = 0
    user_names = []
    browser    = "Chrome"

    # Get Names of Users #
    if is_job_run:
        if   test_name == "Backend" : user_names = get_users_names_in_static_way()[:10]
        elif test_name == "Frontend": user_names = get_users_names_in_static_way()[10:20]
        elif test_name == "Combined": user_names = get_users_names_in_static_way()[20:40]

    else:
        while True:
            user_name = input("Please enter `user name` to `config` table. To stop enter details please enter `-1` : ")
            if user_name == "-1": break
            user_names.append(user_name)
            print()

    # Get number of rows from config table #
    number_of_rows = count_rows_from_table(get_db_config_table_name())

    # Establishing a connection to DB #
    connection, cursor = create_connection_to_db()

    user_id = number_of_rows + 1
    while idx < len(user_names):
        url = f"http://{get_rest_host()}:{get_rest_port()}/{get_db_users_table_name()}/{user_id}"
        try:
            # Inserting data into table #
            statementToExecute = f"INSERT into `{get_db_schema_name()}`.`{get_db_config_table_name()}` " \
                                 f"(url, browser, user_id, user_name) "            \
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


def insert_new_user_to_config_table(user_id, user_name):
    """
    :explanations:
    - Insert new row to config table.

    :param user_id: (str).
    :param user_name: (str).

    :return: True: Succeed.
             False: Not Succeed.
    """
    # Establishing a connection to DB #
    connection, cursor = create_connection_to_db()

    try:
        # Inserting data into table #
        url     = f"http://{get_rest_host()}:{get_rest_port()}/{get_db_users_table_name()}/{user_id}"
        browser = "Chrome"
        statementToExecute = f"INSERT into `{get_db_schema_name()}`.`{get_db_config_table_name()}` " \
                             f"(url, browser, user_id, user_name) "                                  \
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


def get_all_users_ids_from_config_table():
    """
    :explanations:
    - Return all users id's.

    :return: user_ids (list).
    """
    # Establishing a connection to DB #
    connection, cursor = create_connection_to_db()

    # Column to search #
    column_table = "user_id"

    statementToExecute = f"SELECT {column_table} " \
                         f"FROM `{get_db_schema_name()}`.`{get_db_config_table_name()}`;"
    cursor.execute(statementToExecute)
    user_ids = cursor.fetchall()
    user_ids = list(itertools.chain(*user_ids))

    # Close connection #
    close_connection_of_db(connection, cursor)

    return user_ids


def get_all_users_ids_and_users_names_from_config_table():
    """
    :explanations:
    - Return all users details (user_id, user_name).

    :return: users_details (list).
    """

    # Establishing a connection to DB #
    connection, cursor = create_connection_to_db()

    statementToExecute = f"SELECT user_id, user_name " \
                         f"FROM `{get_db_schema_name()}`.`{get_db_config_table_name()}`;"
    cursor.execute(statementToExecute)
    users_details = cursor.fetchall()
    users_details = list(itertools.chain(*users_details))

    # Close connection #
    close_connection_of_db(connection, cursor)

    return users_details
