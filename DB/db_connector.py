##############
# DB Section #
##############


# Imports #
import sys
import pymysql
import datetime
import itertools


# From #
from beautifultable import BeautifulTable


# GLOBAL VARS #
HOST              = "sql.freedb.tech"
PORT              = 3306
USER              = "freedb_Din_Golan"
PASSWORD          = "6G24*7bAr5KaU3G"
SCHEMA_NAME       = "freedb_Din_Golan"
USERS_TABLE_NAME  = "users"
CONFIG_TABLE_NAME = "config"


##############
# Connection #
##############
def create_connection_to_db():
    """
    :explanations:
    - Create connection to DB.

    :return: connection: (pymysql), cursor: (pymysql).
    """
    try:
        connection = pymysql.connect(host=HOST, port=PORT, user=USER, passwd=PASSWORD, db=SCHEMA_NAME)
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


#########
# Users #
#########
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
        statementToExecute = f"CREATE TABLE IF NOT EXISTS`{SCHEMA_NAME}`.`{USERS_TABLE_NAME}` " + \
                             "(`user_id` INT NOT NULL, `user_name` VARCHAR(50) NOT NULL, `creation_date` DATETIME NOT NULL, PRIMARY KEY (`user_id`));"
        cursor.execute(statementToExecute)

    except pymysql.err.ProgrammingError as programming_exception:
        print(f"\nError : You can't create users table because - {programming_exception} ...\n")
        return False

    except  pymysql.Error as error_exception:
        print(f"\nError : You can't create users table because - {error_exception} ...\n")
        return False

    finally:
        # Close connection #
        close_connection_of_db(connection, cursor)

    # Creation of Table - Succeed #
    return True


def insert_new_user_to_table(user_id, user_name, creation_date):
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
        statementToExecute = f"INSERT into {SCHEMA_NAME}.{USERS_TABLE_NAME} " \
                             f"(user_id, user_name, creation_date) "          \
                             f"VALUES ('{user_id}', '{user_name}', '{creation_date}')"
        cursor.execute(statementToExecute)

    except pymysql.err.IntegrityError as integrity_exception:
        print(f"\nError : Row with Primary Key = {user_id} already exists in the table, you can't insert because - {integrity_exception} ...\n")
        return False

    finally:
        # Close connection #
        close_connection_of_db(connection, cursor)

    # Insert - Succeed #
    return True


def delete_user_from_table(user_id):
    """
    :explanations:
    - Delete current user from users table.

    :param: user_id: (str).

    :return: True: Succeed.
             False: Not Succeed.
    """
    # Establishing a connection to DB #
    connection, cursor = create_connection_to_db()

    try:
        # Delete row from table #
        statementToExecute = f"DELETE FROM {SCHEMA_NAME}.{USERS_TABLE_NAME} " \
                             f"WHERE user_id = '{user_id}'"
        cursor.execute(statementToExecute)

    except pymysql.Error as error_exception:
        print(f"\nError : Row with Primary Key = {user_id} can't deleted because - {error_exception} ...\n")
        return False

    finally:
        # Close connection #
        close_connection_of_db(connection, cursor)

    # Delete - Succeed #
    return True


def drop_users_table():
    """
    :explanations:
    - Drop users table.

    :return: None.
    """
    # Establishing a connection to DB #
    connection, cursor = create_connection_to_db()

    try:
        # Delete table from DB #
        statementToExecute = f"DROP TABLE {SCHEMA_NAME}.{USERS_TABLE_NAME};"
        cursor.execute(statementToExecute)

    except pymysql.Error as error_exception:
        print(f"\nError : Can't delete table for DB because - {error_exception} ...\n")

    finally:
        # Close connection #
        close_connection_of_db(connection, cursor)


def get_user_name_from_db(user_id):
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
        statementToExecute = f"SELECT {column_table} "                 \
                             f"FROM {SCHEMA_NAME}.{USERS_TABLE_NAME} " \
                             f"WHERE user_id = '{user_id}';"
        cursor.execute(statementToExecute)
        user_name = cursor.fetchone()[0]

    except pymysql.Error as error_exception:
        print(f"\nError : Can't iterate on the table {USERS_TABLE_NAME} because - {error_exception} ...\n")
        return None

    finally:
        # Close connection #
        close_connection_of_db(connection, cursor)

    return user_name


