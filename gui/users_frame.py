import tkinter as tk
from tkinter import messagebox, simpledialog
import api.users as users
import utils.validators as validators
from gui.scrollable_frame import ScrollableFrame


class UsersFrame(tk.Frame):
    """Frame for managing users."""

    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.selected_user = None
        self.all_users = []
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
        self.search_var.trace("w", lambda *args: self.filter_users())
        search_entry = tk.Entry(self.left_frame, textvariable=self.search_var)
        search_entry.pack(fill="x", padx=2, pady=2)

        self.left_bottom_frame = tk.Frame(self)
        self.left_bottom_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        self.add_user_button = tk.Button(
            self.left_bottom_frame, text="Add user", command=self.add_user
        )

        self.return_button = tk.Button(
            self.left_bottom_frame,
            text="Return to menu",
            command=lambda: controller.show_frame("MainMenuFrame"),
        )

        self.right_top_frame = tk.Frame(self)
        self.right_top_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.user_details_text = tk.Text(
            self.right_top_frame, wrap=tk.WORD, state="disabled"
        )
        self.user_details_text.pack(fill="both", expand=True)

        self.right_bottom_frame = tk.Frame(self)
        self.right_bottom_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

        self.change_user_role_button = tk.Button(
            self.right_bottom_frame,
            text="Change role",
            command=self.change_user_role,
        )

        self.delete_user_button = tk.Button(
            self.right_bottom_frame,
            text="Delete user",
            command=self.delete_user,
        )

        self.refresh_details_button = tk.Button(
            self.right_bottom_frame,
            text="Refresh details",
            command=self.refresh_user_details,
        )

        self.add_user_button.pack(side="left", padx=5, pady=5)
        self.return_button.pack(side="left", padx=5, pady=5)
        self.change_user_role_button.pack(side="left", padx=5, pady=5)
        self.delete_user_button.pack(side="left", padx=5, pady=5)
        self.refresh_details_button.pack(side="left", padx=5, pady=5)

        self.selected_user = None

    def tkraise(self, aboveThis=None):
        """Overrides tkraise to refresh the user list when the frame is raised and filter user options."""

        super().tkraise(aboveThis)
        self.refresh_user_list()
        self.update_menu_visibility()

    def update_menu_visibility(self):
        """Update which buttons are shown based on the logged-in user's role."""
        role = self.controller.current_user.role

        if role == "Admin":
            pass

        elif role in ["Leadership", "General Responder", "Community Member"]:
            self.add_user_button.pack_forget()
            self.delete_user_button.pack_forget()
            self.change_user_role_button.pack_forget()

        else:
            self.add_user_button.pack_forget()
            self.delete_user_button.pack_forget()
            self.change_user_role_button.pack_forget()
            self.refresh_details_button.pack_forget()
            self.return_button.pack_forget()

            messagebox.showerror("Something went wrong, user has no valid role")
            self.controller.show_frame("MainMenuFrame")

    def refresh_user_list(self):
        """Fetches and displays the list of users."""

        current_user = self.controller.current_user
        try:
            users_stored = users.show_all_users(current_user)
            self.all_users = users_stored if users_stored else []

            self.populate_user_buttons(self.all_users)
        except Exception as e:
            messagebox.showerror("Users error", str(e))

    def filter_users(self):
        """Filters displayed users based on the search query."""

        query = self.search_var.get().lower()
        filtered_users = [user for user in self.all_users if query in user[0].lower()]

        self.populate_user_buttons(filtered_users)

    def populate_user_buttons(self, users):
        """Creates buttons for each user in the scrollable frame.

        Args:
            users (list): A list of user records.
        """

        for widget in self.scrollable_frame.scrollable_frame.winfo_children():
            widget.destroy()

        if users:
            for user in users:
                username = user[1]
                btn = tk.Button(
                    self.scrollable_frame.scrollable_frame,
                    text=username,
                    command=lambda name=username: self.show_user_details(name),
                )
                btn.pack(fill="x", padx=2, pady=2)
        else:
            tk.Label(
                self.scrollable_frame.scrollable_frame, text="No users found."
            ).pack()

    def refresh_user_details(self):
        """Refreshes the details for the currently selected user."""

        if self.selected_user:
            self.show_user_details(self.selected_user)
        else:
            messagebox.showerror("Error", "No user selected.")

    def show_user_details(self, username):
        """Displays detailed information for a selected user.

        Args:
            username (str): The username whose details to display.
        """

        self.selected_user = username
        current_user = self.controller.current_user
        try:
            user_data = users.view_user(current_user, username)
            self.user_details_text.config(state="normal")
            self.user_details_text.delete("1.0", tk.END)

            if user_data and len(user_data) > 0:
                user = user_data[0]
                details = (
                    f"Username: {user[1]}\n"
                    f"User ID: {user[0]}\n"
                    f"Role: {user[2]}\n"
                    f"Email: {user[3]}\n"
                    f"Registered: {user[4]}\n"
                    f"Last updated: {user[5]}"
                )

                self.user_details_text.insert(tk.END, details)
            else:
                self.user_details_text.insert(tk.END, "No details available.")
            self.user_details_text.config(state="disabled")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_all_users(self):
        """Displays all users' details in the text area."""

        self.user_details_text.config(state=tk.NORMAL)
        self.user_details_text.delete("1.0", tk.END)
        current_user = self.controller.current_user

        if current_user:
            try:
                users_list = users.show_all_users(current_user)
                if users_list:
                    for user in users_list:
                        user_str = (
                            f"Username: {user[1]}\n"
                            f"User ID: {user[0]}\n"
                            f"Role: {user[2]}\n"
                            f"Email: {user[3]}\n"
                            f"Created: {user[4]}\n"
                            f"Updated: {user[5]}\n"
                            "----------------------------------------\n"
                        )

                        self.user_details_text.insert(tk.END, user_str)
                else:
                    self.user_details_text.insert(tk.END, "No users found.")
            except Exception as e:
                messagebox.showerror(
                    "An error occurred while retrieving all users: ", str(e)
                )
        else:
            messagebox.showerror("Error", "No current user. Please login again.")

    def change_user_role(self):
        """Prompts to change the role of the selected user and updates it."""

        self.user_details_text.config(state=tk.NORMAL)
        self.user_details_text.delete("1.0", tk.END)
        current_user = self.controller.current_user

        if current_user:
            try:
                username = self.selected_user

                if not validators.is_non_empty_string(username):
                    raise ValueError("Username must be a non-empty string.")

                new_role = simpledialog.askstring("Input", "Enter new role: ")

                if not validators.is_valid_role(new_role):
                    raise ValueError("Invalid role.")

                users.change_user_role(current_user, username, new_role)

                self.refresh_user_details()
            except Exception as e:
                messagebox.showerror(
                    "An error occurred while updated user role: ", str(e)
                )
        else:
            messagebox.showerror("Error", "No current user. Please login again.")

    def delete_user(self):
        """Deletes the selected user from the system."""

        self.user_details_text.config(state=tk.NORMAL)
        self.user_details_text.delete("1.0", tk.END)
        current_user = self.controller.current_user

        if current_user:
            try:
                username = self.selected_user

                if not validators.is_non_empty_string(username):
                    raise ValueError("Username must be a non-empty string.")

                users.delete_user(current_user, username)

                self.refresh_user_list()
            except Exception as e:
                messagebox.showerror("User error", str(e))
        else:
            messagebox.showerror("Error", "No current user. Please login again.")

    def add_user(self):
        """Prompts for input and adds a new user."""

        self.user_details_text.config(state=tk.NORMAL)
        self.user_details_text.delete("1.0", tk.END)
        current_user = self.controller.current_user

        if current_user:
            try:
                username = simpledialog.askstring("Input", "Username: ")
                if not validators.is_non_empty_string(username):
                    raise ValueError("Username must be a non-empty string.")

                password = simpledialog.askstring("Input", "Password: ", show="*")
                if not validators.is_non_empty_string(password):
                    raise ValueError("Password must be a non-empty string.")

                role = simpledialog.askstring("Input", "User role: ")
                if not validators.is_valid_role(role):
                    raise ValueError("Invalid role.")

                email = simpledialog.askstring("Input", "User email: ")
                if not validators.is_valid_email(email):
                    raise ValueError("Email must be in valid format.")

                users.add_user(current_user, username, password, role, email)

                self.refresh_user_list()
            except Exception as e:
                messagebox.showerror("An error occurred while adding user: ", str(e))
        else:
            messagebox.showerror("Error", "No current user. Please login again.")
