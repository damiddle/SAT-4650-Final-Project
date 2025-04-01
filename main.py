import db_connection
import encryption
import inventory
import users
import audit_log


class CurrentUser:

    def __init__(self, username, role, email):
        self.username = username
        self.role = role
        self.email = email


# Log in sequence, creates current user class
valid_login = Fals

while not valid_login:
    username = input("Username: ")
    password = input("Password: ")

    connection = db_connection.connect_to_database()
    cursor = connection.cursor()

    query = "SELECT password_encrypted FROM users WHERE username = %s"
    query_list = [username]
    cursor.execute(query, query_list)

    ref_pass = cursor.fetchone()

    # Protects against user not exist
    if not ref_pass == None:
        if encryption.decrypt_password(ref_pass[0]) == password:
            print("Successfully logged in!")

            current_user = users.get_user(username)[0]
            print(current_user)
            current_user = CurrentUser(
                current_user[1], current_user[3], current_user[4]
            )

            print("Welcome " + current_user.username)
            print("Permission level: " + current_user.role)

            audit_log.update_audit_log(
                current_user, current_user.username, "LOGIN", "Logged in"
            )

            valid_login = True

        else:
            print("Login not valid, try again")
    else:
        print("Login not valid, try again")

# Main use sequence
menu_context = "main"

