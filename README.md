# EMS Inventory Management System

The EMS Inventory Management System is a Python-based application that provides a robust graphical user interface (GUI) for managing critical aspects of an EMS environment. Built on Tkinter, this system facilitates user authentication, inventory management, user administration, audit logging, and alert notifications—all backed by a MySQL database and enhanced with data encryption and role-based access control.

## Features

- **User Authentication & Account Management**\
  Secure login, password encryption, and account update functionalities ensure that users access the system safely.

- **Inventory Management**\
  Add, update, or delete inventory items with support for item details such as quantity, expiration date, description, and category management. Alerts are automatically generated for expired items or low-stock conditions.

- **User Management**\
  Administrative features allow for adding new users, changing user roles, updating account details, and deleting users. All actions are logged in the audit log.

- **Audit Logging**\
  Comprehensive audit logging tracks key operations like login, updates, deletions, and unauthorized access attempts, ensuring traceability of user activity.

- **Alert Notifications**\
  Receive notifications on inventory irregularities.

- **Data Security & Encryption**\
  Sensitive data, such as user passwords, are encrypted using Fernet symmetric encryption to ensure data integrity and confidentiality.

- **Role-Based Access Control**\
  Functions are decorated with role-based permissions, ensuring that only authorized roles (e.g., Admin, Leadership) can execute specific operations.

- **Full-Featured Tkinter GUI**\
  Multiple screen frames handle distinct tasks (login, inventory, users, audit logs, alerts, account management), with a responsive design that supports scrollable content and dynamic updates.

## Technologies Used

- **Python 3**\
  The core programming language for application logic.
- **Tkinter**\
  Used to build a dynamic and user-friendly graphical user interface.
- **MySQL**\
  Handles data persistence and is managed through the `mysql.connector` package.
- **cryptography (Fernet)**\
  Provides robust data encryption mechanisms.
- **python-dotenv**\
  Manages configuration settings stored in a `.env` file.

## Configure the Environment

Edit the `.env` file with your specific settings (e.g., MySQL credentials, encryption keys, valid roles). An example configuration:

```plaintext
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "mysqlpass"
DB_NAME = "ems_inventory"
CONNECTION_POOL_SIZE = 5

VALID_USER_ROLES = ["Admin", "Leadership", "General Responder", "Community Member"]
VALID_CATEGORIES = ["Airway", "Ventilation", "Medications", "Trauma", "Vitals", "PPE", "Extrication", "Administrative", "Maintenance", "Miscellaneous"]

ACTIVE_ENCRYPTION_KEY = 'SgUNsA_7OCxc_DGUbRny2G6iP2oIhQjqFmMhAer1IfU='
OLD_ENCRYPTION_KEY = '2MtGIrXxI1D4AUQG465_U52GNbUFLBfM__nAKgZzhE4='
```

## Configuration Details

- **Database Settings:** Connection details and pool size for MySQL.
- **User Roles & Categories:** Defined roles (e.g., Admin, Leadership) and inventory categories.
- **Encryption Keys:** Active and old keys used by the encryption module.

## Project Structure

```plaintext
├── .env                     # Environment configuration (database, roles, encryption)
├── main.py                  # Application entry point for launching the Tkinter GUI
├── api/			# Main modules handling database operations
│   ├── users.py             	# User management (authentication, CRUD operations)
│   ├── alerts.py            	# Functionality for checking expired and low inventory items
│   ├── audit_log.py         	# Audit logging for system actions and procedures
│   └── inventory.py         	# Business logic for inventory operations (add/update/delete items)
├── gui/                     # GUI modules built with Tkinter
│   ├── app.py               	# Main GUI application class that orchestrates screen navigation
│   ├── login_frame.py       	# Login screen for user authentication
│   ├── main_menuframe.py   	# Primary navigation hub for the application
│   ├── inventory_frame.py   	# Inventory management screen with item details and actions
│   ├── users_frame._py       # Screen for managing user accounts
│   ├── audit_frame.py       	# View and export audit logs
│   ├── alert_frame.py       	# Displays inventory alerts for expired or low-stock items
│   ├── account_frame.py     	# Allows users to update account settings like username, password, and email 
│   └── scrollable_frame.py  	# Utility for creating scrollable areas within the GUI
└── utils/                   # Utility modules for common functionality
    ├── encryption.py        	# Data encryption utilities (shared with root encryption module)
    ├── validators.py        	# Common input validation functions
    ├── db_connection.py     	# Manages MySQL connections and database initialization
    └── decorators.py        	# Role-based access control implementations
```

## Usage Guide

- **Login**\
  Launch the application and log in using your credentials. A default admin user is created on first run (username: `admin`, password: `pass`).
- **Navigation**\
  Once logged in, the main menu provides access to:
  - **Inventory Management:** Manage inventory items including adding, updating, and deleting records.

  - **User Management:** Admins can manage user accounts.

  - **Audit Logs:** View the history of critical operations.

  - **Alerts:** Monitor expired items and low-stock warnings.

  - **Account Settings:** Update your username, password, and email address.
- **Inventory Operations**\
  Use the Inventory screen to filter items, view details, adjust quantities, change descriptions, set expiration dates, and categorize items.
- **User Administration & Audit Logs**\
  Only users with admin privileges can access full user management features and view audit logs that capture detailed records of system operations.
