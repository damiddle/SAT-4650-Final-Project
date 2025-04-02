import api.inventory as inventory
import api.users as users
import api.audit_log as audit_log
import api.alerts as alerts


class CurrentUser:
    def __init__(self, username, role, email):
        self.username = username
        self.role = role
        self.email = email


# Log in sequence, creates current user class
valid_login = False

while not valid_login:
    username = input("Username: ")
    password = input("Password: ")

    current_user = users.login(username, password)

    if current_user is not False or None:
        valid_login = True


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
                table_contents = inventory.show_all_inventory(current_user)

                for row in table_contents:
                    print(
                        f"Item name: {row[0]} | Category: {row[1]} | Description: {row[2]} | Quantity: {row[3]} | Expiration date: {row[4]} | Minimum threshold: {row[5]} | Last updated: {row[6]}"
                    )

            # Show item
            elif requested_menu_action == "2":
                item_name = input("Enter item name to view: ")

                inventory.show_item(current_user, item_name)

            # Update item
            elif requested_menu_action == "3":
                item_name = input("Enter item to update: ")
                requested_menu_action = input(
                    "Action:\n[1] Increase quantity\n[2] Decrease quantity\n[3] Set quantity\n[4] Set expiration date\n[5] Set minimum threshold\n[6] Set description\n[7] Exit to inventory\n"
                )

                if requested_menu_action == "1":
                    quantity = int(input("Enter quantity to increase by: "))
                    inventory.increase_item(current_user, item_name, quantity)

                elif requested_menu_action == "2":
                    quantity = int(input("Enter quantity to decrease by: "))
                    inventory.decrease_item(current_user, item_name, quantity)

                elif requested_menu_action == "3":
                    quantity = int(input("Enter quantity to set: "))
                    inventory.set_quantity(current_user, item_name, quantity)

                elif requested_menu_action == "4":
                    new_expiration = input("Enter new expiration date: ")
                    inventory.set_expiration(current_user, item_name, new_expiration)

                elif requested_menu_action == "5":
                    new_threshold = int(input("Enter new minimum alert threshold: "))
                    inventory.set_minimum_threshold(
                        current_user, item_name, new_threshold
                    )

                elif requested_menu_action == "6":
                    new_description = input("Enter new description: ")
                    inventory.set_description(current_user, item_name, new_description)

                else:
                    print("Action not valid")

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
                table_contents = inventory.show_all_inventory(current_user)

                for row in table_contents:
                    print(
                        f"Item name: {row[0]} | Category: {row[1]} | Description: {row[2]} | Quantity: {row[3]} | Expiration date: {row[4]} | Minimum threshold: {row[5]} | Last updated: {row[6]}"
                    )

            # Show item
            elif requested_menu_action == "2":
                item_name = input("Enter item name to view: ")

                inventory.show_item(current_user, item_name)

            # Update item
            elif requested_menu_action == "3":
                item_name = input("Enter item to update: ")
                requested_menu_action = input(
                    "Action:\n[1] Increase quantity\n[2] Decrease quantity\n[3] Set quantity\n[4] Set expiration date\n[5] Set minimum threshold\n[6] Set description\n[7] Exit to inventory\n"
                )

                if requested_menu_action == "1":
                    quantity = int(input("Enter quantity to increase by: "))
                    inventory.increase_item(current_user, item_name, quantity)

                elif requested_menu_action == "2":
                    quantity = int(input("Enter quantity to decrease by: "))
                    inventory.decrease_item(current_user, item_name, quantity)

                elif requested_menu_action == "3":
                    quantity = int(input("Enter quantity to set: "))
                    inventory.set_quantity(current_user, item_name, quantity)

                elif requested_menu_action == "4":
                    new_expiration = input("Enter new expiration date: ")
                    inventory.set_expiration(current_user, item_name, new_expiration)

                elif requested_menu_action == "5":
                    new_threshold = int(input("Enter new minimum alert threshold: "))
                    inventory.set_minimum_threshold(
                        current_user, item_name, new_threshold
                    )

                elif requested_menu_action == "6":
                    new_description = input("Enter new description: ")
                    inventory.set_description(current_user, item_name, new_description)

                else:
                    print("Action not valid")

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
                table_contents = inventory.show_all_inventory(current_user)

                for row in table_contents:
                    print(
                        f"Item name: {row[0]} | Category: {row[1]} | Description: {row[2]} | Quantity: {row[3]} | Expiration date: {row[4]} | Minimum threshold: {row[5]} | Last updated: {row[6]}"
                    )

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

    # User management functions, admin only
    elif menu_context == "users":
        if current_user.role == "Admin":
            requested_menu_action = input(
                "Action:\n[1] View user\n[2] Change user role\n[3] Add user\n[4] Delete user\n[5] View all users\n[6] Exit to main menu\n"
            )

            # View user
            if requested_menu_action == "1":
                user = input("Enter user to view: ")

                try:
                    print(users.view_user(current_user, user))

                except Exception as e:
                    print(f"Database error: {e}")

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

            # View all registered users
            elif requested_menu_action == "5":
                table_contents = users.show_all_users(current_user)

                for row in table_contents:
                    print(
                        f"Username: {row[0]} | Role: {row[1]} | Email: {row[2]} | Created at: {row[3]} | Last updated at: {row[4]}"
                    )

            # Exit to main menu
            elif requested_menu_action == "6":
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

                log = audit_log.pull_audit_log(current_user, number_of_entries)

                for entry in log:
                    print(
                        f"Log ID: {entry[0]} | User: {entry[1]} | Updated object: {entry[2]} | Action: {entry[3]} | Details: {entry[5]} | Time: {entry[4]}"
                    )

            # Exports audit log to .txt
            elif requested_menu_action == "2":
                audit_log.export_to_txt(current_user)

                print("Audit log has been exported as .txt file")

            # Exit to main menu
            elif requested_menu_action == "3":
                menu_context = "main"

            else:
                print("Action not valid")

        else:
            print("You do not have permission for these functions")

    # Alert functions, all users
    elif menu_context == "alerts":
        requested_menu_action = input(
            "[1] Show expired inventory\n[2] Show low inventory\n[3] Exit to main menu\n"
        )

        # View expired items
        if requested_menu_action == "1":
            alerts.search_for_expiration()

        # View low quantities
        elif requested_menu_action == "2":
            alerts.search_for_low_quantity()

        # Exit to main menu
        elif requested_menu_action == "3":
            menu_context = "main"

        else:
            print("Action not valid")

    # Account management functions, all users
    # TODO changing attributes does not update current_user
    elif menu_context == "account":
        requested_menu_action = input(
            "[1] Change username\n[2] Change password\n[3] Change email\n[4] Exit to main menu\n"
        )

        # Change username
        if requested_menu_action == "1":
            users.change_user_username(current_user)

        # Change password
        elif requested_menu_action == "2":
            users.change_user_password(current_user)

        # Change email
        elif requested_menu_action == "3":
            users.change_user_email(current_user)

        # Exit to main menu
        elif requested_menu_action == "4":
            menu_context = "main"

        else:
            print("Action not valid")

    else:
        print("Something went wrong")
        menu_context = "main"


print("Logging out")
audit_log.update_audit_log(current_user, current_user.username, "LOGOUT", "Logged out")
