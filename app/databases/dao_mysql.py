#-------------------------------------------------------------------------------------------------
# This module will connect to mysql database and create database and tables and insert tables
# it will use a class as a wrapper for mysql connection and operations
# The following functions will be implemented in the class:
# 1. connect: to connect to mysql database
# 2. create_database: to create a database in mysql
# 3. create_table: to create a table in mysql database
# 4. show_table_ddl: to show the ddl of a table in mysql database
# 5. create_workflow_table: to create workflow table in mysql database
# 6. show_workflow_table_ddl: to show the ddl of workflow table in mysql database
# 7. insert_into_workflow_table: to insert a workflow into workflow table in mysql database
# 8. update_workflow_table: to update a workflow in workflow table in mysql database
# 9. delete_from_workflow_table: to delete a workflow from workflow table in mysql database
# 10. select_from_workflow_table: to select a workflow from workflow table in mysql database
# 11. select_all_from_workflow_table: to select all workflows from workflow table in mysql database
# 12. create_role_table: to create role table in mysql database
# 13. show_role_table_ddl: to show the ddl of role table in mysql database
# 14. insert_into_role_table: to insert a role into role table in mysql database
# 15. update_role_table: to update a role in role table in mysql database
# 16. delete_from_role_table: to delete a role from role table in mysql database
# 17. select_from_role_table: to select a role from role table in mysql database
# 18. select_all_from_role_table: to select all roles from role table in mysql
# 19. create_guard_table: to create guard table in mysql database
# 20. show_guard_table_ddl: to show the ddl of guard table in mysql database
# 21. insert_into_guard_table: to insert a guard into guard table in mysql database
# 22. update_guard_table: to update a guard in guard table in mysql database
# 23. delete_from_guard_table: to delete a guard from guard table in mysql database
# 24. select_from_guard_table: to select a guard from guard table in mysql database
# 25. select_all_from_guard_table: to select all guards from guard table in mysql database
# All functions should return return_code, error_message, data (if applicable)
# All foreign key relationships will be implemented in the create_table function for the respective tables 
#     with cascading updates and deletes where applicable.
#-------------------------------------------------------------------------------------------------
import logging
from functools import wraps
from typing import Any

import mysql.connector
import pymysql

from app.project_config import get_config

from .dao_base import BaseDAO


LOGGER = logging.getLogger(__name__)


def _summarize_value(value: Any) -> str:
    """Return a compact string representation suitable for DAO log messages."""
    if isinstance(value, str):
        truncated = value if len(value) <= 40 else f"{value[:37]}..."
        return repr(truncated)
    if isinstance(value, (list, tuple, set, dict)):
        return f"{type(value).__name__}(len={len(value)})"
    return repr(value)


