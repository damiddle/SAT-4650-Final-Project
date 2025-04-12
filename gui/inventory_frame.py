import tkinter as tk
from tkinter import messagebox, simpledialog
import api.inventory as inventory
import utils.validators as validators
from gui.scrollable_frame import ScrollableFrame


class InventoryFrame(tk.Frame):
    """Frame for inventory management functionality."""

    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.selected_item = None
        self.all_items = []
        self.grid_columnconfigure(0, weight=1, uniform="col")
        self.grid_columnconfigure(1, weight=3, uniform="col")
        self.grid_rowconfigure(0, weight=3)
        self.grid_rowconfigure(1, weight=1)

        self.left_frame = tk.Frame(self)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.scrollable_frame = ScrollableFrame(self.left_frame)
        self.scrollable_frame.pack(fill="both", expand=True)

        self.search_var = tk.StringVar()
        # Properly invoke the filter callback on change
        self.search_var.trace("w", lambda *args: self.filter_items())
        search_entry = tk.Entry(self.left_frame, textvariable=self.search_var)
        search_entry.pack(fill="x", padx=2, pady=2)

        self.left_bottom_frame = tk.Frame(self)
        self.left_bottom_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        self.add_item_button = tk.Button(
            self.left_bottom_frame, text="Add Item", command=self.add_item
        )

        self.return_button = tk.Button(
            self.left_bottom_frame,
            text="Return to Menu",
            command=lambda: controller.show_frame("MainMenuFrame"),
        )

        self.right_top_frame = tk.Frame(self)
        self.right_top_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        self.item_details_text = tk.Text(
            self.right_top_frame, wrap=tk.WORD, state="disabled"
        )
        self.item_details_text.pack(fill="both", expand=True)

        self.right_bottom_frame = tk.Frame(self)
        self.right_bottom_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

        # Inventory actions
        self.increase_button = tk.Button(
            self.right_bottom_frame,
            text="Increase Quantity",
            command=self.increase_quantity,
        )

        self.decrease_button = tk.Button(
            self.right_bottom_frame,
            text="Decrease Quantity",
            command=self.decrease_quantity,
        )

        self.set_button = tk.Button(
            self.right_bottom_frame, text="Set Quantity", command=self.set_quantity
        )

        self.description_button = tk.Button(
            self.right_bottom_frame,
            text="Set Description",
            command=self.set_description,
        )

        self.expiration_button = tk.Button(
            self.right_bottom_frame,
            text="Set Expiration Date",
            command=self.set_expiration,
        )

        self.threshold_button = tk.Button(
            self.right_bottom_frame,
            text="Set Minimum Threshold",
            command=self.set_minimum_threshold,
        )

        self.category_button = tk.Button(
            self.right_bottom_frame,
            text="Set Category",
            command=self.set_category,
        )

        self.delete_button = tk.Button(
            self.right_bottom_frame,
            text="Delete Item",
            command=self.delete_item,
        )

        self.refresh_details_button = tk.Button(
            self.right_bottom_frame,
            text="Refresh Details",
            command=self.refresh_item_details,
        )

        self.add_item_button.pack(side="left", padx=5, pady=5)
        self.return_button.pack(side="left", padx=5, pady=5)

        self.increase_button.pack(side="left", padx=5, pady=5)
        self.decrease_button.pack(side="left", padx=5, pady=5)
        self.set_button.pack(side="left", padx=5, pady=5)
        self.description_button.pack(side="left", padx=5, pady=5)
        self.expiration_button.pack(side="left", padx=5, pady=5)
        self.threshold_button.pack(side="left", padx=5, pady=5)
        self.category_button.pack(side="left", padx=5, pady=5)
        self.delete_button.pack(side="left", padx=5, pady=5)

        self.refresh_details_button.pack(side="left", padx=5, pady=5)

        self.selected_item = None

    def tkraise(self, aboveThis=None):
        """Overrides tkraise to refresh the inventory list when the frame is raised and update button visibility."""

        super().tkraise(aboveThis)
        self.refresh_inventory_list()
        self.update_button_visibility()

    def refresh_inventory_list(self):
        """Fetches and displays the list of inventory items."""

        current_user = self.controller.current_user
        try:
            items = inventory.show_all_inventory(current_user)
            self.all_items = items if items else []

            self.populate_item_buttons(self.all_items)
        except Exception as e:
            messagebox.showerror("Inventory Error", str(e))

    def update_button_visibility(self):
        """Allows filtering of inventory actions by role"""
        role = self.controller.current_user.role

        if role == "Admin":
            pass

        elif role == "Leadership":
            self.add_item_button.pack_forget()
            self.delete_button.pack_forget()

        elif role == "General Responder":
            self.add_item_button.pack_forget()
            self.delete_button.pack_forget()
            self.increase_button.pack_forget()
            self.decrease_button.pack_forget()
            self.set_button.pack_forget()
            self.description_button.pack_forget()
            self.expiration_button.pack_forget()
            self.threshold_button.pack_forget()

        else:
            messagebox.showerror("Something went wrong, user has no valid role")
            self.controller.show_frame("MainMenuFrame")

    def filter_items(self):
        """Filters the displayed item buttons based on the search query."""

        query = self.search_var.get().lower()
        filtered_items = [item for item in self.all_items if query in item[0].lower()]

        self.populate_item_buttons(filtered_items)

    def populate_item_buttons(self, items):
        """Creates buttons for each inventory item in the scrollable frame.

        Args:
            items (list): A list of inventory items.
        """

        for widget in self.scrollable_frame.scrollable_frame.winfo_children():
            widget.destroy()

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
        """Refreshes the displayed details for the selected item."""

        if self.selected_item:
            self.show_item_details(self.selected_item)
        else:
            messagebox.showerror("Error", "No item selected.")

    def show_item_details(self, item_name):
        """Displays detailed information for a selected inventory item.

        Args:
            item_name (str): The name of the selected inventory item.
        """

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
        """Adds a new inventory item using user inputs."""

        current_user = self.controller.current_user
        try:
            item_name = simpledialog.askstring("Input", "Enter item to add: ")
            if not validators.is_non_empty_string(item_name):
                raise ValueError("Item name must be a non-empty string")

            item_category = simpledialog.askstring("Input", "Enter item category: ")
            if not validators.is_non_empty_string(item_category):
                raise ValueError("Item category must be a non-empty string")

            item_description = simpledialog.askstring(
                "Input", "Enter item description, optional: "
            )
            initial_quantity = simpledialog.askinteger(
                "Input", "Enter the initial quantity: "
            )

            if not validators.is_positive_int(initial_quantity):
                raise ValueError("Initial quantity must be a positive integer")

            expiration_date = simpledialog.askstring(
                "Input", "Enter the expiration date (YYYY-MM-DD), optional: "
            )

            if expiration_date is not None and expiration_date.strip() == "":
                expiration_date = None
            elif expiration_date and not validators.is_valid_date(expiration_date):
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
            messagebox.showerror(f"Error adding item: {e}")

    def delete_item(self):
        """Deletes the currently selected inventory item."""

        current_user = self.controller.current_user
        try:
            if messagebox.askyesno(
                "Delete item", "Do you really want to delete this item?"
            ):
                inventory.delete_item(current_user, self.selected_item)

            self.refresh_inventory_list()
            self.refresh_item_details()
        except Exception as e:
            messagebox.showerror(f"Error deleting item: {e}")

    def increase_quantity(self):
        """Increases the quantity of the selected inventory item."""

        current_user = self.controller.current_user
        try:
            quantity = simpledialog.askinteger("Input", "Increase by: ")

            if not validators.is_positive_int(quantity):
                raise TypeError("Quantity must be a positive integer")

            inventory.increase_item(current_user, self.selected_item, quantity)

            self.refresh_inventory_list()
            self.refresh_item_details()
        except Exception as e:
            messagebox.showerror(
                f"An error occurred while increasing item quantity: {e}"
            )

    def decrease_quantity(self):
        """Decreases the quantity of the selected inventory item."""

        current_user = self.controller.current_user
        try:
            quantity = simpledialog.askinteger("Input", "Decrease by: ")

            if not validators.is_positive_int(quantity):
                raise TypeError("Quantity must be a positive integer")

            inventory.decrease_item(current_user, self.selected_item, quantity)

            self.refresh_inventory_list()
            self.refresh_item_details()
        except Exception as e:
            messagebox.showerror(
                f"An error occurred while decreasing item quantity: {e}"
            )

    def set_quantity(self):
        """Sets the quantity of the selected inventory item to a specific value."""

        current_user = self.controller.current_user
        try:
            quantity = simpledialog.askinteger("Input", "Set quantity to: ")

            if not validators.is_positive_int(quantity):
                raise TypeError("Quantity must be a positive integer")

            inventory.set_quantity(current_user, self.selected_item, quantity)

            self.refresh_inventory_list()
            self.refresh_item_details()
        except Exception as e:
            messagebox.showerror(f"An error occurred while setting item quantity: {e}")

    def set_expiration(self):
        """Updates the expiration date for the selected inventory item."""

        current_user = self.controller.current_user
        try:
            expiration = simpledialog.askstring("Input", "New expiration date: ")

            if not validators.is_valid_date(expiration):
                raise TypeError("Date must be in YYYY-MM-DD format.")

            inventory.set_expiration(current_user, self.selected_item, expiration)

            self.refresh_inventory_list()
            self.refresh_item_details()
        except Exception as e:
            messagebox.showerror(
                f"An error occurred while setting item expiration date: {e}"
            )

    def set_description(self):
        """Updates the description for the selected inventory item."""

        current_user = self.controller.current_user
        try:
            description = simpledialog.askstring("Input", "New description: ")

            inventory.set_description(current_user, self.selected_item, description)

            self.refresh_inventory_list()
            self.refresh_item_details()
        except Exception as e:
            messagebox.showerror(
                f"An error occurred while setting item description: {e}"
            )

    def set_minimum_threshold(self):
        """Sets the minimum threshold for the selected inventory item."""

        current_user = self.controller.current_user
        try:
            quantity = simpledialog.askinteger("Input", "Set minimum threshold to: ")

            if not validators.is_positive_int(quantity):
                raise TypeError("Quantity must be a positive integer")

            inventory.set_minimum_threshold(current_user, self.selected_item, quantity)

            self.refresh_inventory_list()
            self.refresh_item_details()
        except Exception as e:
            messagebox.showerror(
                f"An error occurred while setting item minimum threshold: {e}"
            )

    def set_category(self):
        """Updates the category for the selected inventory item."""

        current_user = self.controller.current_user
        try:
            category = simpledialog.askstring("Input", "New category: ")

            inventory.set_category(current_user, self.selected_item, category)

            self.refresh_inventory_list()
            self.refresh_item_details()
        except Exception as e:
            messagebox.showerror(f"An error occurred while setting item category: {e}")
