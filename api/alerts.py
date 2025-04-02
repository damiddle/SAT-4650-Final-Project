import db_connection


def search_for_expiration(user):
    connection = db_connection.connect_to_database()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM inventory WHERE expiration_date IS NOT NULL AND expiration_date < CURDATE() ORDER BY expiration_date ASC"
    )

    expired_inventory = cursor.fetchall()
    print(expired_inventory)
    cursor.close()


def search_for_low_quantity(user):
    connection = db_connection.connect_to_database()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM inventory WHERE min_threshold IS NOT NULL AND quantity < min_threshold ORDER BY quantity ASC"
    )

    low_inventory = cursor.fetchall()
    print(low_inventory)
    cursor.close()