def _format_call(args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
    """Format positional and keyword arguments for a compact DAO start log."""
    parts = [_summarize_value(arg) for arg in args]
    parts.extend(f"{key}={_summarize_value(value)}" for key, value in kwargs.items())
    return ", ".join(parts) if parts else "no arguments"


def _logged_dao_method(func):
    """Log DAO method start and failures while preserving the existing method behavior."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        method_name = f"{type(self).__name__}.{func.__name__}"
        LOGGER.info("[DAO START] %s(%s)", method_name, _format_call(args, kwargs))
        try:
            result = func(self, *args, **kwargs)
        except Exception as err:
            LOGGER.error("[DAO ERROR] %s raised %s", method_name, err)
            raise

        if isinstance(result, tuple) and len(result) >= 2:
            return_code, error_message = result[0], result[1]
            if return_code == -1 and error_message:
                LOGGER.error("[DAO ERROR] %s failed: %s", method_name, error_message)
        return result

    return wrapper


def _instrument_dao_methods(cls):
    """Decorate concrete DAO methods so they consistently log start and error events."""
    for name, value in list(cls.__dict__.items()):
        if name == "__init__" or name.startswith("__"):
            continue
        if callable(value):
            setattr(cls, name, _logged_dao_method(value))
    return cls

try:
    import mysql.connector as mysql_connector
    import mysql.connector.errors as mysql_errors
except ImportError:
    mysql_connector = None
    mysql_errors = None


class Errors:
    """Namespace that groups supported database exception types."""

    Error = tuple(
        error_type
        for error_type in (
            getattr(mysql_errors, "Error", None),
            pymysql.MySQLError,
        )
        if error_type is not None
    )


class _PyMySQLConnectionAdapter:
    """Adapter that makes a PyMySQL connection look like mysql-connector's API."""

    def __init__(self, connection: pymysql.connections.Connection):
        """Store the wrapped PyMySQL connection instance."""
        self._connection = connection

    def cursor(self, dictionary: bool = False):
        """Return a standard or dictionary-style cursor matching the requested mode."""
        if dictionary:
            return self._connection.cursor(pymysql.cursors.DictCursor)
        return self._connection.cursor()

    def ping(self, reconnect: bool = True, attempts: int = 1, delay: int = 0):
        """Ping the underlying connection, ignoring connector-specific extra arguments."""
        return self._connection.ping(reconnect=reconnect)

    def __getattr__(self, name: str):
        """Delegate unknown attribute access to the wrapped PyMySQL connection."""
        return getattr(self._connection, name)

#from sqlalchemy import table

# All functions should return return_code, error_message, data (if applicable)
@_instrument_dao_methods
class MySQLDatabase(BaseDAO):
    """MySQL-backed DAO implementation for workflow and interaction data."""

    def __init__(self, host=None, user=None, password=None, dbname=None, port=None, auth_plugin=None):
        """Initializes the MySQLDatabase instance with connection parameters.
        Args:
            host (str): Hostname or IP address of the MySQL server.
            user (str): Username for the MySQL server.
            password (str): Password for the MySQL server.
            dbname (str): Name of the database to connect to.
        """
        runtime_config = get_config()
        self.host = host or runtime_config.DB_HOST
        self.user = user or runtime_config.DB_USER
        self.password = password or runtime_config.DB_PASSWORD
        self.dbname = dbname or runtime_config.DB_NAME
        self.port = int(port if port is not None else runtime_config.DB_PORT)
        self.auth_plugin = auth_plugin if auth_plugin is not None else runtime_config.DB_AUTH_PLUGIN
        self.connection = None

    def connect(self)-> tuple[int, str, Any]:
        """Establishes a connection to the MySQL database.
        Returns:
            tuple: (return_code, error_message, connection)
                return_code (bool): True if connection is successful, False otherwise.
                error_message (str): Error message if connection fails, None otherwise.
                connection (mysql.connector.connection.MySQLConnection): MySQL connection object if successful, None otherwise.
        """
        connection_kwargs = {
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "password": self.password,
            "database": self.dbname,
        }
        if self.auth_plugin:
            connection_kwargs["auth_plugin"] = self.auth_plugin

        if mysql_connector is not None:
            try:
                self.connection = mysql_connector.connect(**connection_kwargs)
                logging.info("[*] Connected to MySQL database via mysql-connector-python.")
                return 0, None, self.connection
            except Errors.Error as err:
                error_message = str(err)
                if "Authentication plugin" not in error_message:
                    logging.error(f"[!] Error connecting to MySQL: {err}")
                    self.connection = None
                    return -1, error_message, None
                logging.warning(
                    "[!] mysql-connector-python could not handle the authentication plugin; "
                    "retrying with PyMySQL."
                )

        try:
            pymysql_kwargs = {
                "host": self.host,
                "port": self.port,
                "user": self.user,
                "password": self.password,
                "database": self.dbname,
                "autocommit": False,
            }
            self.connection = _PyMySQLConnectionAdapter(pymysql.connect(**pymysql_kwargs))
            logging.info("[*] Connected to MySQL database via PyMySQL.")
        except Errors.Error as err:
            logging.error(f"[!] Error connecting to MySQL: {err}")
            self.connection = None
            return -1, str(err), None
        return 0, None, self.connection

    def ensure_connection(self) -> tuple[int, str, None]:
        """Ensures there is a live connection, reconnecting when needed."""
        if not self.connection:
            logging.info("[*] No connection to MySQL. Attempting to connect...")
            connect_code, connect_error, _ = self.connect()
            if connect_code != 0:
                return -1, f"Connection failed: {connect_error}", None

        try:
            self.connection.ping(reconnect=True, attempts=3, delay=5)
        except Errors.Error as err:
            logging.warning(f"[!] Ping failed, reconnecting to MySQL: {err}")
            reconnect_code, reconnect_error, _ = self.connect()
            if reconnect_code != 0:
                return -1, f"Reconnection failed: {reconnect_error}", None

            try:
                self.connection.ping(reconnect=True, attempts=3, delay=5)
            except Errors.Error as second_err:
                return -1, f"Ping failed after reconnection: {second_err}", None

        return 0, None, None
    
    def ping(self) -> tuple[int, str, None]:
        """Pings the MySQL server to check if the connection is alive.
        Returns:
            tuple: (return_code, error_message, None)
                return_code (bool): True if ping is successful, False otherwise.
                error_message (str): Error message if ping fails, None otherwise.
                None: Always None.
        """
        ensure_code, ensure_error, _ = self.ensure_connection()
        if ensure_code != 0:
            logging.error(f"[!] Error pinging MySQL server: {ensure_error}")
            return -1, ensure_error, None

        logging.info("[*] Ping to MySQL server successful.")
        return 0, None, None
        
    def create_database(self) -> tuple[int, str, None]:
        """Creates a new database in the MySQL server.
        Returns:
            tuple: (return_code, error_message, None)
                return_code (bool): True if database is created successfully, False otherwise.
                error_message (str): Error message if database creation fails, None otherwise.
                None: Always None.
        """
        connection_code, connection_error, _ = self.ensure_connection()
        if connection_code != 0:
            logging.error(f"[!] Cannot create database because connection failed: {connection_error}")
            return -1, f"Cannot create database because connection failed: {connection_error}", None

        cursor = self.connection.cursor()
        try:
            statements = f"CREATE DATABASE IF NOT EXISTS {self.dbname}"
            logging.info(f"[*] Executing SQL statement: {statements}")
            cursor.execute(statements)
            logging.info(f"[*] Database '{self.dbname}' created successfully.")
        except Errors.Error as err:
            logging.error(f"[!] Error creating database: {err}")
            return -1, str(err), None
        finally:
            cursor.close()
        return 0, None, None

    def create_table(self, table_name:str, columns:dict) -> tuple[int, str, None]:
        """Creates a new table in the specified database.
        Args:
            table_name (str): Name of the table to be created.
            columns (dict): Dictionary of column names and their data types.
        Returns:
            tuple: (return_code, error_message, None)
                return_code (bool): True if table is created successfully, False otherwise.
                error_message (str): Error message if table creation fails, None otherwise.
                None: Always None.
        """
        connection_code, connection_error, _ = self.ensure_connection()
        if connection_code != 0:
            return -1, connection_error, None
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"USE {self.dbname}")
            columns_def = ", ".join([f"{col} {dtype}" for col, dtype in columns.items()])
            # Construct the CREATE TABLE SQL statement
            # create table if not exists to avoid errors if the table already exists
            table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_def})"
            logging.info(f"[*] Executing SQL statement: {table_sql}")
            cursor.execute(table_sql)
            logging.info(f"[*] Table '{table_name}' created successfully in database '{self.dbname}'.")
        except Errors.Error as err:
            logging.error(f"[!] Error creating table: {err}")
            return -1, str(err), None
        finally:
            cursor.close()
        return 0, None, None

    def show_table_ddl(self, table_name:str, filename:str) -> tuple[int, str, list]:
        """Retrieves the DDL (Data Definition Language) for the specified table.
        Args:
            table_name (str): Name of the table whose DDL is to be retrieved.
            filename (str): Name of the file where the DDL will be saved. optional, if not provided, DDL will not be saved to a file.
        Returns:
            tuple: (return_code, error_message, ddl)
                return_code (bool): True if DDL is retrieved successfully, False otherwise.
                error_message (str): Error message if DDL retrieval fails, None otherwise.
                ddl (list): DDL of the table if retrieval is successful, empty list otherwise.
        """
        connection_code, connection_error, _ = self.ensure_connection()
        if connection_code != 0:
            return -1, connection_error, None
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"USE {self.dbname}")
            cursor.execute(f"SHOW CREATE TABLE {table_name}")
            ddl = cursor.fetchone()
            logging.info(f"[*] DDL retrieved successfully for table '{table_name}'.")
        except Errors.Error as err:
            logging.error(f"[!] Error retrieving data: {err}")
            return -1, str(err), []
        finally:
            cursor.close()
            try:
                if filename:
                    with open(filename, "w") as f:
                        f.write(ddl[1])
            except Exception as e:
                logging.error(f"[!] Error writing DDL to file: {e}")
        return 0, None, ddl
    
    def create_workflow_table(self) -> tuple[int, str, None]:
        """Creates workflow table if it does not exits in the specified database."""
        columns = {
            "workflow_id": "INT PRIMARY KEY AUTO_INCREMENT",
            "workflow_name": "VARCHAR(255) NOT NULL UNIQUE",
            "workflow_description": "TEXT",
            "workflow_type": "VARCHAR(50) NOT NULL",
            "workflow_subtype": "VARCHAR(50)",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
            "created_by": "VARCHAR(255)",
            "updated_by": "VARCHAR(255)"
        }
        return self.create_table("workflows", columns)
    
    def show_workflow_table_ddl(self, filename:str) -> tuple[int, str, list]:
        """Retrieves the DDL (Data Definition Language) for the workflow table.
        Args:
            filename (str): Name of the file where the DDL will be saved. optional, if not provided, DDL will not be saved to a file.
        Returns:
            tuple: (return_code, error_message, ddl)
                return_code (bool): True if DDL is retrieved successfully, False otherwise.
                error_message (str): Error message if DDL retrieval fails, None otherwise.
                ddl (list): DDL of the workflow table if retrieval is successful, empty list otherwise.
        """
        return self.show_table_ddl("workflows", filename)

    def drop_workflow_table(self) -> tuple[int, str, None]:
        """Drops the workflow table from the specified database if it exists.
        Returns:
            tuple: (return_code, error_message, None)
                return_code (bool): True if table is dropped successfully, False otherwise.
                error_message (str): Error message if drop fails, None otherwise.
                None: Always None.
        """
        connection_code, connection_error, _ = self.ensure_connection()
        if connection_code != 0:
            return -1, connection_error, None
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"USE {self.dbname}")
            cursor.execute("DROP TABLE IF EXISTS workflows")
            logging.info("[*] Table 'workflows' dropped successfully.")
        except Errors.Error as err:
            logging.error(f"[!] Error dropping table: {err}")
            return -1, str(err), None
        finally:
            cursor.close()
        return 0, None, None

    def insert_into_workflow_table(self, workflow_name:str, workflow_description:str, workflow_type:str, workflow_subtype:str, created_by:str) -> tuple[int, str, None]:
        """Inserts a new workflow into the workflow table.
        Args:
            workflow_name (str): Name of the workflow to be inserted.
            workflow_description (str): Description of the workflow to be inserted.
            workflow_type (str): Type of the workflow to be inserted.
            workflow_subtype (str): Subtype of the workflow to be inserted.
            created_by (str): Name of the user who created the workflow.
        Returns:
            tuple: (return_code, error_message, None)
                return_code (bool): True if workflow is inserted successfully, False otherwise.
                error_message (str): Error message if workflow insertion fails, None otherwise.
                last_inserted_id (int): ID of the last inserted workflow if insertion is successful, None otherwise.
        """
        last_inserted_id = None
        connection_code, connection_error, _ = self.ensure_connection()
        if connection_code != 0:
            return -1, connection_error, None
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"USE {self.dbname}")
            insert_sql = f"INSERT INTO workflows (workflow_name, workflow_description, workflow_type, workflow_subtype, created_by) VALUES (%s, %s, %s, %s, %s)"
            values = (workflow_name, workflow_description, workflow_type, workflow_subtype, created_by)
            logging.info(f"[*] Executing SQL statement: {insert_sql} with values {values}")
            cursor.execute(insert_sql, values)
            # get the last inserted workflow id
            last_inserted_id = cursor.lastrowid
            self.connection.commit()
            logging.info(f"[*] Workflow '{workflow_name}' inserted successfully into table 'workflows' with ID {last_inserted_id}.")
        except Errors.Error as err:
            logging.error(f"[!] Error inserting data: {err}")
            return -1, str(err), None
        finally:
            cursor.close()
        return 0, None, last_inserted_id
    
    def update_workflow_table(self, workflow_id:int, workflow_name:str, workflow_description:str, workflow_type:str, workflow_subtype:str, updated_by:str) -> tuple[int, str, None]:
        """Updates an existing workflow in the workflow table.
        Args:
            workflow_id (int): ID of the workflow to be updated.
            workflow_name (str): New name of the workflow.
            workflow_description (str): New description of the workflow.
            workflow_type (str): New type of the workflow.
            workflow_subtype (str): New subtype of the workflow.
            updated_by (str): Name of the user who updated the workflow.
        Returns:
            tuple: (return_code, error_message, None)
                return_code (bool): True if workflow is updated successfully, False otherwise.
                error_message (str): Error message if workflow update fails, None otherwise.
                updated_workflow_id (int): ID of the updated workflow if update is successful, None otherwise.
        """        
        connection_code, connection_error, _ = self.ensure_connection()
        if connection_code != 0:
            return -1, connection_error, None
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"USE {self.dbname}")
            update_sql = f"UPDATE workflows SET workflow_name=%s, workflow_description=%s, workflow_type=%s, workflow_subtype=%s, updated_by=%s, updated_at=CURRENT_TIMESTAMP WHERE workflow_id=%s"
            values = (workflow_name, workflow_description, workflow_type, workflow_subtype, updated_by, workflow_id)
            logging.info(f"[*] Executing SQL statement: {update_sql} with values {values}")
            cursor.execute(update_sql, values)
            self.connection.commit()
            logging.info(f"[*] Workflow with ID '{workflow_id}' updated successfully in table 'workflows'.")
        except Errors.Error as err:
            logging.error(f"[!] Error updating data: {err}")
            return -1, str(err), None
        finally:
            cursor.close()
        return 0, None, workflow_id
    
    def delete_from_workflow_table(self, workflow_id:int) -> tuple[int, str, None]:
        """Deletes a workflow from the workflow table.
        Args:
            workflow_id (int): ID of the workflow to be deleted.    
        Returns:
            tuple: (return_code, error_message, None)
                return_code (bool): True if workflow is deleted successfully, False otherwise.
                error_message (str): Error message if workflow deletion fails, None otherwise.
                None: Always None.
        """        
        connection_code, connection_error, _ = self.ensure_connection()
        if connection_code != 0:
            return -1, connection_error, None
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"USE {self.dbname}")
            delete_sql = f"DELETE FROM workflows WHERE workflow_id=%s"
            values = (workflow_id,)
            logging.info(f"[*] Executing SQL statement: {delete_sql} with values {values}")
            cursor.execute(delete_sql, values)
            self.connection.commit()
            logging.info(f"[*] Workflow with ID '{workflow_id}' deleted successfully from table 'workflows'.")
        except Errors.Error as err:
            logging.error(f"[!] Error deleting data: {err}")
            return -1, str(err), None
        finally:
            cursor.close()
        return 0, None, None
    
    def select_from_workflow_table(self, workflow_id:int) -> tuple[int, str, dict]:
        """Selects a workflow from the workflow table.
        Args:
            workflow_id (int): ID of the workflow to be selected.
        Returns:
            tuple: (return_code, error_message, workflow)
                return_code (bool): True if workflow is selected successfully, False otherwise.
                error_message (str): Error message if workflow selection fails, None otherwise.
                workflow (dict): Workflow data if selection is successful, empty dict otherwise.
        """        
        connection_code, connection_error, _ = self.ensure_connection()
        if connection_code != 0:
            return -1, connection_error, {}
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(f"USE {self.dbname}")
            select_sql = f"SELECT * FROM workflows WHERE workflow_id=%s"
            values = (workflow_id,)
            logging.info(f"[*] Executing SQL statement: {select_sql} with values {values}")
            cursor.execute(select_sql, values)
            workflow = cursor.fetchone()
            if workflow:
                logging.info(f"[*] Workflow with ID '{workflow_id}' selected successfully from table 'workflows'.")
            else:
                logging.warning(f"[!] Workflow with ID '{workflow_id}' not found in table 'workflows'.")
                return -1, f"Workflow with ID '{workflow_id}' not found.", {}
        except Errors.Error as err:
            logging.error(f"[!] Error selecting data: {err}")
            return -1, str(err), {}
        finally:
            cursor.close()
        return 0, None, workflow

    def select_all_from_workflow_table(self) -> tuple[int, str, list]:
        """Selects all workflows from the workflow table.
        Returns:
            tuple: (return_code, error_message, workflows)
                return_code (bool): True if workflows are selected successfully, False otherwise.
                error_message (str): Error message if workflow selection fails, None otherwise.
                workflows (list): List of workflows if selection is successful, empty list otherwise.
        """        
        connection_code, connection_error, _ = self.ensure_connection()
        if connection_code != 0:
            return -1, connection_error, []
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(f"USE {self.dbname}")
            select_sql = f"SELECT * FROM workflows"
            logging.info(f"[*] Executing SQL statement: {select_sql}")
            cursor.execute(select_sql)
            workflows = cursor.fetchall()
            logging.info(f"[*] All workflows selected successfully from table 'workflows'.")
        except Errors.Error as err:
            logging.error(f"[!] Error selecting data: {err}")
            return -1, str(err), []
        finally:
            cursor.close()
        return 0, None, workflows

    def delete_all_from_workflow_table(self) -> tuple[int, str, None]:
        """Deletes all workflows from the workflow table.
        Returns:
            tuple: (return_code, error_message, None)
                return_code (bool): True if all workflows are deleted successfully, False otherwise.
                error_message (str): Error message if deletion fails, None otherwise.
                None: Always None.
        """
        connection_code, connection_error, _ = self.ensure_connection()
        if connection_code != 0:
            return -1, connection_error, None
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"USE {self.dbname}")
            cursor.execute("DELETE FROM workflows")
            self.connection.commit()
            logging.info("[*] All rows deleted successfully from table 'workflows'.")
        except Errors.Error as err:
            logging.error(f"[!] Error deleting data: {err}")
            return -1, str(err), None
        finally:
            cursor.close()
        return 0, None, None

    def create_role_table(self) -> tuple[int, str, None]:
        """Creates role table if it does not exits in the specified database."""
        columns = {
            "role_id": "INT PRIMARY KEY AUTO_INCREMENT",
            "workspace_id": "INT NOT NULL",
            "role_name": "VARCHAR(255) NOT NULL",
            "role_description": "TEXT",
            "role_type": "VARCHAR(50) NOT NULL",
            "role_subtype": "VARCHAR(50)",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
            "created_by": "VARCHAR(255)",
            "updated_by": "VARCHAR(255)",
                # Foreign key relationship with workflows table
            "FOREIGN KEY (workspace_id) REFERENCES workflows(workflow_id) ON UPDATE CASCADE ON DELETE CASCADE": ""
        }
        return self.create_table("roles", columns)
    
    def show_role_table_ddl(self, filename:str) -> tuple[int, str, list]:
        """Retrieves the DDL (Data Definition Language) for the role table.
        Args:
            filename (str): Name of the file where the DDL will be saved. optional, if not provided, DDL will not be saved to a file.
        Returns:
            tuple: (return_code, error_message, ddl)
                return_code (bool): True if DDL is retrieved successfully, False otherwise.
                error_message (str): Error message if DDL retrieval fails, None otherwise.
                ddl (list): DDL of the role table if retrieval is successful, empty list otherwise.
        """        
        return self.show_table_ddl("roles", filename)

    def drop_role_table(self) -> tuple[int, str, None]:
        """Drops the role table from the specified database if it exists.
        Returns:
            tuple: (return_code, error_message, None)
                return_code (bool): True if table is dropped successfully, False otherwise.
                error_message (str): Error message if drop fails, None otherwise.
                None: Always None.
        """
        connection_code, connection_error, _ = self.ensure_connection()
        if connection_code != 0:
            return -1, connection_error, None
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"USE {self.dbname}")
            cursor.execute("DROP TABLE IF EXISTS roles")
            logging.info("[*] Table 'roles' dropped successfully.")
        except Errors.Error as err:
            logging.error(f"[!] Error dropping table: {err}")
            return -1, str(err), None
        finally:
            cursor.close()
        return 0, None, None

    def insert_into_role_table(self, workspace_id:int, role_name:str, role_description:str, role_type:str, role_subtype:str, created_by:str) -> tuple[int, str, None]:
        """Inserts a new role into the role table.
        Args:
            workspace_id (int): ID of the workspace to which the role belongs.
            role_name (str): Name of the role to be inserted.
            role_description (str): Description of the role to be inserted.
            role_type (str): Type of the role to be inserted.
            role_subtype (str): Subtype of the role to be inserted.
            created_by (str): Name of the user who created the role.
        Returns:
            tuple: (return_code, error_message, None)
                return_code (bool): True if role is inserted successfully, False otherwise.
                error_message (str): Error message if role insertion fails, None otherwise.
                inserted_role_id (int): ID of the last inserted role if insertion is successful, None otherwise.
        """
        connection_code, connection_error, _ = self.ensure_connection()
        if connection_code != 0:
            return -1, connection_error, None
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"USE {self.dbname}")
            insert_sql = f"INSERT INTO roles (workspace_id, role_name, role_description, role_type, role_subtype, created_by) VALUES (%s, %s, %s, %s, %s, %s)"
            values = (workspace_id, role_name, role_description, role_type, role_subtype, created_by)
            logging.info(f"[*] Executing SQL statement: {insert_sql} with values {values}")
            cursor.execute(insert_sql, values)
            last_inserted_id = cursor.lastrowid
            self.connection.commit()
            logging.info(f"[*] Role '{role_name}' inserted successfully into table 'roles' with ID {last_inserted_id}.")
        except Errors.Error as err:
            logging.error(f"[!] Error inserting data: {err}")
            return -1, str(err), None
        finally:
            cursor.close()
        return 0, None, last_inserted_id
    
    def update_role_table(self, role_id:int, workspace_id:int, role_name:str, role_description:str, role_type:str, role_subtype:str, updated_by:str) -> tuple[int, str, None]:
        """Updates an existing role in the role table.
        Args:
            role_id (int): ID of the role to be updated.
            workspace_id (int): ID of the workspace to which the role belongs.
            role_name (str): New name of the role.
            role_description (str): New description of the role.
            role_type (str): New type of the role.
            role_subtype (str): New subtype of the role.
            updated_by (str): Name of the user who updated the role.
        Returns:
            tuple: (return_code, error_message, None)
                return_code (bool): True if role is updated successfully, False otherwise.
                error_message (str): Error message if role update fails, None otherwise.
                updated_role_id (int): ID of the updated role if update is successful, None otherwise.
        """
        connection_code, connection_error, _ = self.ensure_connection()
        if connection_code != 0:
            return -1, connection_error, None
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"USE {self.dbname}")
            update_sql = f"UPDATE roles SET workspace_id=%s, role_name=%s, role_description=%s, role_type=%s, role_subtype=%s, updated_by=%s WHERE role_id=%s"
            values = (workspace_id, role_name, role_description, role_type, role_subtype, updated_by, role_id)
            logging.info(f"[*] Executing SQL statement: {update_sql} with values {values}")
            cursor.execute(update_sql, values)
            self.connection.commit()
            logging.info(f"[*] Role '{role_name}' updated successfully in table 'roles'.")
        except Errors.Error as err:
            logging.error(f"[!] Error updating data: {err}")
            return -1, str(err), None
        finally:
            cursor.close()
        return 0, None, role_id

    def delete_from_role_table(self, role_id:int) -> tuple[int, str, None]:
        """Deletes a role from the role table.
        Args:
            role_id (int): ID of the role to be deleted.
        Returns:
            tuple: (return_code, error_message, None)
                return_code (bool): True if role is deleted successfully, False otherwise.
                error_message (str): Error message if role deletion fails, None otherwise.
                None: Always None.
        """        
        connection_code, connection_error, _ = self.ensure_connection()
        if connection_code != 0:
            return -1, connection_error, None
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"USE {self.dbname}")
            delete_sql = f"DELETE FROM roles WHERE role_id=%s"
            values = (role_id,)
            logging.info(f"[*] Executing SQL statement: {delete_sql} with values {values}")
            cursor.execute(delete_sql, values)
            self.connection.commit()
            logging.info(f"[*] Role with ID '{role_id}' deleted successfully from table 'roles'.")
        except Errors.Error as err:
            logging.error(f"[!] Error deleting data: {err}")
            return -1, str(err), None
        finally:
            cursor.close()
        return 0, None, None
    
    def select_from_role_table(self, role_id:int) -> tuple[int, str, dict]:
        """Selects a role from the role table.
        Args:
            role_id (int): ID of the role to be selected.
        Returns:
            tuple: (return_code, error_message, role_data)
                return_code (bool): True if role is selected successfully, False otherwise.
                error_message (str): Error message if role selection fails, None otherwise.
                role_data (dict): Data of the selected role if selection is successful, empty dict otherwise.
        """
        connection_code, connection_error, _ = self.ensure_connection()
        if connection_code != 0:
            return -1, connection_error, {}
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(f"USE {self.dbname}")
            select_sql = f"SELECT * FROM roles WHERE role_id=%s"
            values = (role_id,)
            logging.info(f"[*] Executing SQL statement: {select_sql} with values {values}")
            cursor.execute(select_sql, values)
            role_data = cursor.fetchone()
            if role_data:
                logging.info(f"[*] Role with ID '{role_id}' selected successfully from table 'roles'.")
            else:
                logging.warning(f"[!] Role with ID '{role_id}' not found in table 'roles'.")
                return -1, "Role not found.", {}
        except Errors.Error as err:
            logging.error(f"[!] Error selecting data: {err}")
            return -1, str(err), {}
        finally:
            cursor.close()
        return 0, None, role_data


    def select_all_from_role_table(self) -> tuple[int, str, list]:
        """Selects all roles from the role table.
        Args:
            None
        Returns:
            tuple: (return_code, error_message, roles_data)
                return_code (bool): True if roles are selected successfully, False otherwise.
                error_message (str): Error message if roles selection fails, None otherwise.
                roles_data (list): List of roles data if selection is successful, empty list otherwise.
        """
        connection_code, connection_error, _ = self.ensure_connection()
        if not connection_code:
            return -1, connection_error, []
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(f"USE {self.dbname}")
            select_sql = f"SELECT * FROM roles"
            logging.info(f"[*] Executing SQL statement: {select_sql}")
            cursor.execute(select_sql)
            roles_data = cursor.fetchall()
            if roles_data:
                logging.info(f"[*] Roles selected successfully from table 'roles'.")
            else:
                logging.warning(f"[!] No roles found in table 'roles'.")
                return -1, "No roles found.", []
        except Errors.Error as err:
            logging.error(f"[!] Error selecting data: {err}")
            return -1, str(err), []
        finally:
            cursor.close()
        return 0, None, roles_data

    def delete_all_from_role_table(self) -> tuple[int, str, None]:
        """Deletes all roles from the role table.
        Args:
            None
        Returns:
            tuple: (return_code, error_message, None)
                return_code (bool): True if all roles are deleted successfully, False otherwise.
                error_message (str): Error message if deletion fails, None otherwise.
                None: Always None.
        """
        connection_code, connection_error, _ = self.ensure_connection()
        if not connection_code:
            return -1, connection_error, None
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"USE {self.dbname}")
            cursor.execute("DELETE FROM roles")
            self.connection.commit()
            logging.info("[*] All rows deleted successfully from table 'roles'.")
        except Errors.Error as err:
            logging.error(f"[!] Error deleting data: {err}")
            return -1, str(err), None
        finally:
            cursor.close()
        return 0, None, None


    def create_guard_table(self) -> tuple[int, str, None]:
        """Creates guard table if it does not exits in the specified database.
        Args:
            None
        Returns:
            tuple: (return_code, error_message, None)
                return_code (bool): True if table is created successfully, False otherwise.
                error_message (str): Error message if creation fails, None otherwise.
                None: Always None.
        """
        columns = {
            "guard_id": "INT PRIMARY KEY AUTO_INCREMENT",
            "workspace_id": "INT NOT NULL", 
            "guard_name": "VARCHAR(255) NOT NULL",
            "guard_description": "TEXT",
            "guard_type": "VARCHAR(50) NOT NULL",
            "guard_subtype": "VARCHAR(50)",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
            "created_by": "VARCHAR(255)",
            "updated_by": "VARCHAR(255)",
                # Foreign key relationship with workflows table
            "FOREIGN KEY (workspace_id) REFERENCES workflows(workflow_id) ON UPDATE CASCADE ON DELETE CASCADE": ""
        }
        return self.create_table("guards", columns)    

    def show_guard_table_ddl(self, filename:str) -> tuple[int, str, list]:
        """Retrieves the DDL (Data Definition Language) for the guard table.
        Args:
                filename (str): Name of the file where the DDL will be saved. optional, if not provided, DDL will not be saved to a file.   Returns:
            tuple: (return_code, error_message, ddl)
                return_code (bool): True if DDL is retrieved successfully, False otherwise.
                error_message (str): Error message if DDL retrieval fails, None otherwise.
                ddl (list): DDL of the guard table if retrieval is successful, empty list otherwise.
        """        
        return self.show_table_ddl("guards", filename)

    def drop_guard_table(self) -> tuple[int, str, None]:
        """Drops the guard table from the specified database if it exists.
        Args:
            db_name (str): Name of the database where the guard table is located.
        Returns:
            tuple: (return_code, error_message, None)
                return_code (bool): True if table is dropped successfully, False otherwise.
                error_message (str): Error message if drop fails, None otherwise.
                None: Always None.
        """
        connection_code, connection_error, _ = self.ensure_connection()
        if not connection_code:
            return -1, connection_error, None
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"USE {self.dbname}")
            cursor.execute("DROP TABLE IF EXISTS guards")
            logging.info("[*] Table 'guards' dropped successfully.")
        except Errors.Error as err:
            logging.error(f"[!] Error dropping table: {err}")
            return -1, str(err), None
        finally:
            cursor.close()
        return 0, None, None


    def insert_into_guard_table(self,  workspace_id:int, guard_name:str, guard_description:str, guard_type:str, guard_subtype:str, created_by:str) -> tuple[int, str, None]:
        """Inserts a new guard into the guard table.
        Args:
            workspace_id (int): ID of the workspace to which the guard belongs.
            guard_name (str): Name of the guard to be inserted.
            guard_description (str): Description of the guard to be inserted.
            guard_type (str): Type of the guard to be inserted.
            guard_subtype (str): Subtype of the guard to be inserted.
            created_by (str): Name of the user who created the guard.
        Returns:
            tuple: (return_code, error_message, None)
                return_code (bool): True if guard is inserted successfully, False otherwise.
                error_message (str): Error message if guard insertion fails, None otherwise.
                None: Always None.
        """
        connection_code, connection_error, _ = self.ensure_connection()
        if not connection_code:
            return -1, connection_error, None
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"USE {self.dbname}")
            insert_sql = f"INSERT INTO guards (workspace_id, guard_name, guard_description, guard_type, guard_subtype, created_by) VALUES (%s, %s, %s, %s, %s, %s)"
            values = (workspace_id, guard_name, guard_description, guard_type, guard_subtype, created_by)
            logging.info(f"[*] Executing SQL statement: {insert_sql} with values {values}")
            cursor.execute(insert_sql, values)
            self.connection.commit()
            logging.info(f"[*] Guard '{guard_name}' inserted successfully into table 'guards'.")
        except Errors.Error as err:
            logging.error(f"[!] Error inserting data: {err}")
            return -1, str(err), None
        finally:
            cursor.close()
        return 0, None, None
    
    def update_guard_table(self, guard_id:int, workspace_id:int, guard_name:str, guard_description:str, guard_type:str, guard_subtype:str, updated_by:str) -> tuple[int, str, None]:
        """Updates an existing guard in the guard table.
        Args:
            guard_id (int): ID of the guard to be updated.
            workspace_id (int): ID of the workspace to which the guard belongs.
            guard_name (str): New name of the guard.
            guard_description (str): New description of the guard.
            guard_type (str): New type of the guard.
            guard_subtype (str): New subtype of the guard.
            updated_by (str): Name of the user who updated the guard.
        Returns:
            tuple: (return_code, error_message, None)
                return_code (bool): True if guard is updated successfully, False otherwise.
                error_message (str): Error message if guard update fails, None otherwise.
                None: Always None.
        """
        connection_code, connection_error, _ = self.ensure_connection()
        if not connection_code:
            return -1, connection_error, None
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"USE {self.dbname}")
            update_sql = f"UPDATE guards SET workspace_id=%s, guard_name=%s, guard_description=%s, guard_type=%s, guard_subtype=%s, updated_by=%s WHERE guard_id=%s"
            values = (workspace_id, guard_name, guard_description, guard_type, guard_subtype, updated_by, guard_id)
            logging.info(f"[*] Executing SQL statement: {update_sql} with values {values}")
            cursor.execute(update_sql, values)
            self.connection.commit()
            logging.info(f"[*] Guard '{guard_name}' updated successfully in table 'guards'.")
        except Errors.Error as err:
            logging.error(f"[!] Error updating data: {err}")
            return -1, str(err), None
        finally:
            cursor.close()
        return 0, None, None
    
    def delete_from_guard_table(self, guard_id:int) -> tuple[int, str, None]:
        """Deletes a guard from the guard table.
        Args:
            guard_id (int): ID of the guard to be deleted.
        Returns:
            tuple: (return_code, error_message, None)
                return_code (bool): True if guard is deleted successfully, False otherwise.
                error_message (str): Error message if guard deletion fails, None otherwise.
                None: Always None.
        """        
        connection_code, connection_error, _ = self.ensure_connection()
        if not connection_code:
            return -1, connection_error, None
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"USE {self.dbname}")
            delete_sql = f"DELETE FROM guards WHERE guard_id=%s"
            values = (guard_id,)
            logging.info(f"[*] Executing SQL statement: {delete_sql} with values {values}")
            cursor.execute(delete_sql, values)
            self.connection.commit()
            logging.info(f"[*] Guard with ID '{guard_id}' deleted successfully from table 'guards'.")
        except Errors.Error as err:
            logging.error(f"[!] Error deleting data: {err}")
            return -1, str(err), None
        finally:
            cursor.close()
        return 0, None, None
    
    def select_from_guard_table(self, guard_id:int) -> tuple[int, str, dict]:
        """Selects a guard from the guard table.
        Args:
            guard_id (int): ID of the guard to be selected.
        Returns:
            tuple: (return_code, error_message, guard_data)
                return_code (bool): True if guard is selected successfully, False otherwise.
                error_message (str): Error message if guard selection fails, None otherwise.
                guard_data (dict): Data of the selected guard if selection is successful, empty dict otherwise.
        """
        connection_code, connection_error, _ = self.ensure_connection()
        if not connection_code:
            return -1, connection_error, []
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(f"USE {self.dbname}")
            select_sql = f"SELECT * FROM guards WHERE guard_id=%s"
            values = (guard_id,)
            logging.info(f"[*] Executing SQL statement: {select_sql} with values {values}")
            cursor.execute(select_sql, values)
            guard_data = cursor.fetchone()
            if guard_data:
                logging.info(f"[*] Guard with ID '{guard_id}' selected successfully from table 'guards'.")
            else:
                logging.warning(f"[!] No guard found with ID '{guard_id}' in table 'guards'.")
                return -1, "No guard found.", {}
        except Errors.Error as err:
            logging.error(f"[!] Error selecting data: {err}")
            return -1, str(err), {}
        finally:
            cursor.close()
        return 0, None, guard_data


    def select_all_from_guard_table(self) -> tuple[int, str, list]:
        """Selects all guards from the guard table.
        Returns:
            tuple: (return_code, error_message, guards_data)
                return_code (bool): True if guards are selected successfully, False otherwise.
                error_message (str): Error message if guards selection fails, None otherwise.
                guards_data (list): List of guards data if selection is successful, empty list otherwise.
        """
        connection_code, connection_error, _ = self.ensure_connection()
        if not connection_code:
            return -1, connection_error, []
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(f"USE {self.dbname}")
            select_sql = f"SELECT * FROM guards"
            logging.info(f"[*] Executing SQL statement: {select_sql}")
            cursor.execute(select_sql)
            guards_data = cursor.fetchall()
            if guards_data:
                logging.info(f"[*] Guards selected successfully from table 'guards'.")
            else:
                logging.warning(f"[!] No guards found in table 'guards'.")
                return -1, "No guards found.", []
        except Errors.Error as err:
            logging.error(f"[!] Error selecting data: {err}")
            return -1, str(err), []
        finally:
            cursor.close()
        return 0, None, guards_data

    def delete_all_from_guard_table(self) -> tuple[int, str, None]:
        """Deletes all guards from the guard table.
        Returns:
            tuple: (return_code, error_message, None)
                return_code (bool): True if all guards are deleted successfully, False otherwise.
                error_message (str): Error message if deletion fails, None otherwise.
                None: Always None.
        """
        connection_code, connection_error, _ = self.ensure_connection()
        if not connection_code:
            return -1, connection_error, None
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"USE {self.dbname}")
            cursor.execute("DELETE FROM guards")
            self.connection.commit()
            logging.info("[*] All rows deleted successfully from table 'guards'.")
        except Errors.Error as err:
            logging.error(f"[!] Error deleting data: {err}")
            return -1, str(err), None
        finally:
            cursor.close()
        return 0, None, None
    
    def create_interaction_table(self) -> tuple[int, str, None]:
        """Creates interaction table if it does not exits in the specified database."""
        columns = {
            "interaction_id": "INT PRIMARY KEY AUTO_INCREMENT",
            "workflow_id": "INT NOT NULL",
            "interaction_name": "VARCHAR(255) NOT NULL",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
            "created_by": "VARCHAR(255)",
            "updated_by": "VARCHAR(255)",
                # Foreign key relationship with guards and roles tables
            "FOREIGN KEY (workflow_id) REFERENCES workflows(workflow_id) ON UPDATE CASCADE ON DELETE CASCADE": ""
        }
        return self.create_table("interaction_components", columns)

    def show_interaction_table_ddl(self, filename:str) -> tuple[int, str, list]:
        """Retrieves the DDL (Data Definition Language) for the interaction table.
        Args:
            filename (str): Name of the file where the DDL will be saved. optional, if not provided, DDL will not be saved to a file.   Returns:
            tuple: (return_code, error_message, ddl)
                return_code (bool): True if DDL is retrieved successfully, False otherwise.
                error_message (str): Error message if DDL retrieval fails, None otherwise.
                ddl (list): DDL of the interaction table if retrieval is successful, empty list otherwise.
        """        
        return self.show_table_ddl("interaction_components", filename)

    def drop_interaction_table(self) -> tuple[int, str, None]:
        """Drops the interaction_components table from the specified database if it exists.
        Returns:
            tuple: (return_code, error_message, None)
                return_code (bool): True if table is dropped successfully, False otherwise.
                error_message (str): Error message if drop fails, None otherwise.
                None: Always None.
        """
        connection_code, connection_error, _ = self.ensure_connection()
        if not connection_code:
            return -1, connection_error, None
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"USE {self.dbname}")
            cursor.execute("DROP TABLE IF EXISTS interaction_components")
            logging.info("[*] Table 'interaction_components' dropped successfully.")
        except Errors.Error as err:
            logging.error(f"[!] Error dropping table: {err}")
            return -1, str(err), None
        finally:
            cursor.close()
        return 0, None, None


    def insert_into_interaction_table(self, workflow_id:int, interaction_name:str, created_by:str) -> tuple[int, str, None]:
        """Inserts a new interaction into the interaction table.
        Args:
            workflow_id (int): ID of the workflow to which the interaction belongs.
            interaction_name (str): Name of the interaction.
            created_by (str): Name of the user who created the interaction.
        Returns:
            tuple: (return_code, error_message, inserted_interaction_id)
                return_code (bool): True if interaction is inserted successfully, False otherwise.
                error_message (str): Error message if interaction insertion fails, None otherwise.
                inserted_interaction_id (int): ID of the inserted interaction if insertion is successful, None otherwise.
        """
        connection_code, connection_error, _ = self.ensure_connection()
        if not connection_code:
            return -1, connection_error, None
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"USE {self.dbname}")
            insert_sql = "INSERT INTO interaction_components (workflow_id, interaction_name, created_by) VALUES (%s, %s, %s)"
            values = (workflow_id, interaction_name, created_by)
            logging.info(f"[*] Executing SQL statement: {insert_sql} with values {values}")
            cursor.execute(insert_sql, values)
            inserted_interaction_id = cursor.lastrowid
            self.connection.commit()
            logging.info(f"[*] Interaction '{interaction_name}' inserted successfully into table 'interaction_components' with ID {inserted_interaction_id}.")
        except Errors.Error as err:
            logging.error(f"[!] Error inserting data: {err}")
            return -1, str(err), None
        finally:
            cursor.close()
        return 0, None, inserted_interaction_id

    def update_interaction_table(self, interaction_id:int, workflow_id:int, interaction_name:str, updated_by:str) -> tuple[int, str, None]:
        """Updates an existing interaction in the interaction table.
        Args:
            interaction_id (int): ID of the interaction to be updated.
            workflow_id (int): ID of the workflow to which the interaction belongs.
            interaction_name (str): Updated name of the interaction.
            updated_by (str): Name of the user who updated the interaction.
        Returns:
            tuple: (return_code, error_message, None)
                return_code (bool): True if interaction is updated successfully, False otherwise.
                error_message (str): Error message if interaction update fails, None otherwise.
                None: Always None.
        """
        connection_code, connection_error, _ = self.ensure_connection()
        if not connection_code:
            return -1, connection_error, None
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"USE {self.dbname}")
            update_sql = "UPDATE interaction_components SET workflow_id=%s, interaction_name=%s, updated_by=%s WHERE interaction_id=%s"
            values = (workflow_id, interaction_name, updated_by, interaction_id)
            logging.info(f"[*] Executing SQL statement: {update_sql} with values {values}")
            cursor.execute(update_sql, values)
            self.connection.commit()
            logging.info(f"[*] Interaction with ID '{interaction_id}' updated successfully in table 'interaction_components'.")
        except Errors.Error as err:
            logging.error(f"[!] Error updating data: {err}")
            return -1, str(err), None
        finally:
            cursor.close()
        return 0, None, None
    
    def delete_from_interaction_table(self, interaction_id:int) -> tuple[int, str, None]:
        """Deletes an interaction from the interaction table.
        Args:
            interaction_id (int): ID of the interaction to be deleted.
        Returns:
            tuple: (return_code, error_message, None)
                return_code (bool): True if interaction is deleted successfully, False otherwise.
                error_message (str): Error message if interaction deletion fails, None otherwise.
                None: Always None.
        """        
        connection_code, connection_error, _ = self.ensure_connection()
        if not connection_code:
            return -1, connection_error, None
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"USE {self.dbname}")
            delete_sql = "DELETE FROM interaction_components WHERE interaction_id=%s"
            values = (interaction_id,)
            logging.info(f"[*] Executing SQL statement: {delete_sql} with values {values}")
            cursor.execute(delete_sql, values)
            self.connection.commit()
            logging.info(f"[*] Interaction with ID '{interaction_id}' deleted successfully from table 'interaction_components'.")
        except Errors.Error as err:
            logging.error(f"[!] Error deleting data: {err}")
            return -1, str(err), None
        finally:
            cursor.close()
        return 0, None, None
    
    def select_from_interaction_table(self, interaction_id:int) -> tuple[int, str, dict]:
        """Selects an interaction from the interaction table.
        Args:
            db_name (str): Name of the database where the interaction table is located.
            interaction_id (int): ID of the interaction to be selected.
        Returns:
            tuple: (return_code, error_message, interaction_data)
                return_code (bool): True if interaction is selected successfully, False otherwise.
                error_message (str): Error message if interaction selection fails, None otherwise.
                interaction_data (dict): Data of the selected interaction if selection is successful, empty dict otherwise.
        """
        connection_code, connection_error, _ = self.ensure_connection()
        if not connection_code:
            return -1, connection_error, []
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(f"USE {self.dbname}")
            select_sql = "SELECT * FROM interaction_components WHERE interaction_id=%s"
            values = (interaction_id,)
            logging.info(f"[*] Executing SQL statement: {select_sql} with values {values}")
            cursor.execute(select_sql, values)
            interaction_data = cursor.fetchone()
            if interaction_data:
                logging.info(f"[*] Interaction with ID '{interaction_id}' selected successfully from table 'interaction_components'.")
            else:
                logging.warning(f"[!] No interaction found with ID '{interaction_id}' in table 'interaction_components'.")
                return -1, "No interaction found.", {}
        except Errors.Error as err:
            logging.error(f"[!] Error selecting data: {err}")
            return -1, str(err), {}
        finally:
            cursor.close()
        return 0, None, interaction_data
    
    def select_all_from_interaction_table(self) -> tuple[int, str, list]:
        """Selects all interaction components from the interaction table.
        Args:
            None
        Returns:
            tuple: (return_code, error_message, interaction_components_data)
                return_code (bool): True if interaction components are selected successfully, False otherwise.
                error_message (str): Error message if interaction components selection fails, None otherwise.
                interaction_components_data (list): List of interaction components data if selection is successful, empty list otherwise.
        """

        connection_code, connection_error, _ = self.ensure_connection()
        if not connection_code:
            return -1, connection_error, []
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(f"USE {self.dbname}")
            select_sql = f"SELECT * FROM interaction_components"
            logging.info(f"[*] Executing SQL statement: {select_sql}")
            cursor.execute(select_sql)
            interaction_components_data = cursor.fetchall()
            if interaction_components_data:
                logging.info(f"[*] Interaction components selected successfully from table 'interaction_components'.")
            else:
                logging.warning(f"[!] No interaction components found in table 'interaction_components'.")
                return -1, "No interaction components found.", []
        except Errors.Error as err:
            logging.error(f"[!] Error selecting data: {err}")
            return -1, str(err), []
        finally:
            cursor.close()
        return 0, None, interaction_components_data
    
    def delete_all_from_interaction_table(self) -> tuple[int, str, None]:
        """Deletes all interaction components from the interaction table.
        Args:
            None
        Returns:
            tuple: (return_code, error_message, None)
                return_code (bool): True if interaction components are deleted successfully, False otherwise.
                error_message (str): Error message if interaction components deletion fails, None otherwise.
                None: Always None.
        """

        connection_code, connection_error, _ = self.ensure_connection()
        if not connection_code:
            return -1, connection_error, None
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"USE {self.dbname}")
            delete_sql = f"DELETE FROM interaction_components"
            logging.info(f"[*] Executing SQL statement: {delete_sql}")
            cursor.execute(delete_sql)
            self.connection.commit()
            logging.info(f"[*] All interaction components deleted successfully from table 'interaction_components'.")
        except Errors.Error as err:
            logging.error(f"[!] Error deleting data: {err}")
            return -1, str(err), None
        finally:
            cursor.close()
        return 0, None, None
   
    def create_interaction_component_table(self) -> tuple[int, str, None]:
        """Creates interaction component table if it does not exits in the specified database.
        Args:
            db_name (str): Name of the database where the interaction component table will be created."""
        columns = {
            "interaction_component_id": "INT PRIMARY KEY AUTO_INCREMENT",
            "workflow_id": "INT NOT NULL",
            "interaction_component_name": "VARCHAR(255) NOT NULL",
            "interaction_component_description": "TEXT",
            "interaction_component_type": "VARCHAR(50) NOT NULL",
            "interaction_component_subtype": "VARCHAR(50)",
            "interaction_id": "INT NOT NULL",
            "guard_id": "INT",
            "role_id": "INT",
            "direction": "VARCHAR(10) NOT NULL",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
            "created_by": "VARCHAR(255)",
            "updated_by": "VARCHAR(255)",
            # Foreign key relationship with interactions, guards, and roles tables
            "FOREIGN KEY (workflow_id) REFERENCES workflows(workflow_id) ON UPDATE CASCADE ON DELETE CASCADE": "",
            "FOREIGN KEY (interaction_id) REFERENCES interaction_components(interaction_id) ON UPDATE CASCADE ON DELETE CASCADE": "",
            "FOREIGN KEY (guard_id) REFERENCES guards(guard_id) ON UPDATE CASCADE ON DELETE SET NULL": "",
            "FOREIGN KEY (role_id) REFERENCES roles(role_id) ON UPDATE CASCADE ON   DELETE SET NULL": ""

        }
        return self.create_table("interaction_component", columns)

    def show_interaction_component_table_ddl(self, filename:str) -> tuple[int, str, list]:
        """Retrieves the DDL (Data Definition Language) for the interaction component table.
        Args:
            filename (str): Name of the file where the DDL will be saved. optional, if not provided, DDL will not be saved to a file.   Returns:
            tuple: (return_code, error_message, ddl)
                return_code (bool): True if DDL is retrieved successfully, False otherwise.
                error_message (str): Error message if DDL retrieval fails, None otherwise.
                ddl (list): DDL of the interaction component table if retrieval is successful, empty list otherwise.
        """        
        return self.show_table_ddl("interaction_component", filename)

    def drop_interaction_component_table(self) -> tuple[int, str, None]:
        """Drops the interaction_component table from the specified database if it exists.
        Args:
            None
        Returns:
            tuple: (return_code, error_message, None)
                return_code (bool): True if table is dropped successfully, False otherwise.
                error_message (str): Error message if drop fails, None otherwise.
                None: Always None.
        """
        connection_code, connection_error, _ = self.ensure_connection()
        if not connection_code:
            return -1, connection_error, None
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"USE {self.dbname}")
            cursor.execute("DROP TABLE IF EXISTS interaction_component")
            logging.info("[*] Table 'interaction_component' dropped successfully.")
        except Errors.Error as err:
            logging.error(f"[!] Error dropping table: {err}")
            return -1, str(err), None
        finally:
            cursor.close()
        return 0, None, None

    def insert_into_interaction_component_table(self, interaction_component_name:str, interaction_component_description:str, interaction_component_type:str, interaction_component_subtype:str, interaction_id:int, guard_id:int, role_id:int, direction:str, created_by:str) -> tuple[int, str, None]:
        """Inserts a new interaction component into the interaction component table.
        Args:
            None
            interaction_component_name (str): Name of the interaction component to be inserted.
            interaction_component_description (str): Description of the interaction component to be inserted.
            interaction_component_type (str): Type of the interaction component to be inserted.
            interaction_component_subtype (str): Subtype of the interaction component to be inserted.
            interaction_id (int): ID of the interaction to which the component belongs.
            guard_id (int): ID of the guard associated with the interaction component.
            role_id (int): ID of the role associated with the interaction component.
            direction (str): Direction of the interaction component (e.g., "inbound", "outbound").
            created_by (str): Name of the user who created the interaction component.
        Returns:
            tuple: (return_code, error_message, None)
                return_code (bool): True if interaction component is inserted successfully, False otherwise.
                error_message (str): Error message if interaction component insertion fails, None otherwise.
                None: Always None.
        """
        last_inserted_id = None
        connection_code, connection_error, _ = self.ensure_connection()
        if not connection_code:
            return -1, connection_error, None
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"USE {self.dbname}")
            insert_sql = f"INSERT INTO interaction_component (interaction_component_name, interaction_component_description, interaction_component_type, interaction_component_subtype, interaction_id, guard_id, role_id, direction, created_by) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            values = (interaction_component_name, interaction_component_description, interaction_component_type, interaction_component_subtype, interaction_id, guard_id, role_id, direction, created_by)
            logging.info(f"[*] Executing SQL statement: {insert_sql} with values {values}")
            cursor.execute(insert_sql, values)
            last_inserted_id = cursor.lastrowid
            self.connection.commit()
            logging.info(f"[*] Interaction component '{interaction_component_name}' inserted successfully into table 'interaction_component'.")
            return 0, None, last_inserted_id
        except Errors.Error as err:
            logging.error(f"[!] Error inserting interaction component '{interaction_component_name}': {err}")
            return -1, str(err), None
        finally:
            cursor.close()

    def update_interaction_component_table(self, interaction_component_id:int, interaction_component_name:str, interaction_component_description:str, interaction_component_type:str, interaction_component_subtype:str, interaction_id:int, guard_id:int, role_id:int, direction:str, updated_by:str) -> tuple[int, str, None]:
        """Updates an existing interaction component in the interaction component table.
        Args:
            interaction_component_id (int): ID of the interaction component to be updated.
            interaction_component_name (str): New name of the interaction component.
            interaction_component_description (str): New description of the interaction component.
            interaction_component_type (str): New type of the interaction component.
            interaction_component_subtype (str): New subtype of the interaction component.
            interaction_id (int): ID of the interaction to which the component belongs.
            guard_id (int): ID of the guard associated with the interaction component.
            role_id (int): ID of the role associated with the interaction component.
            direction (str): Direction of the interaction component (e.g., "inbound", "outbound").
            updated_by (str): Name of the user who updated the interaction component.
        Returns:
            tuple: (return_code, error_message, None)
                return_code (bool): True if interaction component is updated successfully, False otherwise.
                error_message (str): Error message if interaction component update fails, None otherwise.
                None: Always None.
        """
        connection_code, connection_error, _ = self.ensure_connection()
        if not connection_code:
            return -1, connection_error, None
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"USE {self.dbname}")
            update_sql = f"UPDATE interaction_component SET interaction_component_name=%s, interaction_component_description=%s, interaction_component_type=%s, interaction_component_subtype=%s, interaction_id=%s, guard_id=%s, role_id=%s, direction=%s, updated_by=%s WHERE interaction_component_id=%s"
            values = (interaction_component_name, interaction_component_description, interaction_component_type, interaction_component_subtype, interaction_id, guard_id, role_id, direction, updated_by, interaction_component_id)
            logging.info(f"[*] Executing SQL statement: {update_sql} with values {values}")
            cursor.execute(update_sql, values)
            self.connection.commit()
            logging.info(f"[*] Interaction component with ID '{interaction_component_id}' updated successfully in table 'interaction_component'.")
            return 0, None, interaction_component_id
        except Errors.Error as err:
            logging.error(f"[!] Error updating interaction component with ID '{interaction_component_id}': {err}")
            return -1, str(err), None
        finally:
            cursor.close()

    def delete_from_interaction_component_table(self, interaction_component_id:int) -> tuple[int, str, None]:
        """Deletes an interaction component from the interaction component table.
        Args:
            interaction_component_id (int): ID of the interaction component to be deleted.
        Returns:
            tuple: (return_code, error_message, None)
                return_code (bool): True if interaction component is deleted successfully, False otherwise.
                error_message (str): Error message if interaction component deletion fails, None otherwise.
                None: Always None.
        """
        connection_code, connection_error, _ = self.ensure_connection()
        if not connection_code:
            return -1, connection_error, None
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"USE {self.dbname}")
            delete_sql = f"DELETE FROM interaction_component WHERE interaction_component_id=%s"
            values = (interaction_component_id,)
            logging.info(f"[*] Executing SQL statement: {delete_sql} with values {values}")
            cursor.execute(delete_sql, values)
            self.connection.commit()
            logging.info(f"[*] Interaction component with ID '{interaction_component_id}' deleted successfully from table 'interaction_component'.")
            return 0, None, None
        except Errors.Error as err:
            logging.error(f"[!] Error deleting interaction component with ID '{interaction_component_id}': {err}")
            return -1, str(err), None
        finally:
            cursor.close()

    def select_from_interaction_component_table(self, interaction_component_id:int) -> tuple[int, str, dict]:
        """Selects an interaction component from the interaction component table.
        Args:
            db_name (str): Name of the database where the interaction component table is located.
            interaction_component_id (int): ID of the interaction component to be selected.
        Returns:
            tuple: (return_code, error_message, interaction_component)
                return_code (bool): True if interaction component is selected successfully, False otherwise.
                error_message (str): Error message if interaction component selection fails, None otherwise.
                interaction_component (dict): Selected interaction component data if successful, None otherwise.
        """
        connection_code, connection_error, _ = self.ensure_connection()
        if not connection_code:
            return -1, connection_error, []
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(f"USE {self.dbname}")
            select_sql = f"SELECT * FROM interaction_component WHERE interaction_component_id=%s"
            values = (interaction_component_id,)
            logging.info(f"[*] Executing SQL statement: {select_sql} with values {values}")
            cursor.execute(select_sql, values)
            interaction_component = cursor.fetchone()
            if interaction_component:
                logging.info(f"[*] Interaction component with ID '{interaction_component_id}' selected successfully from table 'interaction_component'.")
                return 0, None, interaction_component
            else:
                logging.warning(f"[!] No interaction component found with ID '{interaction_component_id}' in table 'interaction_component'.")
                return -1, "No interaction component found.", None
        except Errors.Error as err:
            logging.error(f"[!] Error selecting interaction component with ID '{interaction_component_id}': {err}")
            return -1, str(err), None
        finally:
            cursor.close()


    def select_all_from_interaction_component_table(self) -> tuple[int, str, list]:
        """Selects all interaction components from the interaction component table.
        Args:
            None
        Returns:
            tuple: (return_code, error_message, interaction_components)
                return_code (bool): True if interaction components are selected successfully, False otherwise.
                error_message (str): Error message if interaction component selection fails, None otherwise.
                interaction_components (list): List of selected interaction components if successful, None otherwise.
        """
        connection_code, connection_error, _ = self.ensure_connection()
        if not connection_code:
            return -1, connection_error, []
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(f"USE {self.dbname}")
            select_sql = f"SELECT * FROM interaction_component"
            logging.info(f"[*] Executing SQL statement: {select_sql}")
            cursor.execute(select_sql)
            interaction_components = cursor.fetchall()
            if interaction_components:
                logging.info(f"[*] Interaction components selected successfully from table 'interaction_component'.")
                return 0, None, interaction_components
            else:
                logging.warning(f"[!] No interaction components found in table 'interaction_component'.")
                return -1, "No interaction components found.", None
        except Errors.Error as err:
            logging.error(f"[!] Error selecting interaction components: {err}")
            return -1, str(err), None
        finally:
            cursor.close()

    def delete_all_from_interaction_component_table(self) -> tuple[int, str, None]:
        """Deletes all interaction components from the interaction component table.
        Args:
            None
        Returns:
            tuple: (return_code, error_message, None)
                return_code (bool): True if all interaction components are deleted successfully, False otherwise.
                error_message (str): Error message if deletion fails, None otherwise.
                None: Always None.
        """
        connection_code, connection_error, _ = self.ensure_connection()
        if not connection_code:
            return -1, connection_error, None
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"USE {self.dbname}")
            cursor.execute("DELETE FROM interaction_component")
            self.connection.commit()
            logging.info("[*] All rows deleted successfully from table 'interaction_component'.")
        except Errors.Error as err:
            logging.error(f"[!] Error deleting data: {err}")
            return -1, str(err), None
        finally:
            cursor.close()
        return 0, None, None

    def close(self):
        """Close the active database connection if one is open."""
        if self.connection:
            self.connection.close()
            logging.info("[*] MySQL connection closed.")    


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("[*] Starting MySQL database operations...")
    db = MySQLDatabase(host="localhost", user="root", password="root")
    logging.info("[*] Testing MySQL database connection and operations...")
    db.connect()
    logging.info("[*] Creating database and table...")
    return_code, return_msg, _ = db.create_database()
    logging.info("[*] Creating table 'users' in database 'test_db'...")
    if return_code == 0:
        logging.info("[*] Table 'users' created successfully.")
    else:
        logging.error(f"[!] Error creating table 'users': {return_msg}")

    create_table_code, create_table_msg, _ =db.create_workflow_table()
    if create_table_code == 0:
        logging.info("[*] Workflow table created successfully.")
    else:        
        logging.error(f"[!] Error creating workflow table: {create_table_msg}")
    
    create_table_code, create_table_msg, _ =db.create_role_table()
    if create_table_code == 0:
        logging.info("[*] Role table created successfully.")
    else:
        logging.error(f"[!] Error creating role table: {create_table_msg}")

    create_table_code, create_table_msg, _ =db.create_guard_table()
    if create_table_code == 0:
        logging.info("[*] Guard table created successfully.")
    else:
        logging.error(f"[!] Error creating guard table: {create_table_msg}")

    create_table_code, create_table_msg, _ =db.create_interaction_table()
    if create_table_code == 0:
        logging.info("[*] Interaction table created successfully.")
    else:
        logging.error(f"[!] Error creating interaction table: {create_table_msg}")

    create_table_code, create_table_msg, _ =db.create_interaction_component_table()
    if create_table_code == 0:
        logging.info("[*] Interaction component table created successfully.")
    else:
        logging.error(f"[!] Error creating interaction component table: {create_table_msg}")


    logging.info("[*] Inserting data into table 'users'...")