while not menu_context == "exit":
    if menu_context == "main":

        # Admin access
        if current_user.role == "Admin":
            requested_menu_action = input(
                "Action:\n[1] View inventory/use actions \n[2] View users/use actions \n[3] View audit log\n[4] View alerts\n[5] Manage account \n[6] Log out\n"
            )

            if requested_menu_action == "1":
                menu_context = "inventory"

            elif requested_menu_action == "2":
                menu_context = "users"

            elif requested_menu_action == "3":
                menu_context = "audit"

            elif requested_menu_action == "4":
                menu_context = "alerts"

            elif requested_menu_action == "5":
                menu_context = "account"

            elif requested_menu_action == "6":
                menu_context = "exit"

            else:
                print("Action not valid")

        # User access
        elif current_user.role == "User":
            requested_menu_action = input(
                "Action:\n[1] View inventory/use actions \n[2] View alerts\n[3] Manage account\n[4] Exit"
            )

            if requested_menu_action == "1":
                menu_context = "inventory"

            elif requested_menu_action == "2":
                menu_context = "alerts"

            elif requested_menu_action == "3":
                menu_context = "account"

            elif requested_menu_action == "4":
                menu_context = "exit"

            else:
                print("Action not valid")

        # Viewer access
        elif current_user.role == "Viewer":
            requested_menu_action = input(
                "Action:\n[1] View inventory \n[2] View alerts\n[3] Manage account\n[4] Exit"
            )

            if requested_menu_action == "1":
                menu_context = "inventory"

            elif requested_menu_action == "2":
                menu_context = "alerts"

            elif requested_menu_action == "3":
                menu_context = "account"

            elif requested_menu_action == "4":
                menu_context = "exit"

            else:
                print("Action not valid")

        else:
            print("Something went wrong, permission level not valid")
            print("User permissions: " + current_user.role)

    # Inventory functions
    elif menu_context == "inventory":

        # Admin access functions
        if current_user.role == "Admin":
            requested_menu_action = input(
                "Action:\n[1] Show all inventory\n[2] Show item\n[3] Update item\n[4] Add new item\n[5] Delete item\n[6] Exit to main menu\n"
            )

            # Show all inventory
            if requested_menu_action == "1":
                db_connection.show_table("inventory")

            # Show item
            elif requested_menu_action == "2":
                item_name = input("Enter item name to view: ")

                inventory.show_item(current_user, item_name)

            # Update item
            elif requested_menu_action == "3":
                item_name = input("Enter item name: ")
                action = input(
                    "increase, decrease, update quantity, update expiration, update description, or update minimum threshold\n"
                )

                inventory.update_inventory_item(current_user, item_name, action)

            # Add new item
            elif requested_menu_action == "4":
                item_name = input("Enter item to add: ")
                item_category = input("Enter item category: ")
                item_description = input("Enter item description: ")
                initial_quantity = input("Enter the initial quantity: ")
                expiration_date = input(
                    "Enter the expiration date (in YYYY-MM-DD format): "
                )
                minimum_threshold = input("Enter the minimum threshold: ")

                inventory.add_inventory_item(
                    current_user,
                    item_name,
                    item_category,
                    item_description,
                    initial_quantity,
                    expiration_date,
                    minimum_threshold,
                )

            # Delete item
            elif requested_menu_action == "5":
                item_name = input("Enter item to delete: ")

                inventory.delete_item(current_user, item_name)

            # Exit to main menu
            elif requested_menu_action == "6":
                menu_context = "main"

            else:
                print("Action not valid")

        # User access functions
        elif current_user.role == "User":
            requested_menu_action = input(
                "Action:\n[1] Show all inventory\n[2] Show item\n[3] Update item\n[4] Exit to main menu\n"
            )

            # Shows all inventory
            if requested_menu_action == "1":
                db_connection.show_table("inventory")

            # Show item
            elif requested_menu_action == "2":
                item_name = input("Enter item name to view: ")

                inventory.show_item(current_user, item_name)

            # Update item
            elif requested_menu_action == "3":
                item_name = input("Enter item name: ")
                action = input(
                    "increase, decrease, update quantity, update expiration, update description, or update minimum threshold\n"
                )

                inventory.update_inventory_item(current_user, item_name, action)

            # Exit to main menu
            elif requested_menu_action == "4":
                menu_context = "main"

            else:
                print("Action not valid")

        # Viewer access functions
        elif current_user.role == "Viewer":
            requested_menu_action = input(
                "Action:\n[1] Show all inventory\n[2] Show item\n[3] Exit to main menu\n"
            )

            # Show all inventory
            if requested_menu_action == "1":
                db_connection.show_table("inventory")

            # Show item
            elif requested_menu_action == "2":
                item_name = input("Enter item name to view: ")

                inventory.show_item(current_user, item_name)

            # Exit to main menu
            elif requested_menu_action == "3":
                menu_context = "main"

            else:
                print("Action not valid")

        else:
            print("Something went wrong, permission level not valid")
            print("User permissions: " + current_user.role)

    # User management functions, admin only
    elif menu_context == "users":
        if current_user.role == "Admin":
            requested_menu_action = input(
                "Action:\n[1] View user\n[2] Change user role\n[3] Add user\n[4] Delete user\n[5] Exit to main menu\n"
            )

            # View user
            if requested_menu_action == "1":
                user = input("Enter user to view: ")

                print(users.view_user(current_user, user))

            # Change user role
            elif requested_menu_action == "2":
                user = input("Enter user: ")
                new_role = input("Enter new role: ")

                users.change_user_role(current_user, user, new_role)

            # Add user
            elif requested_menu_action == "3":
                user = input("Username: ")
                password = input("Password: ")
                role = input("User role: ")
                email = input("User email: ")

                users.add_user(current_user, user, password, role, email)

            # Delete user
            elif requested_menu_action == "4":
                user = input("User to delete: ")

                users.delete_user(current_user, user)

            # Exit to main menu
            elif requested_menu_action == "5":
                menu_context = "main"

            else:
                print("Action not valid")

        else:
            print("You do not have permission for these functions")
            print("User permissions: " + current_user.role)

    # Audit functions, admin only
    elif menu_context == "audit":
        if current_user.role == "Admin":
            requested_menu_action = input(
                "[1] View recent logs\n[2] Export audit log to .txt\n[3] Exit to main menu\n"
            )

            # View recent logs
            if requested_menu_action == "1":
                number_of_entries = input("Pull last ___ logs: ")

                audit_log.pull_audit_log(current_user, number_of_entries)

            # Exports audit log to .txt
            elif requested_menu_action == "2":
                audit_log.export_to_txt(current_user)

            # Exit to main menu
            elif requested_menu_action == "3":
                menu_context = "main"

            else:
                print("Action not valid")

        else:
            print("You do not have permission for these functions")
            print("User permissions: " + current_user.role)

    # Alert functions
    elif menu_context == "alerts":
        pass

    else:
        print("Something went wrong")
        menu_context = "main"


print("Logging out")
audit_log.update_audit_log(current_user, current_user.username, "LOGOUT", "Logged out")
