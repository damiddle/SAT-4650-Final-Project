import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog
import api.audit_log as audit_log
import utils.validators as validators
import logging

logger = logging.getLogger(__name__)


class AuditFrame(tk.Frame):
    """Frame for viewing and exporting audit logs."""

    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        tk.Label(self, text="Audit Log", font=("Arial", 18)).pack(pady=20)

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
            command=lambda: controller.show_frame("MainMenuFrame"),
        ).pack(pady=5)

    def view_recent_logs(self):
        """Retrieves and displays a specified number of recent audit logs."""

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
                messagebox.showerror("Error", f"Error retrieving audit logs: {e}")
                logger.error(f"Error retrieving audit logs: {e}")
        else:
            messagebox.showerror("Error", "No current user. Please login again.")
            logger.error("No logged in user specified")

    def export_logs_to_text(self):
        """Exports the audit log to a text file and notifies the user."""

        self.audit_text.config(state=tk.NORMAL)
        self.audit_text.delete("1.0", tk.END)
        current_user = self.controller.current_user

        try:
            audit_log.export_to_txt(current_user)

            self.audit_text.insert(
                tk.END, "Audit log has been exported as a .txt file."
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting the audit log: {e}")
            logger.error(f"Error exporting the audit log: {e}")
