import tkinter as tk
from tkinter import messagebox, simpledialog, scrolledtext
import utils.validators as validators
import api.users as users
import api.inventory as inventory
import api.audit_log as audit_log
import api.alerts as alerts


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("EMS Inventory GUI")
        self.geometry("1000x600")
        self.attributes("-fullscreen", True)
        self.bind("<Escape>", lambda event: self.attributes("-fullscreen", False))
        self.current_user = None  # To hold the logged-in user
        # Container to stack frames on top of each other
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        # List of frames/screens to create
        for F in (
            LoginFrame,
            MainMenuFrame,
            InventoryFrame,
            UsersFrame,
            AuditFrame,
            AlertFrame,
            AccountFrame,
        ):
            frame = F(container, self)
            self.frames[F] = frame
            # Place all frames in the same location;
            # the one on the top of the stacking order will be visible.
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(LoginFrame)

    def show_frame(self, frame_class):
        """Raises the selected frame to the front."""
        frame = self.frames[frame_class]
        frame.tkraise()


class LoginFrame(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        tk.Label(self, text="Login", font=("Arial", 18)).pack(pady=20)

        form_frame = tk.Frame(self)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Username:").grid(
            row=0, column=0, padx=5, pady=5, sticky="e"
        )
        self.username_entry = tk.Entry(form_frame)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Password:").grid(
            row=1, column=0, padx=5, pady=5, sticky="e"
        )
        self.password_entry = tk.Entry(form_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(self, text="Login", command=self.perform_login).pack(pady=10)

    def perform_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        try:
            current_user = users.login(username, password)
            if current_user:
                # messagebox.showinfo("Login", "Login successful!")
                self.controller.current_user = current_user
                self.controller.show_frame(MainMenuFrame)
            else:
                messagebox.showerror("Login Error", "Invalid username or password.")
        except Exception as e:
            messagebox.showerror("An error occurred while logging in: ", str(e))


class MainMenuFrame(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        tk.Label(self, text="Main Menu", font=("Arial", 18)).pack(pady=20)

        tk.Button(
            self,
            text="Inventory management",
            width=25,
            command=lambda: controller.show_frame(InventoryFrame),
        ).pack(pady=10)
        tk.Button(
            self,
            text="User management",
            width=25,
            command=lambda: controller.show_frame(UsersFrame),
        ).pack(pady=10)
        tk.Button(
            self,
            text="Audit log",
            width=25,
            command=lambda: controller.show_frame(AuditFrame),
        ).pack(pady=10)
        tk.Button(
            self,
            text="Alerts",
            width=25,
            command=lambda: controller.show_frame(AlertFrame),
        ).pack(pady=10)
        tk.Button(
            self,
            text="Manage account",
            width=25,
            command=lambda: controller.show_frame(AccountFrame),
        ).pack(pady=10)
        tk.Button(self, text="Logout", width=25, command=self.logout).pack(pady=10)

    def logout(self):
        self.controller.current_user = None
        self.controller.show_frame(LoginFrame)


class ScrollableFrame(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        canvas = tk.Canvas(self)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)

        # Update the scrollregion when the inner frame changes
        self.scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


class InventoryFrame(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.selected_item = None  # Currently selected item name
        self.all_items = []  # Will hold all inventory items (as tuples)
        # Configure grid: left column (for buttons) and right column (for details & functions)
        self.grid_columnconfigure(0, weight=1, uniform="col")
        self.grid_columnconfigure(1, weight=3, uniform="col")
        self.grid_rowconfigure(0, weight=3)
        self.grid_rowconfigure(1, weight=1)

        # Left side: Item List and Bottom Buttons
        self.left_frame = tk.Frame(self)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.scrollable_frame = ScrollableFrame(self.left_frame)
        self.scrollable_frame.pack(fill="both", expand=True)

        # Search bar at top left
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda name, index, mode: self.filter_items)
        search_entry = tk.Entry(self.left_frame, textvariable=self.search_var)
        search_entry.pack(fill="x", padx=2, pady=2)

        self.left_bottom_frame = tk.Frame(self)
        self.left_bottom_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        self.add_item_button = tk.Button(
            self.left_bottom_frame, text="Add Item", command=self.add_item
        )
        self.add_item_button.pack(side="left", padx=5, pady=5)
        self.return_button = tk.Button(
            self.left_bottom_frame,
            text="Return to Menu",
            command=lambda: controller.show_frame(MainMenuFrame),
        )
        self.return_button.pack(side="left", padx=5, pady=5)

        # Right side: Item Details and Inventory Management Functions
        self.right_top_frame = tk.Frame(self)
        self.right_top_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.item_details_text = tk.Text(
            self.right_top_frame, wrap=tk.WORD, state="disabled"
        )
        self.item_details_text.pack(fill="both", expand=True)

        self.right_bottom_frame = tk.Frame(self)
        self.right_bottom_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

        self.increase_button = tk.Button(
            self.right_bottom_frame,
            text="Increase Quantity",
            command=self.increase_quantity,
        )
        self.increase_button.pack(side="left", padx=5, pady=5)

        self.decrease_button = tk.Button(
            self.right_bottom_frame,
            text="Decrease Quantity",
            command=self.decrease_quantity,
        )
        self.decrease_button.pack(side="left", padx=5, pady=5)

        self.set_button = tk.Button(
            self.right_bottom_frame, text="Set Quantity", command=self.set_quantity
        )
        self.set_button.pack(side="left", padx=5, pady=5)

        self.description_button = tk.Button(
            self.right_bottom_frame,
            text="Set Description",
            command=self.set_description,
        )
        self.description_button.pack(side="left", padx=5, pady=5)

        self.expiration_button = tk.Button(
            self.right_bottom_frame,
            text="Set Expiration Date",
            command=self.set_expiration,
        )
        self.expiration_button.pack(side="left", padx=5, pady=5)

        self.threshold_button = tk.Button(
            self.right_bottom_frame,
            text="Set Minimum Threshold",
            command=self.set_minimum_threshold,
        )
        self.threshold_button.pack(side="left", padx=5, pady=5)

        self.delete_button = tk.Button(
            self.right_bottom_frame,
            text="Delete Item",
            command=self.delete_item,
        )
        self.delete_button.pack(side="left", padx=5, pady=5)

        self.refresh_details_button = tk.Button(
            self.right_bottom_frame,
            text="Refresh Details",
            command=self.refresh_item_details,
        )
        self.refresh_details_button.pack(side="left", padx=5, pady=5)

        self.selected_item = None  # will hold the name of the currently selected item

    def tkraise(self, aboveThis=None):
        # When this frame is raised, refresh the inventory list.
        super().tkraise(aboveThis)
        self.refresh_inventory_list()

    def refresh_inventory_list(self):
        current_user = self.controller.current_user
        try:
            # Retrieve all items from the database and store them
            items = inventory.show_all_inventory(current_user)
            self.all_items = items if items else []
            # Initially, display all items
            self.populate_item_buttons(self.all_items)
        except Exception as e:
            messagebox.showerror("Inventory Error", str(e))

    def filter_items(self):
        query = self.search_var.get().lower()
        # Filter self.all_items based on the query in the item name
        filtered_items = [item for item in self.all_items if query in item[0].lower()]
        self.populate_item_buttons(filtered_items)

    def populate_item_buttons(self, items):
        # Clear existing buttons
        for widget in self.scrollable_frame.scrollable_frame.winfo_children():
            widget.destroy()
        # Create a button for each item in the provided list
        if items:
            for item in items:
                item_name = item[0]
                btn = tk.Button(
                    self.scrollable_frame.scrollable_frame,
                    text=item_name,
                    command=lambda name=item_name: self.show_item_details(name),
                )
                btn.pack(fill="x", padx=2, pady=2)
        else:
            tk.Label(
                self.scrollable_frame.scrollable_frame, text="No inventory items found."
            ).pack()

    def refresh_item_details(self):
        # Refresh details of the currently selected item
        if self.selected_item:
            self.show_item_details(self.selected_item)
        else:
            messagebox.showerror("Error", "No item selected.")

    def show_item_details(self, item_name):
        self.selected_item = item_name
        current_user = self.controller.current_user
        try:
            item_data = inventory.show_item(current_user, item_name)
            self.item_details_text.config(state="normal")
            self.item_details_text.delete("1.0", tk.END)
            if item_data and len(item_data) > 0:
                item = item_data[0]
                details = (
                    f"Item Name: {item[1]}\n"
                    f"Category: {item[2]}\n"
                    f"Description: {item[3]}\n"
                    f"Quantity: {item[4]}\n"
                    f"Expiration Date: {item[5]}\n"
                    f"Min Threshold: {item[6]}\n"
                    f"Last Updated: {item[7]}\n"
                )
                self.item_details_text.insert(tk.END, details)
            else:
                self.item_details_text.insert(tk.END, "No details available.")
            self.item_details_text.config(state="disabled")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def add_item(self):
        current_user = self.controller.current_user
        # This method should open a dialog or new window to add an inventory item.
        try:
            item_name = simpledialog.askstring("Input", "Enter item to add: ")
            if not validators.is_non_empty_string(item_name):
                raise ValueError("Item name must be a non-empty string")
            item_category = simpledialog.askstring("Input", "Enter item category: ")
            if not validators.is_non_empty_string(item_category):
                raise ValueError("Item category must be a non-empty string")
            item_description = simpledialog.askstring(
                "Input", "Enter item description (optional): "
            )
            initial_quantity = simpledialog.askinteger(
                "Input", "Enter the initial quantity: "
            )
            if not validators.is_positive_int(initial_quantity):
                raise ValueError("Initial quantity must be a positive integer")
            expiration_date = simpledialog.askstring(
                "Input", "Enter the expiration date (YYYY-MM-DD): "
            )
            if not validators.is_valid_date(expiration_date):
                raise ValueError("Expiration date must be in YYYY-MM-DD format")
            minimum_threshold = simpledialog.askinteger(
                "Input", "Enter the minimum threshold: "
            )
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
            self.refresh_inventory_list()
            self.selected_item = item_name
            self.refresh_item_details()
        except Exception as e:
            print(f"Error adding item: {e}")

    def delete_item(self):
        current_user = self.controller.current_user
        try:
            if messagebox.askyesno(
                "Delete item", "Do you really want to delete this item?"
            ):
                inventory.delete_item(current_user, self.selected_item)
            self.refresh_inventory_list()
            self.refresh_item_details()
        except Exception as e:
            print(f"Error deleting item: {e}")

    def increase_quantity(self):
        current_user = self.controller.current_user
        try:
            quantity = simpledialog.askinteger("Input", "Increase by: ")
            if not validators.is_positive_int(quantity):
                raise TypeError("Quantity must be a positive integer")
            inventory.increase_item(current_user, self.selected_item, quantity)
            self.refresh_inventory_list()
            self.refresh_item_details()
        except Exception as e:
            print(f"An error occurred while increasing item quantity: {e}")

    def decrease_quantity(self):
        current_user = self.controller.current_user
        try:
            quantity = simpledialog.askinteger("Input", "Decrease by: ")
            if not validators.is_positive_int(quantity):
                raise TypeError("Quantity must be a positive integer")
            inventory.decrease_item(current_user, self.selected_item, quantity)
            self.refresh_inventory_list()
            self.refresh_item_details()
        except Exception as e:
            print(f"An error occurred while decreasing item quantity: {e}")

    def set_quantity(self):
        current_user = self.controller.current_user
        try:
            quantity = simpledialog.askinteger("Input", "Set quantity to: ")
            if not validators.is_positive_int(quantity):
                raise TypeError("Quantity must be a positive integer")
            inventory.set_quantity(current_user, self.selected_item, quantity)
            self.refresh_inventory_list()
            self.refresh_item_details()
        except Exception as e:
            print(f"An error occurred while setting item quantity: {e}")

    def set_expiration(self):
        current_user = self.controller.current_user
        try:
            expiration = simpledialog.askstring("Input", "New expiration date: ")
            if not validators.is_valid_date(expiration):
                raise TypeError("Date must be in YYYY-MM-DD format.")
            inventory.set_expiration(current_user, self.selected_item, expiration)
            self.refresh_inventory_list()
            self.refresh_item_details()
        except Exception as e:
            print(f"An error occurred while setting item expiration date: {e}")

    def set_description(self):
        current_user = self.controller.current_user
        try:
            description = simpledialog.askstring("Input", "New description: ")
            inventory.set_description(current_user, self.selected_item, description)
            self.refresh_inventory_list()
            self.refresh_item_details()
        except Exception as e:
            print(f"An error occurred while setting item description: {e}")

    def set_minimum_threshold(self):
        current_user = self.controller.current_user
        try:
            quantity = simpledialog.askinteger("Input", "Set minimum threshold to: ")
            if not validators.is_positive_int(quantity):
                raise TypeError("Quantity must be a positive integer")
            inventory.set_minimum_threshold(current_user, self.selected_item, quantity)
            self.refresh_inventory_list()
            self.refresh_item_details()
        except Exception as e:
            print(f"An error occurred while setting item minimum threshold: {e}")


class UsersFrame(tk.Frame):
    # TODO restructure user interface
    def show_all_users(self):
        self.user_text.config(state=tk.NORMAL)
        self.user_text.delete("1.0", tk.END)
        current_user = self.controller.current_user
        if current_user:
            try:
                users_list = users.show_all_users(current_user)
                if users_list:
                    for user in users_list:
                        # Each user is a tuple: (username, role, email, created_at, updated_at)
                        user_str = (
                            f"User ID: {user[0]}\n"
                            f"Username: {user[1]}\n"
                            f"Role: {user[2]}\n"
                            f"Email: {user[3]}\n"
                            f"Created: {user[4]}\n"
                            f"Updated: {user[5]}\n"
                            "----------------------------------------\n"
                        )
                        self.user_text.insert(tk.END, user_str)
                else:
                    self.user_text.insert(tk.END, "No users found.")
            except Exception as e:
                messagebox.showerror(
                    "An error occurred while retrieving all users: ", str(e)
                )
        else:
            messagebox.showerror("Error", "No current user. Please login again.")

    def view_user(self):
        self.user_text.config(state=tk.NORMAL)
        self.user_text.delete("1.0", tk.END)
        current_user = self.controller.current_user
        if current_user:
            try:
                username = simpledialog.askstring("Input", "Enter username to view: ")
                if not validators.is_non_empty_string(username):
                    raise ValueError("Username must be a non-empty string.")
                user_contents = users.view_user(current_user, username)
                if user_contents and len(user_contents) > 0:
                    user = user_contents[0]
                    user_str = (
                        f"User ID: {user[0]}\n"
                        f"Username: {user[1]}\n"
                        f"Role: {user[2]}\n"
                        f"Email: {user[3]}\n"
                        f"Created: {user[4]}\n"
                        f"Updated: {user[5]}\n"
                        "----------------------------------------\n"
                    )
                    self.user_text.insert(tk.END, user_str)
                else:
                    self.user_text.insert(tk.END, "No users found.")
            except Exception as e:
                messagebox.showerror(
                    "An error occurred while retrieving user " + username + ": ", str(e)
                )
        else:
            messagebox.showerror("Error", "No current user. Please login again.")

    def change_user_role(self):
        self.user_text.config(state=tk.NORMAL)
        self.user_text.delete("1.0", tk.END)
        current_user = self.controller.current_user
        if current_user:
            try:
                username = simpledialog.askstring("Input", "Enter username to change: ")
                if not validators.is_non_empty_string(username):
                    raise ValueError("Username must be a non-empty string.")
                new_role = simpledialog.askstring("Input", "Enter new role: ")
                if not validators.is_valid_role(new_role):
                    raise ValueError("Invalid role.")
                users.change_user_role(current_user, username, new_role)
                self.user_text.insert(
                    "User " + username + " role has been updated to " + new_role
                )
            except Exception as e:
                messagebox.showerror(
                    "An error occurred while updated user role: ", str(e)
                )
        else:
            messagebox.showerror("Error", "No current user. Please login again.")

    def delete_user(self):
        self.user_text.config(state=tk.NORMAL)
        self.user_text.delete("1.0", tk.END)
        current_user = self.controller.current_user
        if current_user:
            try:
                username = simpledialog.askstring("Input", "Enter username to delete: ")
                if not validators.is_non_empty_string(username):
                    raise ValueError("Username must be a non-empty string.")
                users.delete_user(current_user, username)
            except Exception as e:
                messagebox.showerror("User Error", str(e))
        else:
            messagebox.showerror("Error", "No current user. Please login again.")

    def add_user(self):
        self.user_text.config(state=tk.NORMAL)
        self.user_text.delete("1.0", tk.END)
        current_user = self.controller.current_user
        if current_user:
            try:
                username = simpledialog.askstring("Input", "Username: ")
                if not validators.is_non_empty_string(username):
                    raise ValueError("Username must be a non-empty string.")
                password = simpledialog.askstring("Input", "Password: ")
                if not validators.is_non_empty_string(password):
                    raise ValueError("Password must be a non-empty string.")
                role = simpledialog.askstring("Input", "User role: ")
                if not validators.is_valid_role(role):
                    raise ValueError("Invalid role.")
                email = simpledialog.askstring("Input", "User email: ")
                if not validators.is_valid_email(email):
                    raise ValueError("Email must be in valid format.")
                users.add_user(current_user, username, password, role, email)
            except Exception as e:
                messagebox.showerror("An error occurred while adding user: ", str(e))
        else:
            messagebox.showerror("Error", "No current user. Please login again.")


class AuditFrame(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        tk.Label(self, text="Audit Log", font=("Arial", 18)).pack(pady=20)

        # Listbox to display inventory items
        self.audit_text = scrolledtext.ScrolledText(
            self, wrap=tk.WORD, width=100, height=20
        )
        self.audit_text.pack(pady=10)

        tk.Button(self, text="View recent logs", command=self.view_recent_logs).pack(
            pady=5
        )
        tk.Button(
            self, text="Export to .txt file", command=self.export_logs_to_text
        ).pack(pady=5)
        tk.Button(
            self,
            text="Exit to main menu",
            command=lambda: controller.show_frame(MainMenuFrame),
        ).pack(pady=5)

    def view_recent_logs(self):
        self.audit_text.config(state=tk.NORMAL)
        self.audit_text.delete("1.0", tk.END)
        current_user = self.controller.current_user
        if current_user:
            try:
                number_of_entries_input = simpledialog.askinteger(
                    "Input", "Enter number of recent logs to pull: "
                )
                if not validators.is_positive_int(number_of_entries_input):
                    raise ValueError("Number of entries must be a positive integer.")
                log_entries = audit_log.pull_audit_log(
                    current_user, number_of_entries_input
                )
                for entry in log_entries:
                    audit_str = (
                        f"Log ID: {entry[0]}\n"
                        f"User: {entry[1]}\n"
                        f"Updated object: {entry[2]}\n"
                        f"Action: {entry[3]}\n"
                        f"Details: {entry[5]}\n"
                        f"Time: {entry[4]}\n"
                        "----------------------------------------\n"
                    )
                    self.audit_text.insert(tk.END, audit_str)
            except Exception as e:
                messagebox.showerror(
                    "An error occurred while retrieving audit logs: ", str(e)
                )
        else:
            messagebox.showerror("Error", "No current user. Please login again.")

    def export_logs_to_text(self):
        self.audit_text.config(state=tk.NORMAL)
        self.audit_text.delete("1.0", tk.END)
        current_user = self.controller.current_user
        try:
            audit_log.export_to_txt(current_user)
            self.audit_text.insert(
                tk.END, "Audit log has been exported as a .txt file."
            )
        except Exception as e:
            messagebox.showerror(
                f"An error occurred while exporting the audit log: {e}"
            )


class AlertFrame(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        tk.Label(self, text="Alerts", font=("Arial", 18)).pack(pady=20)

        # Listbox to display inventory items
        self.alert_text = scrolledtext.ScrolledText(
            self, wrap=tk.WORD, width=100, height=20
        )
        self.alert_text.pack(pady=10)

        tk.Button(
            self, text="View expired items", command=self.view_expired_items
        ).pack(pady=5)
        tk.Button(
            self, text="View low inventory", command=self.view_low_inventory
        ).pack(pady=5)
        tk.Button(
            self,
            text="Exit to main menu",
            command=lambda: controller.show_frame(MainMenuFrame),
        ).pack(pady=5)

    def view_expired_items(self):
        self.alert_text.config(state=tk.NORMAL)
        self.alert_text.delete("1.0", tk.END)
        try:
            expired_inventory = alerts.search_for_expiration()
            if expired_inventory:
                for item in expired_inventory:
                    alert_str = (
                        f"Item: {item[0]}\n"
                        f"Quantity: {item[1]}\n"
                        f"Expiration date: {item[2]}\n"
                        "----------------------------------------\n"
                    )
                    self.alert_text.insert(tk.END, alert_str)
            else:
                self.alert_text.insert(tk.END, "There is no expired inventory.")
        except Exception as e:
            messagebox.showerror(
                f"An error occurred while retrieving expired inventory: {e}"
            )

    def view_low_inventory(self):
        self.alert_text.config(state=tk.NORMAL)
        self.alert_text.delete("1.0", tk.END)
        try:
            low_inventory = alerts.search_for_low_quantity()
            if low_inventory:
                for item in low_inventory:
                    alert_str = (
                        f"Item: {item[0]}\n"
                        f"Quantity: {item[1]}\n"
                        f"Minimum threshold: {item[2]}\n"
                        "----------------------------------------\n"
                    )
                    self.alert_text.insert(tk.END, alert_str)
            else:
                self.alert_text.insert(tk.END, "There is no low inventory.")
        except Exception as e:
            messagebox.showerror(
                f"An error occurred while retrieving low inventory: {e}"
            )


class AccountFrame(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        tk.Label(self, text="Manage Account", font=("Arial", 18)).pack(pady=20)

        # Listbox to display inventory items
        self.account_text = scrolledtext.ScrolledText(
            self, wrap=tk.WORD, width=100, height=20
        )
        self.account_text.pack(pady=10)

        tk.Button(self, text="Change username", command=self.change_username).pack(
            pady=5
        )
        tk.Button(self, text="Change password", command=self.change_password).pack(
            pady=5
        )
        tk.Button(self, text="Change email", command=self.change_email).pack(pady=5)
        tk.Button(
            self,
            text="Exit to main menu",
            command=lambda: controller.show_frame(MainMenuFrame),
        ).pack(pady=5)

    def change_username(self):
        self.account_text.config(state=tk.NORMAL)
        self.account_text.delete("1.0", tk.END)
        current_user = self.controller.current_user
        try:
            current_password = simpledialog.askstring(
                "Input", "Verify your current password: "
            )
            login_check = users.login(current_user.username, current_password)
            if (login_check is not None) and (login_check is not False):
                new_username = simpledialog.askstring(
                    "Input", "Please enter your new username: "
                )
                if not validators.is_non_empty_string(new_username):
                    raise TypeError("New username must be non-empty string.")
                reentered = simpledialog.askstring(
                    "Input", "Reenter your new username: "
                )
                if reentered == new_username:
                    users.change_user_username(current_user, new_username)
                else:
                    self.account_text.insert(tk.END, "Usernames did not match.")
            else:
                self.account_text.insert(tk.END, "Password was not valid.")
        except Exception as e:
            messagebox.showerror(f"An error occurred while changing username: {e}")

    def change_password(self):
        self.account_text.config(state=tk.NORMAL)
        self.account_text.delete("1.0", tk.END)
        current_user = self.controller.current_user
        try:
            current_password = simpledialog.askstring(
                "Input", "Verify your current password: "
            )
            login_check = users.login(current_user.username, current_password)
            if (login_check is not None) and (login_check is not False):
                new_password = simpledialog.askstring(
                    "Input", "Please enter your new password: "
                )
                if not validators.is_non_empty_string(new_password):
                    raise TypeError("New password must be non-empty string.")
                reentered = simpledialog.askstring(
                    "Input", "Reenter your new password: "
                )
                if reentered == new_password:
                    users.change_user_password(current_user, new_password)
                else:
                    self.account_text.insert(tk.END, "Passwords did not match.")
            else:
                self.account_text.insert(tk.END, "Password was not valid.")
        except Exception as e:
            messagebox.showerror(f"An error occurred while changing password: {e}")

    def change_email(self):
        self.account_text.config(state=tk.NORMAL)
        self.account_text.delete("1.0", tk.END)
        current_user = self.controller.current_user
        try:
            current_password = simpledialog.askstring(
                "Input", "Verify your current password: "
            )
            login_check = users.login(current_user.username, current_password)
            if (login_check is not None) and (login_check is not False):
                new_email = simpledialog.askstring(
                    "Input", "Please enter your new email: "
                )
                if not validators.is_valid_email(new_email):
                    raise TypeError("New email must be valid.")
                reentered = simpledialog.askstring("Input", "Reenter your new email: ")
                if reentered == new_email:
                    users.change_user_email(current_user, new_email)
                else:
                    self.account_text.insert(tk.END, "Emails did not match.")
            else:
                self.account_text.insert(tk.END, "Email was not valid.")
        except Exception as e:
            messagebox.showerror(f"An error occurred while changing email: {e}")


if __name__ == "__main__":
    app = App()
    app.mainloop()
