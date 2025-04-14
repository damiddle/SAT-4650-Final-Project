"""
Module for the EMS Inventory Graphical User Interface (GUI).

Creates a Tkinter-based GUI application for managing inventory, users, audit logs,
alerts, and account settings. Each screen/frame in the application is represented by
a subclass of tk.Frame.
"""

from gui.app import App
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("ems_inventory.log", mode="a"),
    ],
)

if __name__ == "__main__":
    app = App()
    app.mainloop()
