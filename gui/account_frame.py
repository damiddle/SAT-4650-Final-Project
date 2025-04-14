import tkinter as tk
from tkinter import messagebox, simpledialog, scrolledtext
import api.users as users
import utils.validators as validators
import logging

logger = logging.getLogger(__name__)


class AccountFrame(tk.Frame):
    """Frame for managing the current user's account (username, password, email)."""

    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        tk.Label(self, text="Manage Account", font=("Arial", 18)).pack(pady=20)

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
            command=lambda: controller.show_frame("MainMenuFrame"),
        ).pack(pady=5)

    def change_username(self):
        """Prompts the user to change their username after verifying their password."""

        self.account_text.config(state=tk.NORMAL)
        self.account_text.delete("1.0", tk.END)
        current_user = self.controller.current_user

        try:
            current_password = simpledialog.askstring(
                "Input", "Verify your current password: ", show="*"
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

                    current_user.username = new_username
                else:
                    self.account_text.insert(tk.END, "Usernames did not match.")
            else:
                self.account_text.insert(tk.END, "Password was not valid.")
        except Exception as e:
            messagebox.showerror("Error", f"Error changing username: {e}")
            logger.error(f"Error changing username: {e}")

    def change_password(self):
        """Prompts the user to change their password after verifying their current password."""

        self.account_text.config(state=tk.NORMAL)
        self.account_text.delete("1.0", tk.END)
        current_user = self.controller.current_user

        try:
            current_password = simpledialog.askstring(
                "Input", "Verify your current password: ", show="*"
            )
            login_check = users.login(current_user.username, current_password)

            if (login_check is not None) and (login_check is not False):
                new_password = simpledialog.askstring(
                    "Input", "Please enter your new password: ", show="*"
                )
                if not validators.is_non_empty_string(new_password):
                    raise TypeError("New password must be non-empty string.")

                reentered = simpledialog.askstring(
                    "Input", "Reenter your new password: ", show="*"
                )
                if reentered == new_password:
                    users.change_user_password(current_user, new_password)
                else:
                    self.account_text.insert(tk.END, "Passwords did not match.")
            else:
                self.account_text.insert(tk.END, "Password was not valid.")
        except Exception as e:
            messagebox.showerror("Error", f"Error changing password: {e}")
            logger.error(f"Error changing password: {e}")

    def change_email(self):
        """Prompts the user to change their email after verifying their password."""

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

                    current_user.email = new_email
                else:
                    self.account_text.insert(tk.END, "Emails did not match.")
            else:
                self.account_text.insert(tk.END, "Email was not valid.")
        except Exception as e:
            messagebox.showerror("Error", f"Error changing email: {e}")
            logger.error(f"Error changing email: {e}")
