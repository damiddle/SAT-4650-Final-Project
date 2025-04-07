import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import scrolledtext
import utils.validators as validators
import api.users as users
import api.inventory as inventory


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("EMS Inventory GUI")
        self.geometry("800x600")
        self.current_user = None  # To hold the logged-in user
        # Container to stack frames on top of each other
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        # List of frames/screens to create
        for F in (LoginFrame, MainMenuFrame, InventoryFrame, UsersFrame):
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
            messagebox.showerror("Login Error", str(e))


class MainMenuFrame(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        tk.Label(self, text="Main Menu", font=("Arial", 18)).pack(pady=20)

        tk.Button(
            self,
            text="Inventory Management",
            width=25,
            command=lambda: controller.show_frame(InventoryFrame),
        ).pack(pady=10)
        tk.Button(
            self,
            text="User Management",
            width=25,
            command=lambda: controller.show_frame(UsersFrame),
        ).pack(pady=10)
        tk.Button(self, text="Logout", width=25, command=self.logout).pack(pady=10)

    def logout(self):
        self.controller.current_user = None
        self.controller.show_frame(LoginFrame)


class InventoryFrame(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        tk.Label(self, text="Inventory Management", font=("Arial", 18)).pack(pady=20)

        # Listbox to display inventory items
        self.inventory_text = scrolledtext.ScrolledText(
            self, wrap=tk.WORD, width=100, height=20
        )
        self.inventory_text.pack(pady=10)

        tk.Button(
            self, text="Show all inventory", command=self.show_all_inventory
        ).pack(pady=5)
        tk.Button(self, text="Show item", command=self.show_item).pack(pady=5)
        tk.Button(self, text="Update item", command=self.open_update_dialog).pack(
            pady=5
        )
        tk.Button(self, text="Add new item", command=self.add_item).pack(pady=5)
        tk.Button(self, text="Delete item", command=self.delete_item).pack(pady=5)
        tk.Button(
            self,
            text="Back to Main Menu",
            command=lambda: controller.show_frame(MainMenuFrame),
        ).pack(pady=5)

    def show_all_inventory(self):
        self.inventory_text.config(state=tk.NORMAL)
        self.inventory_text.delete("1.0", tk.END)
        current_user = self.controller.current_user
        if current_user:
            try:
                items = inventory.show_all_inventory(current_user)
                if items:
                    for item in items:
                        # Format each inventory item into a multi-line string
                        item_str = (
                            f"Item Name: {item[0]}\n"
                            f"Category: {item[1]}\n"
                            f"Description: {item[2]}\n"
                            f"Quantity: {item[3]}\n"
                            f"Expiration Date: {item[4]}\n"
                            f"Min Threshold: {item[5]}\n"
                            f"Last Updated: {item[6]}\n"
                            "----------------------------------------\n"
                        )
                        self.inventory_text.insert(tk.END, item_str)
                else:
                    self.inventory_text.insert(tk.END, "No inventory items found.\n")
            except Exception as e:
                messagebox.showerror("Inventory Error", str(e))
        else:
            messagebox.showerror("Error", "No current user. Please login again.")
        # Disable editing after populating the text
        self.inventory_text.config(state=tk.DISABLED)

    def show_item(self):
        self.inventory_text.config(state=tk.NORMAL)
        self.inventory_text.delete("1.0", tk.END)
        current_user = self.controller.current_user
        if current_user:
            try:
                user_input = simpledialog.askstring(
                    "Input", "Please enter the item name:"
                )
                item_contents = inventory.show_item(current_user, user_input)
                if item_contents and len(item_contents) > 0:
                    row = item_contents[0]
                    item_str = (
                        f"Item name: {row[1]} | Category: {row[2]} | Description: {row[3]} | "
                        f"Quantity: {row[4]} | Expiration date: {row[5]} | "
                        f"Minimum threshold: {row[6]} | Last updated: {row[7]}"
                    )
                    self.inventory_text.insert(tk.END, item_str)
                else:
                    self.inventory_text.insert(tk.END, "Item not found.")
            except Exception as e:
                messagebox.showerror("Inventory Error", str(e))
        else:
            messagebox.showerror("Error", "No current user. Please login again.")

    def open_update_dialog(self):
        current_user = self.controller.current_user
        if current_user:
            # You could ask the user for the item name or let them select it from a list
            item_name = simpledialog.askstring(
                "Update Item", "Enter item name to update:"
            )
            if item_name:
                UpdateItemDialog(self, current_user, item_name)
        else:
            messagebox.showerror("Error", "No current user. Please login again.")

    def add_item(self):
        self.inventory_text.config(state=tk.NORMAL)
        self.inventory_text.delete("1.0", tk.END)
        current_user = self.controller.current_user
        if current_user:
            try:
                item_name = simpledialog.askstring("Input", "Enter item to add: ")
                if not validators.is_non_empty_string(item_name):
                    raise ValueError("Item name must be a non-empty string")
                item_category = simpledialog.askstring("Input", "Enter item category: ")
                if not validators.is_non_empty_string(item_category):
                    raise ValueError("Item category must be a non-empty string")
                item_description = simpledialog.askstring(
                    "Input", "Enter item description: "
                )
                initial_quantity_input = simpledialog.askinteger(
                    "Input", "Enter the initial quantity: "
                )
                try:
                    initial_quantity = int(initial_quantity_input)
                except ValueError:
                    raise ValueError("Initial quantity must be a positive integer")
                if not validators.is_positive_int(initial_quantity):
                    raise ValueError("Initial quantity must be a positive integer")
                expiration_date = simpledialog.askstring(
                    "Input", "Enter the expiration date (YYYY-MM-DD): "
                )
                if not validators.is_valid_date(expiration_date):
                    raise ValueError("Expiration date must be in YYYY-MM-DD format")
                minimum_threshold_input = simpledialog.askinteger(
                    "Input", "Enter the minimum threshold: "
                )
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
                messagebox.showerror("Inventory Error", str(e))
        else:
            messagebox.showerror("Error", "No current user. Please login again.")

    def delete_item(self):
        self.inventory_text.config(state=tk.NORMAL)
        self.inventory_text.delete("1.0", tk.END)
        current_user = self.controller.current_user
        if current_user:
            try:
                item_name = simpledialog.askstring("Input", "Enter item to delete: ")
                if not validators.is_non_empty_string(item_name):
                    raise ValueError("Item name must be a non-empty string")
                inventory.delete_item(current_user, item_name)
            except Exception as e:
                messagebox.showerror("Inventory Error", str(e))
        else:
            messagebox.showerror("Error", "No current user. Please login again.")


class UpdateItemDialog(tk.Toplevel):
    def __init__(self, parent, current_user, item_name):
        super().__init__(parent)
        self.title("Update Item")
        self.current_user = current_user
        self.item_name = item_name
        self.geometry("400x300")
        self.transient(parent)  # Set the window to be on top of the parent
        self.grab_set()  # Make the dialog modal

        tk.Label(self, text=f"Update '{item_name}'", font=("Arial", 14)).pack(pady=10)

        # Dropdown for update options
        self.update_type_var = tk.StringVar(value="Increase quantity")
        options = [
            "Increase quantity",
            "Decrease quantity",
            "Set quantity",
            "Set expiration date",
            "Set minimum threshold",
            "Set description",
        ]
        tk.Label(self, text="Select update type:").pack(pady=5)
        tk.OptionMenu(self, self.update_type_var, *options).pack(pady=5)

        # Entry for new value
        tk.Label(self, text="Enter new value:").pack(pady=5)
        self.value_entry = tk.Entry(self)
        self.value_entry.pack(pady=5)

        # Action buttons
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Update", command=self.perform_update).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(button_frame, text="Cancel", command=self.destroy).pack(
            side=tk.LEFT, padx=5
        )

    def perform_update(self):
        update_type = self.update_type_var.get()
        new_value = self.value_entry.get()

        try:
            if update_type == "Increase quantity":
                quantity = int(new_value)
                inventory.increase_item(self.current_user, self.item_name, quantity)
            elif update_type == "Decrease quantity":
                quantity = int(new_value)
                inventory.decrease_item(self.current_user, self.item_name, quantity)
            elif update_type == "Set quantity":
                quantity = int(new_value)
                inventory.set_quantity(self.current_user, self.item_name, quantity)
            elif update_type == "Set expiration date":
                # Here you might want to validate the date format
                inventory.set_expiration(self.current_user, self.item_name, new_value)
            elif update_type == "Set minimum threshold":
                threshold = int(new_value)
                inventory.set_minimum_threshold(
                    self.current_user, self.item_name, threshold
                )
            elif update_type == "Set description":
                inventory.set_description(self.current_user, self.item_name, new_value)
            else:
                messagebox.showerror("Error", "Unknown update type.")
                return

            messagebox.showinfo("Success", f"{self.item_name} updated successfully!")
            self.destroy()  # Close the dialog
        except Exception as e:
            messagebox.showerror("Update Error", str(e))


class UsersFrame(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        tk.Label(self, text="User Management", font=("Arial", 18)).pack(pady=20)

        # Listbox to display users
        self.users_listbox = tk.Listbox(self, width=100)
        self.users_listbox.pack(pady=10)

        tk.Button(self, text="View user", command=self.view_user).pack(pady=5)
        tk.Button(self, text="Change user role", command=self.change_user_role).pack(
            pady=5
        )
        tk.Button(self, text="Add user", command=self.add_user).pack(pady=5)
        tk.Button(self, text="Delete user", command=self.delete_user).pack(pady=5)
        tk.Button(self, text="Show All Users", command=self.show_all_users).pack(pady=5)
        tk.Button(
            self,
            text="Back to Main Menu",
            command=lambda: controller.show_frame(MainMenuFrame),
        ).pack(pady=5)

    def show_all_users(self):
        self.users_listbox.delete(0, tk.END)
        current_user = self.controller.current_user
        if current_user:
            try:
                users_list = users.show_all_users(current_user)
                if users_list:
                    for user in users_list:
                        # Each user is a tuple: (username, role, email, created_at, updated_at)
                        user_str = (
                            f"{user[0]} | {user[1]} | {user[2]} | "
                            f"Created: {user[3]} | Updated: {user[4]}"
                        )
                        self.users_listbox.insert(tk.END, user_str)
                else:
                    self.users_listbox.insert(tk.END, "No users found.")
            except Exception as e:
                messagebox.showerror("User Error", str(e))
        else:
            messagebox.showerror("Error", "No current user. Please login again.")

    def view_user(self):
        pass

    def change_user_role(self):
        pass

    def delete_user(self):
        pass

    def add_user(self):
        pass


class AuditFrame(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        tk.Label(self, text="Audit Log", font=("Arial", 18)).pack(pady=20)

        # Listbox to display inventory items
        self.inventory_text = scrolledtext.ScrolledText(
            self, wrap=tk.WORD, width=100, height=20
        )
        self.inventory_text.pack(pady=10)

        tk.Button(self, text="View recent logs", command=self.show_all_inventory).pack(
            pady=5
        )
        tk.Button(self, text="Export to .txt file", command=self.show_item).pack(pady=5)
        tk.Button(
            self,
            text="Back to Main Menu",
            command=lambda: controller.show_frame(MainMenuFrame),
        ).pack(pady=5)

    def view_recent_logs(self):
        pass


if __name__ == "__main__":
    app = App()
    app.mainloop()
