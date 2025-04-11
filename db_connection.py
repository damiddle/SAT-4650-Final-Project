"""
Module for database connection and operations.

Provides functions to create a connection pool, get individual connections,
execute SQL queries, and initialize the database (including table creation).
"""

import mysql.connector
import os
import ast
from dotenv import load_dotenv
from mysql.connector import pooling, Error

ENV_FILE_PATH = ".env"
load_dotenv(ENV_FILE_PATH)

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
CONNECTION_POOL_SIZE = os.getenv("CONNECTION_POOL_SIZE")
VALID_USER_ROLES = ast.literal_eval(os.getenv("VALID_USER_ROLES"))


def create_connection_pool():
    """Creates a MySQL connection pool for database operations.

    Returns:
        MySQLConnectionPool: An instance of the created connection pool.

    Raises:
        Error: If there is an issue creating the connection pool.
    """

    try:
        pool = pooling.MySQLConnectionPool(
            pool_name="db_pool",
            pool_size=int(CONNECTION_POOL_SIZE),
            pool_reset_session=True,
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
        )
        print("Connection pool created successfully.")

        return pool
    except Error as err:
        print(f"Error creating connection pool: {err}")
        raise


connection_pool = create_connection_pool()


def get_connection():
    """Retrieves a connection from the connection pool.

    Returns:
        MySQLConnection: A valid connection object.

    Raises:
        Error: If a valid connection cannot be retrieved.
    """

    try:
        connection = connection_pool.get_connection()
        if connection.is_connected():
            return connection
        else:
            raise Error("Failed to retrieve a valid connection from the pool.")
    except Error as e:
        print(f"Error getting connection from pool: {e}")
        raise


def execute_query(query, params=None, commit=True):
    """Executes a SQL query on the database.

    For SELECT queries, the function returns fetched results; for other queries,
    it commits the changes and returns the number of affected rows.

    Args:
        query (str): The SQL query to execute.
        params (list, optional): List of parameters for the query. Defaults to None.
        commit (bool, optional): Whether to commit the transaction. Defaults to True.

    Returns:
        object: The result of the query (fetched data or row count), or None if an error occurs.
    """

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)

                if query.strip().upper().startswith("SELECT"):
                    result = cursor.fetchall()
                else:
                    connection.commit()
                    result = cursor.rowcount

                return result
    except Error as err:
        print(f"Database error during query execution: {err}")

        return None


def initialize_database():
    """Initializes the database and creates necessary tables if they do not exist.

    Creates the 'users', 'inventory', and 'audit_log' tables using SQL commands.
    """

    connection = None
    cursor = None

    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
        )
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS %s", [DB_NAME])
        cursor.execute("USE %s", [DB_NAME])
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS users (
                    user_id INT PRIMARY KEY AUTO_INCREMENT, 
                    username VARCHAR(50) UNIQUE NOT NULL, 
                    password_encrypted VARCHAR(255) NOT NULL, 
                    role ENUM('Admin', 'Leadership', 'General Responder', 'Community Member') DEFAULT 'General Responder', 
                    email VARCHAR(100) UNIQUE NOT NULL, 
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                );"""
        )

        print("Table 'users' created")
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS inventory (
                    item_id INT PRIMARY KEY AUTO_INCREMENT,
                    item_name VARCHAR(100) NOT NULL,
                    category VARCHAR(50) NOT NULL,
                    description TEXT,
                    quantity INT NOT NULL CHECK (quantity >= 0),
                    expiration_date DATE,
                    min_threshold INT DEFAULT 1,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    UNIQUE(item_name, category)
                );"""
        )

        print("Table 'inventory' created")
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS audit_log (
                    log_id INT PRIMARY KEY AUTO_INCREMENT,
                    username VARCHAR(50),
                    updated_object VARCHAR(100),
                    action_type ENUM('ADD', 'UPDATE', 'DELETE', 'LOGIN', 'LOGOUT', 'ACCESS') NOT NULL,
                    action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    details TEXT
                );"""
        )

        print("Table 'audit_log' created")
    except Error as err:
        print("Error initializing database: %s", err)
    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
