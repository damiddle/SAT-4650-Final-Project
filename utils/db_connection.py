"""
Module for database connection and operations.

Provides functions to create a connection pool, get individual connections,
execute SQL queries, and initialize the database (including table creation).
"""

import mysql.connector
import os
import ast
import logging
import utils.encryption as encryption
from dotenv import load_dotenv
from mysql.connector import pooling, Error

logger = logging.getLogger(__name__)

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

        return pool
    except Error as err:
        if "Unknown database" in str(err):
            logger.error("Database not found. Initializing database...")
            initialize_database()
            pool = pooling.MySQLConnectionPool(
                pool_name="db_pool",
                pool_size=int(CONNECTION_POOL_SIZE),
                pool_reset_session=True,
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
            )
            return pool
        else:
            logger.error(f"Error creating connection pool: {err}")
            raise


def initialize_database():
    """Initializes the database and creates necessary tables if they do not exist.

    Creates the 'users', 'inventory', and 'audit_log' tables using SQL commands.
    Loads initial user 'admin' with password 'pass' into the program.
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
        cursor.execute("CREATE DATABASE IF NOT EXISTS " + DB_NAME)
        cursor.execute("USE " + DB_NAME)
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
        logger.info("Table 'users' created or already initialized")

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
        logger.info("Table 'inventory' created or already initialized")

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
        logger.info("Table 'audit_log' created or already initialized")

        cursor.execute("""CREATE PROCEDURE IF NOT EXISTS GetLastAuditEntries(IN num_entries INT)
            BEGIN
                SELECT 
                    log_id,
                    username,
                    updated_object,
                    action_type,
                    action_timestamp,
                    details
                FROM audit_log
                ORDER BY action_timestamp DESC
                LIMIT num_entries;
            END;
            """)
        logger.info("Procedure 'GetLastAuditEntries' created or already initialized")

        cursor.execute(
            "INSERT IGNORE INTO users(username, password_encrypted, role, email) VALUES(%s, %s, %s, %s)",
            ["admin", encryption.encrypt_data("pass"), "Admin", "initialized@mtu.edu"],
        )
        logger.info("Test user 'admin' with password 'pass' created")
        connection.commit()
    except Error as err:
        logger.error("Error initializing database: %s", err)
    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


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
        logger.error(f"Error getting connection from pool: {e}")
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
        logger.error(f"Database error during query execution: {err}")

        return None
