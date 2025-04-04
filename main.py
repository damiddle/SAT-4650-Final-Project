import getpass
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


def login_user():
    """Handles secure login using getpass and proper input validation."""
    valid_login = False
    while not valid_login:
        try:
            username = input("Username: ")
            if not validators.is_non_empty_string(username):
                raise ValueError("Username must be a non-empty string")
            # Using getpass to hide the password input
            password = getpass.getpass("Password: ")
            if not validators.is_non_empty_string(password):
                raise ValueError("Password must be a non-empty string")
            current_user = users.login(username, password)
            if current_user:
                valid_login = True
                return current_user
            else:
                print("Invalid credentials. Please try again.")
        except Exception as e:
            print(f"Error occurred during login: {e}")


def inventory_menu(current_user):
    """Handles inventory-related actions."""
    while True:
        if current_user.role not in ["Admin", "User", "Viewer"]:
            print("You do not have permission for these functions")
            return

        if current_user.role == "Admin":
            action = input(
                "Inventory Menu (Admin):\n"
                "[1] Show all inventory\n"
                "[2] Show item\n"
                "[3] Update item\n"
                "[4] Add new item\n"
                "[5] Delete item\n"
                "[6] Return to main menu\n"
            )
        elif current_user.role == "User":
            action = input(
                "Inventory Menu (User):\n"
                "[1] Show all inventory\n"
                "[2] Show item\n"
                "[3] Update item\n"
                "[4] Return to main menu\n"
            )
        elif current_user.role == "Viewer":
            action = input(
                "Inventory Menu (Viewer):\n"
                "[1] Show all inventory\n"
                "[2] Show item\n"
                "[3] Return to main menu\n"
            )

        if action == "1":
            try:
                table_contents = inventory.show_all_inventory(current_user)
                for row in table_contents:
                    print(
                        f"Item name: {row[0]} | Category: {row[1]} | Description: {row[2]} | "
                        f"Quantity: {row[3]} | Expiration date: {row[4]} | "
                        f"Minimum threshold: {row[5]} | Last updated: {row[6]}"
                    )
            except Exception as e:
                print(f"Error displaying inventory: {e}")

        elif action == "2":
            try:
                item_name = input("Enter item name to view: ")
                if not validators.is_non_empty_string(item_name):
                    raise ValueError("Item name must be a non-empty string")
                item_contents = inventory.show_item(current_user, item_name)
                if item_contents and len(item_contents) > 0:
                    row = item_contents[0]
                    print(
                        f"Item name: {row[0]} | Category: {row[1]} | Description: {row[2]} | "
                        f"Quantity: {row[3]} | Expiration date: {row[4]} | "
                        f"Minimum threshold: {row[5]} | Last updated: {row[6]}"
                    )
                else:
                    print("Item not found.")
            except Exception as e:
                print(f"Error retrieving item: {e}")

        elif action == "3":
            try:
                item_name = input("Enter item to update: ")
                if not validators.is_non_empty_string(item_name):
                    raise ValueError("Item must be a non-empty string")
                update_action = input(
                    "Update Options:\n"
                    "[1] Increase quantity\n"
                    "[2] Decrease quantity\n"
                    "[3] Set quantity\n"
                    "[4] Set expiration date\n"
                    "[5] Set minimum threshold\n"
                    "[6] Set description\n"
                    "[7] Cancel\n"
                )
                if update_action in ["1", "2", "3"]:
                    quantity_input = input("Enter quantity: ")
                    try:
                        quantity = int(quantity_input)
                    except ValueError:
                        raise ValueError("Quantity must be a positive integer")
                    if not validators.is_positive_int(quantity):
                        raise ValueError("Quantity must be a positive integer")
                    if update_action == "1":
                        inventory.increase_item(current_user, item_name, quantity)
                    elif update_action == "2":
                        inventory.decrease_item(current_user, item_name, quantity)
                    elif update_action == "3":
                        inventory.set_quantity(current_user, item_name, quantity)
                elif update_action == "4":
                    new_expiration = input("Enter new expiration date (YYYY-MM-DD): ")
                    if not validators.is_valid_date(new_expiration):
                        raise ValueError(
                            "New expiration date must be in YYYY-MM-DD format"
                        )
                    inventory.set_expiration(current_user, item_name, new_expiration)
                elif update_action == "5":
                    threshold_input = input("Enter new minimum threshold: ")
                    try:
                        new_threshold = int(threshold_input)
                    except ValueError:
                        raise ValueError("New threshold must be a positive integer")
                    if not validators.is_positive_int(new_threshold):
                        raise ValueError("New threshold must be a positive integer")
                    inventory.set_minimum_threshold(
                        current_user, item_name, new_threshold
                    )
                elif update_action == "6":
                    new_description = input("Enter new description: ")
                    inventory.set_description(current_user, item_name, new_description)
                elif update_action == "7":
                    print("Update cancelled.")
                else:
                    print("Invalid update action")
            except Exception as e:
                print(f"Error updating item: {e}")

        elif action == "4" and current_user.role == "Admin":
            try:
                item_name = input("Enter item to add: ")
                if not validators.is_non_empty_string(item_name):
                    raise ValueError("Item name must be a non-empty string")
                item_category = input("Enter item category: ")
                if not validators.is_non_empty_string(item_category):
                    raise ValueError("Item category must be a non-empty string")
                item_description = input("Enter item description: ")
                initial_quantity_input = input("Enter the initial quantity: ")
                try:
                    initial_quantity = int(initial_quantity_input)
                except ValueError:
                    raise ValueError("Initial quantity must be a positive integer")
                if not validators.is_positive_int(initial_quantity):
                    raise ValueError("Initial quantity must be a positive integer")
                expiration_date = input("Enter the expiration date (YYYY-MM-DD): ")
                if not validators.is_valid_date(expiration_date):
                    raise ValueError("Expiration date must be in YYYY-MM-DD format")
                minimum_threshold_input = input("Enter the minimum threshold: ")
                try:
                    minimum_threshold = int(minimum_threshold_input)
                except ValueError:
                    raise ValueError("Minimum threshold must be a positive integer")
                if not validators.is_positive_int(minimum_threshold):
                    raise ValueError("Minimum threshold must be a positive integer")
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
                print(f"Error adding item: {e}")

        elif action == "5" and current_user.role == "Admin":
            try:
                item_name = input("Enter item to delete: ")
                if not validators.is_non_empty_string(item_name):
                    raise ValueError("Item name must be a non-empty string")
                inventory.delete_item(current_user, item_name)
            except Exception as e:
                print(f"Error deleting item: {e}")

        elif (action == "6" and current_user.role in ["Admin"]) or (
            action == "4" and current_user.role in ["User", "Viewer"]
        ):
            break

        else:
            print("Invalid action. Please try again.")


