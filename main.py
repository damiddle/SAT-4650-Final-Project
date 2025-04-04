import api.inventory as inventory
import api.users as users
import api.audit_log as audit_log
import api.alerts as alerts
import utils.validators as validators


class CurrentUser:
    def __init__(self, username, role, email):
        self.username = username
        self.role = role
        self.email = email


valid_login = False
while not valid_login:
    try:
        username = input("Username: ")
        if not validators.is_non_empty_string(username):
            raise TypeError("Username must be a non-empty string")
        password = input("Password: ")
        if not validators.is_non_empty_string(password):
            raise TypeError("Password must be a non-empty string")
        current_user = users.login(username, password)
        if (current_user is not False) and (current_user is not None):
            valid_login = True
    except Exception as e:
        print(f"Error occurred during login: {e}")
menu_context = "main"
while not menu_context == "exit":
    if menu_context == "main":
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
                print("Action " + requested_menu_action + " is not valid")
        elif current_user.role == "User":
            requested_menu_action = input(
                "Action:\n[1] View inventory/use actions \n[2] View alerts\n[3] Manage account\n[4] Exit\n"
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
                print("Action " + requested_menu_action + " is not valid")
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
                print("Action " + requested_menu_action + " is not valid")
        else:
            print("You do not have permission for these functions")
            print("User permissions: " + current_user.role)
    elif menu_context == "inventory":
        if current_user.role == "Admin":
            requested_menu_action = input(
                "Action:\n[1] Show all inventory\n[2] Show item\n[3] Update item\n[4] Add new item\n[5] Delete item\n[6] Exit to main menu\n"
            )
            if requested_menu_action == "1":
                table_contents = inventory.show_all_inventory(current_user)
                for row in table_contents:
                    print(
                        f"Item name: {row[0]} | Category: {row[1]} | Description: {row[2]} | Quantity: {row[3]} | Expiration date: {row[4]} | Minimum threshold: {row[5]} | Last updated: {row[6]}"
                    )
            elif requested_menu_action == "2":
                try:
                    item_name = input("Enter item name to view: ")
                    if not validators.is_non_empty_string(item_name):
                        raise TypeError("Item name must be non-empty string")
                    item_contents = inventory.show_item(current_user, item_name)
                    print(
                        f"Item name: {item_contents[0][0]} | Category: {item_contents[0][1]} | Description: {item_contents[0][2]} | Quantity: {item_contents[0][3]} | Expiration date: {item_contents[0][4]} | Minimum threshold: {item_contents[0][5]} | Last updated: {item_contents[0][6]}"
                    )
                except Exception as e:
                    print(f"An error occurred while retrieving item: {e}")
            elif requested_menu_action == "3":
                try:
                    item_name = input("Enter item to update: ")
                    if not validators.is_non_empty_string(item_name):
                        raise TypeError("Item must be non-empty string")
                    requested_menu_action = input(
                        "Action:\n[1] Increase quantity\n[2] Decrease quantity\n[3] Set quantity\n[4] Set expiration date\n[5] Set minimum threshold\n[6] Set description\n[7] Exit to inventory\n"
                    )
                    if requested_menu_action == "1":
                        quantity = int(input("Enter quantity to increase by: "))
                        if not validators.is_positive_int(quantity):
                            raise TypeError("Quantity must be positive integer")
                        inventory.increase_item(current_user, item_name, quantity)
                    elif requested_menu_action == "2":
                        quantity = int(input("Enter quantity to decrease by: "))
                        if not validators.is_positive_int(quantity):
                            raise TypeError("Quantity must be positive integer")
                        inventory.decrease_item(current_user, item_name, quantity)
                    elif requested_menu_action == "3":
                        quantity = int(input("Enter quantity to set: "))
                        if not validators.is_positive_int(quantity):
                            raise TypeError("Quantity must be positive integer")
                        inventory.set_quantity(current_user, item_name, quantity)
                    elif requested_menu_action == "4":
                        new_expiration = input("Enter new expiration date: ")
                        if not validators.is_valid_date(new_expiration):
                            raise TypeError(
                                "New expiration date must be YYYY-MM-DD format"
                            )
                        inventory.set_expiration(
                            current_user, item_name, new_expiration
                        )
                    elif requested_menu_action == "5":
                        new_threshold = int(
                            input("Enter new minimum alert threshold: ")
                        )
                        if not validators.is_positive_int(new_threshold):
                            raise TypeError("New threshold must be positive integer")
                        inventory.set_minimum_threshold(
                            current_user, item_name, new_threshold
                        )
                    elif requested_menu_action == "6":
                        new_description = input("Enter new description: ")
                        inventory.set_description(
                            current_user, item_name, new_description
                        )
                    else:
                        print("Action " + requested_menu_action + " is not valid")
                except Exception as e:
                    print(f"An error occurred while updating item: {e}")
            elif requested_menu_action == "4":
                try:
                    item_name = input("Enter item to add: ")
                    if not validators.is_non_empty_string(item_name):
                        raise TypeError("Item name must be non-empty string")
                    item_category = input("Enter item category: ")
                    if not validators.is_non_empty_string(item_category):
                        raise TypeError("Item category must be non-empty string")
                    item_description = input("Enter item description: ")
                    initial_quantity = input("Enter the initial quantity: ")
                    if not validators.is_positive_int(initial_quantity):
                        raise TypeError("Initial quantity must be positive integer")
                    expiration_date = input(
                        "Enter the expiration date (in YYYY-MM-DD format): "
                    )
                    if not validators.is_valid_date(expiration_date):
                        raise TypeError("Expiration date must be in YYYY-MM-DD format")
                    minimum_threshold = input("Enter the minimum threshold: ")
                    if not validators.is_positive_int(minimum_threshold):
                        raise TypeError(
                            "Minimum alert threshold must be positive integer"
                        )
                    inventory.add_inventory_item(
                        current_user,
                        item_name,
                        item_category,
                        item_description,
                        initial_quantity,
                        expiration_date,
                        minimum_threshold,
                    )
                except Exception as e:
                    print(f"An error occurred while adding item: {e}")
            elif requested_menu_action == "5":
                try:
                    item_name = input("Enter item to delete: ")
                    if not validators.is_non_empty_string(item_name):
                        raise TypeError("Item name must be non-empty string")
                    inventory.delete_item(current_user, item_name)
                except Exception as e:
                    print(f"An error occurred while deleting item: {e}")
            elif requested_menu_action == "6":
                menu_context = "main"
            else:
                print("Action " + requested_menu_action + " is not valid")
        elif current_user.role == "User":
            requested_menu_action = input(
                "Action:\n[1] Show all inventory\n[2] Show item\n[3] Update item\n[4] Exit to main menu\n"
            )
            if requested_menu_action == "1":
                table_contents = inventory.show_all_inventory(current_user)
                for row in table_contents:
                    print(
                        f"Item name: {row[0]} | Category: {row[1]} | Description: {row[2]} | Quantity: {row[3]} | Expiration date: {row[4]} | Minimum threshold: {row[5]} | Last updated: {row[6]}"
                    )
            elif requested_menu_action == "2":
                try:
                    item_name = input("Enter item name to view: ")
                    if not validators.is_non_empty_string(item_name):
                        raise TypeError("Item name must be non-empty string")
                    inventory.show_item(current_user, item_name)
                except Exception as e:
                    print(f"An error occurred while retrieving item: {e}")
            elif requested_menu_action == "3":
                try:
                    item_name = input("Enter item to update: ")
                    if not validators.is_non_empty_string(item_name):
                        raise TypeError("Item must be non-empty string")
                    requested_menu_action = input(
                        "Action:\n[1] Increase quantity\n[2] Decrease quantity\n[3] Set quantity\n[4] Set expiration date\n[5] Set minimum threshold\n[6] Set description\n[7] Exit to inventory\n"
                    )
                    if requested_menu_action == "1":
                        quantity = int(input("Enter quantity to increase by: "))
                        if not validators.is_positive_int(quantity):
                            raise TypeError("Quantity must be positive integer")
                        inventory.increase_item(current_user, item_name, quantity)
                    elif requested_menu_action == "2":
                        quantity = int(input("Enter quantity to decrease by: "))
                        if not validators.is_positive_int(quantity):
                            raise TypeError("Quantity must be positive integer")
                        inventory.decrease_item(current_user, item_name, quantity)
                    elif requested_menu_action == "3":
                        quantity = int(input("Enter quantity to set: "))
                        if not validators.is_positive_int(quantity):
                            raise TypeError("Quantity must be positive integer")
                        inventory.set_quantity(current_user, item_name, quantity)
                    elif requested_menu_action == "4":
                        new_expiration = input("Enter new expiration date: ")
                        if not validators.is_valid_date(new_expiration):
                            raise TypeError(
                                "New expiration date must be YYYY-MM-DD format"
                            )
                        inventory.set_expiration(
                            current_user, item_name, new_expiration
                        )
                    elif requested_menu_action == "5":
                        new_threshold = int(
                            input("Enter new minimum alert threshold: ")
                        )
                        if not validators.is_positive_int(new_threshold):
                            raise TypeError("New threshold must be positive integer")
                        inventory.set_minimum_threshold(
                            current_user, item_name, new_threshold
                        )
                    elif requested_menu_action == "6":
                        new_description = input("Enter new description: ")
                        inventory.set_description(
                            current_user, item_name, new_description
                        )
                    else:
                        print("Action " + requested_menu_action + " is not valid")
                except Exception as e:
                    print(f"An error occurred while updating item: {e}")
            elif requested_menu_action == "4":
                menu_context = "main"
            else:
                print("Action " + requested_menu_action + " is not valid")
        elif current_user.role == "Viewer":
            requested_menu_action = input(
                "Action:\n[1] Show all inventory\n[2] Show item\n[3] Exit to main menu\n"
            )
            if requested_menu_action == "1":
                table_contents = inventory.show_all_inventory(current_user)
                for row in table_contents:
                    print(
                        f"Item name: {row[0]} | Category: {row[1]} | Description: {row[2]} | Quantity: {row[3]} | Expiration date: {row[4]} | Minimum threshold: {row[5]} | Last updated: {row[6]}"
                    )
            elif requested_menu_action == "2":
                try:
                    item_name = input("Enter item name to view: ")
                    if not validators.is_non_empty_string(item_name):
                        raise TypeError("Item name must be non-empty string")
                    inventory.show_item(current_user, item_name)
                except Exception as e:
                    print(f"An error occurred while retrieving item: {e}")
            elif requested_menu_action == "3":
                menu_context = "main"
            else:
                print("Action " + requested_menu_action + " is not valid")
        else:
            print("You do not have permission for these functions")
            print("User permissions: " + current_user.role)
    elif menu_context == "users":
        if current_user.role == "Admin":
            requested_menu_action = input(
                "Action:\n[1] View user\n[2] Change user role\n[3] Add user\n[4] Delete user\n[5] View all users\n[6] Exit to main menu\n"
            )
            if requested_menu_action == "1":
                try:
                    username = input("Enter user to view: ")
                    if not validators.is_non_empty_string(username):
                        raise TypeError("Username must be non-empty string")
                    user_contents = users.view_user(current_user, username)
                    print(
                        f"User ID: {user_contents[0][0]} | Username: {user_contents[0][1]} | User role: {user_contents[0][3]} | User email: {user_contents[0][4]} | Date registered: {user_contents[0][5]} | Date last updated: {user_contents[0][6]}"
                    )
                except Exception as e:
                    print(f"An error occurred while retrieving user attributes: {e}")
            elif requested_menu_action == "2":
                try:
                    username = input("Enter user: ")
                    if not validators.is_non_empty_string(username):
                        raise TypeError("Username must be non-empty string")
                    new_role = input("Enter new role: ")
                    if not validators.is_valid_role(new_role):
                        raise TypeError("Role must be valid")
                    users.change_user_role(current_user, username, new_role)
                except Exception as e:
                    print(f"An error occurred while changing user role: {e}")
            elif requested_menu_action == "3":
                try:
                    username = input("Username: ")
                    if not validators.is_non_empty_string(username):
                        raise TypeError("Username must be non-empty string")
                    password = input("Password: ")
                    if not validators.is_non_empty_string(password):
                        raise TypeError("Password must be non-empty string")
                    role = input("User role: ")
                    if not validators.is_valid_role(role):
                        raise TypeError("Role must be valid")
                    email = input("User email: ")
                    if not validators.is_valid_email(email):
                        raise TypeError("Email must be valid format")
                    users.add_user(current_user, username, password, role, email)
                except Exception as e:
                    print(f"An error occurred while adding user: {e}")
            elif requested_menu_action == "4":
                try:
                    username = input("User to delete: ")
                    if not validators.is_non_empty_string(username):
                        raise TypeError("Username must be non-empty string")
                    users.delete_user(current_user, username)
                except Exception as e:
                    print(f"An error occurred while deleting user: {e}")
            elif requested_menu_action == "5":
                table_contents = users.show_all_users(current_user)
                for row in table_contents:
                    print(
                        f"Username: {row[0]} | Role: {row[1]} | Email: {row[2]} | Created at: {row[3]} | Last updated at: {row[4]}"
                    )
            elif requested_menu_action == "6":
                menu_context = "main"
            else:
                print("Action " + requested_menu_action + " is not valid")
        else:
            print("You do not have permission for these functions")
            print("User permissions: " + current_user.role)
    elif menu_context == "audit":
        if current_user.role == "Admin":
            requested_menu_action = input(
                "[1] View recent logs\n[2] Export audit log to .txt\n[3] Exit to main menu\n"
            )
            if requested_menu_action == "1":
                try:
                    number_of_entries = input("Pull last ___ logs: ")
                    if not validators.is_positive_int(number_of_entries):
                        raise TypeError("Number of entries must be positive integer")
                    log = audit_log.pull_audit_log(current_user, number_of_entries)
                    for entry in log:
                        print(
                            f"Log ID: {entry[0]} | User: {entry[1]} | Updated object: {entry[2]} | Action: {entry[3]} | Details: {entry[5]} | Time: {entry[4]}"
                        )
                except Exception as e:
                    print(f"An error occurred while viewing recent logs: {e}")
            elif requested_menu_action == "2":
                audit_log.export_to_txt(current_user)
                print("Audit log has been exported as .txt file")
            elif requested_menu_action == "3":
                menu_context = "main"
            else:
                print("Action " + requested_menu_action + " is not valid")
        else:
            print("You do not have permission for these functions")
            print("User permissions: " + current_user.role)
    elif menu_context == "alerts":
        requested_menu_action = input(
            "[1] Show expired inventory\n[2] Show low inventory\n[3] Exit to main menu\n"
        )
        if requested_menu_action == "1":
            expired_inventory = alerts.search_for_expiration()
            if not expired_inventory == []:
                print(
                    f"Item: {expired_inventory[0][0]} | Quantity: {expired_inventory[0][1]} | Expiration date: {expired_inventory[0][2]}"
                )
            else:
                print("There is no expired inventory")
        elif requested_menu_action == "2":
            low_inventory = alerts.search_for_low_quantity()
            if not low_inventory == []:
                print(
                    f"Item: {low_inventory[0][0]} | Quantity: {low_inventory[0][1]} | Minimum threshold: {low_inventory[0][2]}"
                )
            else:
                print("There is no low inventory")
        elif requested_menu_action == "3":
            menu_context = "main"
        else:
            print("Action " + requested_menu_action + " is not valid")
    elif menu_context == "account":
        requested_menu_action = input(
            "[1] Change username\n[2] Change password\n[3] Change email\n[4] Exit to main menu\n"
        )
        if requested_menu_action == "1":
            try:
                new_username = users.change_user_username(current_user)
                current_user.username = new_username
            except Exception as e:
                print(f"An error occurred while changing username: {e}")
        elif requested_menu_action == "2":
            users.change_user_password(current_user)
        elif requested_menu_action == "3":
            try:
                new_email = users.change_user_email(current_user)
                current_user.username = new_username
            except Exception as e:
                print(f"An error occurred while changing email: {e}")
        elif requested_menu_action == "4":
            menu_context = "main"
        else:
            print("Action " + requested_menu_action + " is not valid")
    else:
        print("Something went wrong.")
        menu_context = "main"
print("Logging out")
audit_log.update_audit_log(current_user, current_user.username, "LOGOUT", "Logged out")
