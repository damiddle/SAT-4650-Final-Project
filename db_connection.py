import mysql.connector
import os
from dotenv import load_dotenv

ENV_FILE_PATH = ".env"
load_dotenv(ENV_FILE_PATH)

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

VALID_USER_ROLES = os.getenv("VALID_USER_ROLES")


def connect_to_database():
    """Connects to ems_inventory database

    Returns:
        Connection: Connection object to MySQL database
    """

    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database="ems_inventory",
        )

        if connection.is_connected():
            # print("Successfully connected to EMS database")

            return connection

    except mysql.connector.Error as e:
        print(f"Database error: {e}")

        try:
            # Create database if not exist
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="mysqlpass",
            )

            print("Creating database")
            cursor = connection.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS ems_inventory")
            cursor.execute("USE ems_inventory")

            print("Creating tables")
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS users (
                    user_id INT PRIMARY KEY AUTO_INCREMENT, 
                    username VARCHAR(50) UNIQUE NOT NULL, 
                    password_encrypted VARCHAR(255) NOT NULL, 
                    role ENUM('Admin', 'User', 'Viewer') DEFAULT 'Viewer', 
                    email VARCHAR(100) UNIQUE NOT NULL, 
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP);"""
            )
            print("Users created")

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
                    UNIQUE(item_name, category));"""
            )
            print("Inventory created")

            cursor.execute(
                """CREATE TABLE audit_log (
                    log_id INT PRIMARY KEY AUTO_INCREMENT,
                    username VARCHAR(50),
                    updated_object VARCHAR(100),
                    action_type ENUM('ADD', 'UPDATE', 'DELETE', 'LOGIN', 'LOGOUT') NOT NULL,
                    action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    details TEXT);"""
            )
            print("Audit log created")

            print("All tables created")

            connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database="ems_inventory",
            )

            if connection.is_connected():
                print("Successfully connected to EMS database")

                return connection

        except mysql.connector.Error as e:
            print(f"Database error: {e}")


def show_table(table):
    """Prints MySQL table to console

    Args:
        table (String): Name of the table in ems_inventory to print
    """

    with connect_to_database() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM " + table)
            contents = cursor.fetchall()

            for row in contents:
                print(row)


def execute_query(query, params=None, commit=True):
    try:
        with connect_to_database() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)

                if commit:
                    connection.commit()

                result = cursor.fetchall()

        return result

    except Exception as e:
        print(f"Database error: {e}")

        return
