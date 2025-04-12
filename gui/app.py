import tkinter as tk
from gui.login_frame import LoginFrame
from gui.main_menu_frame import MainMenuFrame
from gui.inventory_frame import InventoryFrame
from gui.users_frame import UsersFrame
from gui.audit_frame import AuditFrame
from gui.alert_frame import AlertFrame
from gui.account_frame import AccountFrame


class App(tk.Tk):
    """Main application class for the EMS Inventory GUI."""

    def __init__(self):
        super().__init__()
        self.title("EMS Inventory GUI")
        self.geometry("1000x600")
        self.attributes("-fullscreen", True)
        self.bind("<Escape>", lambda event: self.attributes("-fullscreen", False))
        self.current_user = None

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Dictionary for frame instances, keyed by a string identifier.
        self.frames = {}
        frame_classes = {
            "LoginFrame": LoginFrame,
            "MainMenuFrame": MainMenuFrame,
            "InventoryFrame": InventoryFrame,
            "UsersFrame": UsersFrame,
            "AuditFrame": AuditFrame,
            "AlertFrame": AlertFrame,
            "AccountFrame": AccountFrame,
        }
        for name, FrameClass in frame_classes.items():
            frame = FrameClass(container, self)
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginFrame")

    def show_frame(self, frame_name):
        """Raises the specified frame to the top for display."""
        frame = self.frames.get(frame_name)
        if frame:
            frame.tkraise()
