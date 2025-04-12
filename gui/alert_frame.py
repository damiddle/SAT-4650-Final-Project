import tkinter as tk
from tkinter import scrolledtext
import api.alerts as alerts


class AlertFrame(tk.Frame):
    """Frame for displaying inventory alerts."""

    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        tk.Label(self, text="Alerts", font=("Arial", 18)).pack(pady=20)

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
            command=lambda: controller.show_frame("MainMenuFrame"),
        ).pack(pady=5)

    def view_expired_items(self):
        """Displays a list of expired inventory items."""

        self.alert_text.config(state=tk.NORMAL)
        self.alert_text.delete("1.0", tk.END)

        try:
            expired_inventory = alerts.search_for_expiration(
                self.controller.current_user
            )
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
            self.alert_text.insert(
                tk.END, f"An error occurred while retrieving expired inventory: {e}"
            )

    def view_low_inventory(self):
        """Displays inventory items with quantity below the threshold."""

        self.alert_text.config(state=tk.NORMAL)
        self.alert_text.delete("1.0", tk.END)

        try:
            low_inventory = alerts.search_for_low_quantity(self.controller.current_user)

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
            self.alert_text.insert(
                tk.END, f"An error occurred while retrieving low inventory: {e}"
            )