def get_user_ids_from_db(user_name):
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
        statementToExecute = f"SELECT {column_table} "                 \
                             f"FROM {SCHEMA_NAME}.{USERS_TABLE_NAME} " \
                             f"WHERE user_name = '{user_name}';"
        cursor.execute(statementToExecute)
        user_ids = cursor.fetchall()
        user_ids = [user_tuple[0] for user_tuple in user_ids]

    except pymysql.Error as error_exception:
        print(f"\nError : Can't iterate on the table {USERS_TABLE_NAME} because - {error_exception} ...\n")
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


def get_new_user_id(user_id):
    """
    :explanations:
    - Check if `user_id` already exist (If `user_id` exists already, we will give him another ID).

    :param: user_id: (str).

    :return: new_user_id (int).
    """
    sql_query    = f"SELECT user_id " \
                     f"FROM {SCHEMA_NAME}.{USERS_TABLE_NAME};"
    query_result = run_sql_query(sql_query)
    query_result = list(itertools.chain(*query_result))

    # Default Value #
    new_user_id  = user_id

    if len(query_result) > 0:
        for idx in range(1, max(query_result)):
            if idx not in query_result:
                new_user_id = idx
                break
        else:
            new_user_id = max(query_result) + 1

    return new_user_id


##########
# Config #
##########
def create_config_table():
    """
    :explanations:
    - Create another table (in DB) and call it config, the table will contain :
      * The API gateway URL (e.g: 127.0.0.1:5001/users)
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
        statementToExecute = f"CREATE TABLE IF NOT EXISTS`{SCHEMA_NAME}`.`{CONFIG_TABLE_NAME}` " \
                             f"(`url` VARCHAR(50) NOT NULL, `browser` VARCHAR(50) NOT NULL, `user_id` INT NOT NULL, `user_name` VARCHAR(50) NOT NULL, PRIMARY KEY (`user_id`));"
        cursor.execute(statementToExecute)

    except pymysql.err.ProgrammingError as programming_exception:
        print(f"\nError : You can't create users table because - {programming_exception} ...\n")

    except  pymysql.Error as error_exception:
        print(f"\nError : You can't create users table because - {error_exception} ...\n")

    finally:
        # Close connection #
        close_connection_of_db(connection, cursor)


def insert_rows_to_config_table():
    """
    :explanations:
    - Insert new rows to config table.

    :return: None.
    """
    # Vars #
    idx        = 0
    user_names = []
    browser    = "Chrome"

    # Get Names of Users #
    while True:
        user_name = input("Please enter `user name` to `config` table. To stop enter details please enter `-1` : ")
        if user_name == "-1": break
        user_names.append(user_name)
        print()

    # Get number of rows from config table #
    number_of_rows = count_rows_from_table(CONFIG_TABLE_NAME)

    # Establishing a connection to DB #
    connection, cursor = create_connection_to_db()

    user_id = number_of_rows + 1
    while idx < len(user_names):
        url     = f"http://127.0.0.1:5000/{USERS_TABLE_NAME}/{user_id}"
        try:
            # Inserting data into table #
            statementToExecute = f"INSERT into {SCHEMA_NAME}.{CONFIG_TABLE_NAME} " \
                                 f"(url, browser, user_id, user_name) "            \
                                 f"VALUES ('{url}', '{browser}', '{user_id}', '{user_names[idx]}')"
            cursor.execute(statementToExecute)
            idx            += 1
            number_of_rows += 1

        except pymysql.err.IntegrityError as integrity_exception:
            print(f"\nError : Row with Primary Key = {user_id} already exists in the table, you can't insert because - {integrity_exception} ...\n")

        # Update `user_id` for next row #
        user_id += 1

    # Close connection #
    close_connection_of_db(connection, cursor)

    # Extreme Case - If `config` table is empty #
    if number_of_rows == 0:
        raise Exception(f"\nError : {CONFIG_TABLE_NAME} table can't be empty ...\n")


############
# Generals #
############
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
        statementToExecute = f"UPDATE {SCHEMA_NAME}.{table_name} " \
                             f"SET user_name = '{new_user_name}' " \
                             f"WHERE user_id = '{user_id}'"
        cursor.execute(statementToExecute)

    except pymysql.Error as error_exception:
        print(f"\nError : Row with Primary Key = {user_id} can't updated because - {error_exception} ...\n")
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
                             f"FROM {SCHEMA_NAME}.{table_name};"
        cursor.execute(statementToExecute)

    except pymysql.Error as error_exception:
        print(f"\nError : Can't iterate on the table {USERS_TABLE_NAME} because - {error_exception} ...\n")
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
                f"FROM {SCHEMA_NAME}.{table_name};"
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
