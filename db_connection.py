import mysql.connector


def connect_to_database():
    """Connects to ems_inventory database

    Returns:
        Connection: Connection object to MySQL database
    """

    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="mysqlpass",
            database="ems_inventory",
        )

        if connection.is_connected():
            # print("Successfully connected to EMS database")

            return connection

    except mysql.connector.Error as e:
        print("Error connecting to EMS database")

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
            host="localhost",
            user="root",
            password="mysqlpass",
            database="ems_inventory",
        )

        if connection.is_connected():
            print("Successfully connected to EMS database")

            return connection


def show_table(table):
    """Prints MySQL table to console

    Args:
        table (String): Name of the table in ems_inventory to print
    """

    connection = connect_to_database()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM " + table)
    contents = cursor.fetchall()

    for row in contents:
        print(row)

    cursor.close()