def users_menu(current_user):
    """Handles user management (Admin only)."""
    if current_user.role != "Admin":
        print("You do not have permission for these functions")
        return
    while True:
        action = input(
            "Users Menu:\n"
            "[1] View user\n"
            "[2] Change user role\n"
            "[3] Add user\n"
            "[4] Delete user\n"
            "[5] View all users\n"
            "[6] Return to main menu\n"
        )
        if action == "1":
            try:
                username = input("Enter username to view: ")
                if not validators.is_non_empty_string(username):
                    raise ValueError("Username must be a non-empty string")
                user_contents = users.view_user(current_user, username)
                if user_contents and len(user_contents) > 0:
                    row = user_contents[0]
                    print(
                        f"User ID: {row[0]} | Username: {row[1]} | Role: {row[3]} | "
                        f"Email: {row[4]} | Registered: {row[5]} | Last updated: {row[6]}"
                    )
                else:
                    print("User not found.")
            except Exception as e:
                print(f"Error retrieving user: {e}")

        elif action == "2":
            try:
                username = input("Enter username: ")
                if not validators.is_non_empty_string(username):
                    raise ValueError("Username must be a non-empty string")
                new_role = input("Enter new role: ")
                if not validators.is_valid_role(new_role):
                    raise ValueError("Invalid role")
                users.change_user_role(current_user, username, new_role)
            except Exception as e:
                print(f"Error changing user role: {e}")

        elif action == "3":
            try:
                username = input("Username: ")
                if not validators.is_non_empty_string(username):
                    raise ValueError("Username must be a non-empty string")
                password = getpass.getpass("Password: ")
                if not validators.is_non_empty_string(password):
                    raise ValueError("Password must be a non-empty string")
                role = input("User role: ")
                if not validators.is_valid_role(role):
                    raise ValueError("Invalid role")
                email = input("User email: ")
                if not validators.is_valid_email(email):
                    raise ValueError("Email must be in valid format")
                users.add_user(current_user, username, password, role, email)
            except Exception as e:
                print(f"Error adding user: {e}")

        elif action == "4":
            try:
                username = input("Enter username to delete: ")
                if not validators.is_non_empty_string(username):
                    raise ValueError("Username must be a non-empty string")
                users.delete_user(current_user, username)
            except Exception as e:
                print(f"Error deleting user: {e}")

        elif action == "5":
            try:
                table_contents = users.show_all_users(current_user)
                for row in table_contents:
                    print(
                        f"Username: {row[0]} | Role: {row[1]} | Email: {row[2]} | "
                        f"Created at: {row[3]} | Last updated: {row[4]}"
                    )
            except Exception as e:
                print(f"Error displaying all users: {e}")

        elif action == "6":
            break
        else:
            print("Invalid action. Please try again.")


