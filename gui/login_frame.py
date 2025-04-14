import tkinter as tk
from tkinter import messagebox
import api.users as users
import logging

logger = logging.getLogger(__name__)


class LoginFrame(tk.Frame):
    """Frame for user login."""

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
        tk.Button(self, text="Close application", command=self.close_application).pack(
            pady=10
        )

    def close_application(self):
        if messagebox.askyesno("Close", "Do you really want to close the application?"):
            self.controller.destroy()

    def perform_login(self):
        """Attempts to login using the provided username and password."""

        username = self.username_entry.get()
        password = self.password_entry.get()

        try:
            current_user = users.login(username, password)

            if current_user:
                self.controller.current_user = current_user
                self.controller.show_frame("MainMenuFrame")
            else:
                messagebox.showerror("Login error", "Invalid username or password.")

        except Exception as e:
            messagebox.showerror("Error", f"Login error: {e}")
            logger.error(f"Login error: {e}")
