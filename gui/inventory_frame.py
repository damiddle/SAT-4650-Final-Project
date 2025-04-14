import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import api.inventory as inventory
import utils.validators as validators
from gui.scrollable_frame import ScrollableFrame
from dotenv import load_dotenv
import os
import logging
import ast

logger = logging.getLogger(__name__)

ENV_FILE_PATH = ".env"
load_dotenv(ENV_FILE_PATH)

VALID_CATEGORIES = ast.literal_eval(os.getenv("VALID_CATEGORIES"))


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
            text="Increase",
            command=self.increase_quantity,
        )

        self.decrease_button = tk.Button(
            self.right_bottom_frame,
            text="Decrease",
            command=self.decrease_quantity,
        )

        self.set_button = tk.Button(
            self.right_bottom_frame, text="Change quantity", command=self.set_quantity
        )

        self.description_button = tk.Button(
            self.right_bottom_frame,
            text="Change description",
            command=self.set_description,
        )

        self.expiration_button = tk.Button(
            self.right_bottom_frame,
            text="Change expiration date",
            command=self.set_expiration,
        )

        self.threshold_button = tk.Button(
            self.right_bottom_frame,
            text="Change minimum alert threshold",
            command=self.set_minimum_threshold,
        )

        self.category_button = tk.Button(
            self.right_bottom_frame,
            text="Change category",
            command=self.set_category,
        )

        self.delete_button = tk.Button(
            self.right_bottom_frame,
            text="Delete item",
            command=self.delete_item,
        )

        self.refresh_details_button = tk.Button(
            self.right_bottom_frame,
            text="Refresh details",
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
            logger.error(f"Error refreshing inventory list: {e}")

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
            messagebox.showerror("Error", "Button visibility error")
            self.controller.show_frame("MainMenuFrame")

    def filter_items(self):
        """Filters the displayed item buttons based on the search query."""

        query = self.search_var.get().lower()
        filtered_items = [
            item
            for item in self.all_items
            if query in item[0].lower() or query in item[1].lower()
        ]

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
            logger.error("No item selected")

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
                    f"Name: {item[1]}\n"
                    f"Description: {item[3]}\n"
                    f"Category: {item[2]}\n"
                    f"Quantity: {item[4]}\n"
                    f"Expiration date: {item[5]}\n"
                    f"Minimum alert threshold: {item[6]}\n"
                    f"Last updated: {item[7]}\n"
                )

                self.item_details_text.insert(tk.END, details)
            else:
                self.item_details_text.insert(tk.END, "No details available.")

            self.item_details_text.config(state="disabled")
        except Exception as e:
            messagebox.showerror("Error", f"Error showing item details: {e}")
            logger.error(f"Error showing item details: {e}")

    def add_item(self):
        """Adds a new inventory item using user inputs."""

        current_user = self.controller.current_user

        popup = tk.Toplevel(self)
        popup.title("Add Inventory Item")

        item_name_frame = tk.Frame(popup)
        item_name_label = tk.Label(item_name_frame, text="Item name:")
        item_name_input = tk.Entry(item_name_frame)
        item_name_label.pack(side="left", padx=20, pady=10)
        item_name_input.pack(side="left", padx=20, pady=10)
        item_name_frame.pack()

        item_category_frame = tk.Frame(popup)
        item_category_label = tk.Label(item_category_frame, text="Category:")
        selected_category = tk.StringVar(popup)
        selected_category.set(VALID_CATEGORIES[0])
        item_category_dropdown = ttk.Combobox(
            item_category_frame,
            textvariable=selected_category,
            values=VALID_CATEGORIES,
            state="readonly",
        )
        item_category_label.pack(side="left", padx=20, pady=10)
        item_category_dropdown.pack(side="left", padx=20, pady=10)
        item_category_dropdown.current(0)
        item_category_frame.pack()

        item_quantity_frame = tk.Frame(popup)
        item_quantity_label = tk.Label(item_quantity_frame, text="Current quantity:")
        item_quantity_input = tk.Entry(item_quantity_frame)
        item_quantity_label.pack(side="left", padx=20, pady=10)
        item_quantity_input.pack(side="left", padx=20, pady=10)
        item_quantity_frame.pack()

        item_minimum_threshold_frame = tk.Frame(popup)
        item_minimum_threshold_label = tk.Label(
            item_minimum_threshold_frame, text="Minimum alert threshold (optional):"
        )
        item_minimum_threshold_input = tk.Entry(item_minimum_threshold_frame)
        item_minimum_threshold_label.pack(side="left", padx=20, pady=10)
        item_minimum_threshold_input.pack(side="left", padx=20, pady=10)
        item_minimum_threshold_frame.pack()

        item_expiration_frame = tk.Frame(popup)
        item_expiration_label = tk.Label(
            item_expiration_frame, text="Expiration date (YYYY-MM-DD, optional):"
        )
        item_expiration_input = tk.Entry(item_expiration_frame)
        item_expiration_label.pack(side="left", padx=20, pady=10)
        item_expiration_input.pack(side="left", padx=20, pady=10)
        item_expiration_frame.pack()

        item_description_frame = tk.Frame(popup)
        item_description_label = tk.Label(
            item_description_frame, text="Description (optional):"
        )
        item_description_input = tk.Entry(item_description_frame)
        item_description_label.pack(side="left", padx=20, pady=10)
        item_description_input.pack(side="left", padx=20, pady=10)
        item_description_frame.pack()

        def submit():
            try:
                item_name = item_name_input.get()
                if not validators.is_non_empty_string(item_name):
                    raise TypeError("Item name must be a non-empty string")

                category = selected_category.get()
                if not validators.is_non_empty_string(category):
                    raise TypeError("Item category must be a non-empty string")

                quantity = int(item_quantity_input.get())
                if not validators.is_positive_int(quantity):
                    raise TypeError("Item quantity must be a positive integer")

                minimum_threshold = item_minimum_threshold_input.get()
                if minimum_threshold is not None and minimum_threshold.strip() == "":
                    minimum_threshold = None
                elif minimum_threshold and not validators.is_positive_int(
                    minimum_threshold
                ):
                    raise TypeError(
                        "Item minimum alert threshold must be a positive integer"
                    )

                expiration_date = item_expiration_input.get()
                if expiration_date is not None and expiration_date.strip() == "":
                    expiration_date = None
                elif expiration_date and not validators.is_valid_date(expiration_date):
                    raise ValueError("Expiration date must be in YYYY-MM-DD format")

                description = item_description_input.get()
                if description is not None and description.strip() == "":
                    description = None
                elif description and not validators.is_non_empty_string(description):
                    raise ValueError("Description must be non-empty string")

                inventory.add_inventory_item(
                    current_user,
                    item_name,
                    category,
                    description,
                    quantity,
                    expiration_date,
                    minimum_threshold,
                )

                self.refresh_inventory_list()
                self.show_item_details(item_name)
                self.refresh_item_details()

            except Exception as e:
                messagebox.showerror(
                    "Error", f"An error occurred while setting item category: {e}"
                )
                logger.error(f"An error occurred while setting item category: {e}")
            popup.destroy()

        submit_button = tk.Button(popup, text="Submit", command=submit)
        submit_button.pack(padx=20, pady=10)

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
            messagebox.showerror("Error", f"Error deleting item: {e}")
            logger.error(f"Error deleting item: {e}")

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
            messagebox.showerror("Error", f"Error increasing item: {e}")
            logger.error(f"Error increasing item: {e}")

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
            messagebox.showerror("Error", f"Error decreasing quantity: {e}")
            logger.error(f"Error decreasing quantity: {e}")

    def set_quantity(self):
        """Sets the quantity of the selected inventory item to a specific value."""

        current_user = self.controller.current_user
        try:
            quantity = simpledialog.askinteger("Input", "Change quantity to: ")

            if not validators.is_positive_int(quantity):
                raise TypeError("Quantity must be a positive integer")

            inventory.set_quantity(current_user, self.selected_item, quantity)

            self.refresh_inventory_list()
            self.refresh_item_details()
        except Exception as e:
            messagebox.showerror("Error", f"Error setting item quantity: {e}")
            logger.error(f"Error setting item quantity: {e}")

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
            messagebox.showerror("Error", f"Error setting item expiration date: {e}")
            logger.error(f"Error setting item expiration date: {e}")

    def set_description(self):
        """Updates the description for the selected inventory item."""

        current_user = self.controller.current_user
        try:
            description = simpledialog.askstring("Input", "New description: ")

            inventory.set_description(current_user, self.selected_item, description)

            self.refresh_inventory_list()
            self.refresh_item_details()
        except Exception as e:
            messagebox.showerror("Error", f"Error setting item description: {e}")
            logger.error(f"Error setting item description: {e}")

    def set_minimum_threshold(self):
        """Sets the minimum threshold for the selected inventory item."""

        current_user = self.controller.current_user
        try:
            quantity = simpledialog.askinteger(
                "Input", "Set minimum alert threshold to: "
            )

            if not validators.is_positive_int(quantity):
                raise TypeError("Quantity must be a positive integer")

            inventory.set_minimum_threshold(current_user, self.selected_item, quantity)

            self.refresh_inventory_list()
            self.refresh_item_details()
        except Exception as e:
            messagebox.showerror("Error", f"Error setting item minimum threshold: {e}")
            logger.error(f"Error setting item minimum threshold: {e}")

    def set_category(self):
        """Updates the category for the selected inventory item."""

        current_user = self.controller.current_user
        try:
            popup = tk.Toplevel(self)
            popup.title("Select Category")

            label = tk.Label(popup, text="Select new category:")
            label.pack(padx=20, pady=10)

            selected_category = tk.StringVar(popup)
            selected_category.set(VALID_CATEGORIES[0])

            dropdown = ttk.Combobox(
                popup,
                textvariable=selected_category,
                values=VALID_CATEGORIES,
                state="readonly",
            )
            dropdown.pack(padx=20, pady=10)
            dropdown.current(0)

            def submit():
                category = selected_category.get()
                try:
                    inventory.set_category(current_user, self.selected_item, category)

                    self.refresh_inventory_list()
                    self.refresh_item_details()
                except Exception as e:
                    messagebox.showerror("Error", f"Error setting item category: {e}")
                    logger.error(f"Error setting item category: {e}")
                popup.destroy()

            submit_button = tk.Button(popup, text="Submit", command=submit)
            submit_button.pack(padx=20, pady=10)

        except Exception as e:
            messagebox.showerror("Error", f"Error setting item category: {e}")
            logger.error(f"Error setting item category: {e}")