def audit_menu(current_user):
    """Handles audit log actions (Admin only)."""
    if current_user.role != "Admin":
        print("You do not have permission for these functions")
        return
    while True:
        action = input(
            "Audit Log Menu:\n"
            "[1] View recent logs\n"
            "[2] Export audit log to .txt\n"
            "[3] Return to main menu\n"
        )
        if action == "1":
            try:
                number_of_entries_input = input("Enter number of recent logs to pull: ")
                try:
                    number_of_entries = int(number_of_entries_input)
                except ValueError:
                    raise ValueError("Number of entries must be a positive integer")
                if not validators.is_positive_int(number_of_entries):
                    raise ValueError("Number of entries must be a positive integer")
                log_entries = audit_log.pull_audit_log(current_user, number_of_entries)
                for entry in log_entries:
                    print(
                        f"Log ID: {entry[0]} | User: {entry[1]} | Updated object: {entry[2]} | "
                        f"Action: {entry[3]} | Details: {entry[5]} | Time: {entry[4]}"
                    )
            except Exception as e:
                print(f"Error retrieving logs: {e}")
        elif action == "2":
            try:
                audit_log.export_to_txt(current_user)
                print("Audit log has been exported as a .txt file")
            except Exception as e:
                print(f"Error exporting audit log: {e}")
        elif action == "3":
            break
        else:
            print("Invalid action. Please try again.")


def alerts_menu(current_user):
    """Handles alert-related actions."""
    while True:
        action = input(
            "Alerts Menu:\n"
            "[1] Show expired inventory\n"
            "[2] Show low inventory\n"
            "[3] Return to main menu\n"
        )
        if action == "1":
            try:
                expired_inventory = alerts.search_for_expiration()
                if expired_inventory:
                    for item in expired_inventory:
                        print(
                            f"Item: {item[0]} | Quantity: {item[1]} | Expiration date: {item[2]}"
                        )
                else:
                    print("There is no expired inventory")
            except Exception as e:
                print(f"Error retrieving expired inventory: {e}")
        elif action == "2":
            try:
                low_inventory = alerts.search_for_low_quantity()
                if low_inventory:
                    for item in low_inventory:
                        print(
                            f"Item: {item[0]} | Quantity: {item[1]} | Minimum threshold: {item[2]}"
                        )
                else:
                    print("There is no low inventory")
            except Exception as e:
                print(f"Error retrieving low inventory: {e}")
        elif action == "3":
            break
        else:
            print("Invalid action. Please try again.")


def account_menu(current_user):
    """Handles account management actions."""
    while True:
        action = input(
            "Account Management Menu:\n"
            "[1] Change username\n"
            "[2] Change password\n"
            "[3] Change email\n"
            "[4] Return to main menu\n"
        )
        if action == "1":
            try:
                new_username = users.change_user_username(current_user)
                current_user.username = new_username
            except Exception as e:
                print(f"Error changing username: {e}")
        elif action == "2":
            try:
                users.change_user_password(current_user)
            except Exception as e:
                print(f"Error changing password: {e}")
        elif action == "3":
            try:
                new_email = users.change_user_email(current_user)
                current_user.email = new_email  # Fixed bug: correctly updating email
            except Exception as e:
                print(f"Error changing email: {e}")
        elif action == "4":
            break
        else:
            print("Invalid action. Please try again.")


def main_menu(current_user):
    """Primary menu that routes to submenus based on user role."""
    while True:
        if current_user.role == "Admin":
            action = input(
                "Main Menu (Admin):\n"
                "[1] Inventory Menu\n"
                "[2] Users Menu\n"
                "[3] Audit Log Menu\n"
                "[4] Alerts Menu\n"
                "[5] Account Management\n"
                "[6] Log out\n"
            )
            if action == "1":
                inventory_menu(current_user)
            elif action == "2":
                users_menu(current_user)
            elif action == "3":
                audit_menu(current_user)
            elif action == "4":
                alerts_menu(current_user)
            elif action == "5":
                account_menu(current_user)
            elif action == "6":
                break
            else:
                print("Invalid action. Please try again.")
        elif current_user.role == "User":
            action = input(
                "Main Menu (User):\n"
                "[1] Inventory Menu\n"
                "[2] Alerts Menu\n"
                "[3] Account Management\n"
                "[4] Log out\n"
            )
            if action == "1":
                inventory_menu(current_user)
            elif action == "2":
                alerts_menu(current_user)
            elif action == "3":
                account_menu(current_user)
            elif action == "4":
                break
            else:
                print("Invalid action. Please try again.")
        elif current_user.role == "Viewer":
            action = input(
                "Main Menu (Viewer):\n"
                "[1] Inventory Menu\n"
                "[2] Alerts Menu\n"
                "[3] Account Management\n"
                "[4] Log out\n"
            )
            if action == "1":
                inventory_menu(current_user)
            elif action == "2":
                alerts_menu(current_user)
            elif action == "3":
                account_menu(current_user)
            elif action == "4":
                break
            else:
                print("Invalid action. Please try again.")
        else:
            print("You do not have permission for these functions")
            break


def main():
    current_user = login_user()
    main_menu(current_user)
    print("Logging out")
    audit_log.update_audit_log(
        current_user, current_user.username, "LOGOUT", "Logged out"
    )


if __name__ == "__main__":
    main()
