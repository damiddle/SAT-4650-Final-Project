import tkinter as tk
from tkinter import messagebox
import api.audit_log as audit_log


class MainMenuFrame(tk.Frame):
    """Frame for the main menu with navigation options."""

    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        tk.Label(self, text="Main Menu", font=("Arial", 18)).pack(pady=20)

        self.inventory_button = tk.Button(
            self,
            text="Inventory management",
            width=25,
            command=lambda: controller.show_frame("InventoryFrame"),
        )

        self.users_button = tk.Button(
            self,
            text="User management",
            width=25,
            command=lambda: controller.show_frame("UsersFrame"),
        )

        self.audit_button = tk.Button(
            self,
            text="Audit log",
            width=25,
            command=lambda: controller.show_frame("AuditFrame"),
        )

        self.alerts_button = tk.Button(
            self,
            text="Alerts",
            width=25,
            command=lambda: controller.show_frame("AlertFrame"),
        )

        self.account_button = tk.Button(
            self,
            text="Manage account",
            width=25,
            command=lambda: controller.show_frame("AccountFrame"),
        )

        self.logout_button = tk.Button(
            self, text="Logout", width=25, command=self.logout
        )

        self.inventory_button.pack(pady=10)
        self.users_button.pack(pady=10)
        self.audit_button.pack(pady=10)
        self.alerts_button.pack(pady=10)
        self.account_button.pack(pady=10)
        self.logout_button.pack(pady=10)

    def logout(self):
        """Logs out the current user and returns to the login frame."""

        audit_log.update_audit_log(
            self.controller.current_user,
            self.controller.current_user.username,
            "LOGOUT",
            "Logged out",
        )
        self.controller.current_user = None
        self.controller.show_frame("LoginFrame")

    def update_menu_visibility(self):
        """Update which buttons are shown based on the logged-in user's role."""
        role = self.controller.current_user.role

        if role == "Admin":
            pass

        elif role == "Leadership":
            self.users_button.pack_forget()
            self.audit_button.pack_forget()

        elif role == "General Responder":
            self.users_button.pack_forget()
            self.audit_button.pack_forget()
            self.alerts_button.pack_forget()

        elif role == "Community Member":
            self.users_button.pack_forget()
            self.audit_button.pack_forget()
            self.alerts_button.pack_forget()
            self.inventory_button.pack_forget()

        else:
            self.users_button.pack_forget()
            self.audit_button.pack_forget()
            self.alerts_button.pack_forget()
            self.inventory_button.pack_forget()
            self.account_button.pack_forget()

            messagebox.showerror("Something went wrong, user has no valid role")
            self.logout()

    def tkraise(self, aboveThis=None):
        """Override tkraise to update visibility each time this frame is shown."""
        super().tkraise(aboveThis)
        if self.controller.current_user:
            self.update_menu_visibility()
