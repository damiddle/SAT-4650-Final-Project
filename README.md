EMS Inventory Management System
The EMS Inventory Management System is a Python-based application that provides a robust graphical user interface (GUI) for managing critical aspects of an EMS environment. Built on Tkinter, this system facilitates user authentication, inventory management, user administration, audit logging, and alert notifications—all backed by a MySQL database and enhanced with data encryption and role-based access control.

Features
User Authentication & Account Management
Secure login, password encryption, and account update functionalities ensure that users access the system safely.

Inventory Management
Add, update, or delete inventory items with support for item details such as quantity, expiration date, description, and category management. Alerts are automatically generated for expired items or low-stock conditions.

User Management
Administrative features allow for adding new users, changing user roles, updating account details, and deleting users. All actions are logged in the audit log.

Audit Logging
Comprehensive audit logging tracks key operations like login, updates, deletions, and unauthorized access attempts, ensuring traceability of user activity.

Alert Notifications & Email Integration
Receive notifications on inventory irregularities and send email notifications using SMTP settings defined in the configuration.

Data Security & Encryption
Sensitive data, such as user passwords, are encrypted using Fernet symmetric encryption to ensure data integrity and confidentiality.

Role-Based Access Control
Functions are decorated with role-based permissions, ensuring that only authorized roles (e.g., Admin, Leadership) can execute specific operations.

Full-Featured Tkinter GUI
Multiple screen frames handle distinct tasks (login, inventory, users, audit logs, alerts, account management), with a responsive design that supports scrollable content and dynamic updates.

Technologies Used
Python 3
The core programming language for application logic.

Tkinter
Used to build a dynamic and user-friendly graphical user interface.

MySQL
Handles data persistence and is managed through the mysql.connector package.

cryptography (Fernet)
Provides robust data encryption mechanisms.

smtplib & EmailMessage
For sending email notifications from the application.

python-dotenv
Manages configuration settings stored in a .env file.

Configuration Details
All configurations are defined in the .env file, including:

Database Settings:
Connection details and pool size for MySQL.

User Roles & Categories:
Defined roles (e.g., Admin, Leadership) and inventory categories.

Encryption Keys:
Active and old keys used by the encryption module.

Email Server Settings:
SMTP server details and security settings.

Project Structure
├── .env                      # Environment configuration (database, roles, encryption, SMTP) :contentReference[oaicite:11]{index=11}
├── main.py                   # Application entry point for launching the Tkinter GUI :contentReference[oaicite:12]{index=12}
├── db_connection.py          # Manages MySQL connections and database initialization :contentReference[oaicite:13]{index=13}
├── users.py                  # User management (authentication, CRUD operations) :contentReference[oaicite:14]{index=14}
├── alerts.py                 # Functionality for checking expired and low inventory items :contentReference[oaicite:15]{index=15}
├── audit_log.py              # Audit logging for system actions and procedures :contentReference[oaicite:16]{index=16}
├── inventory.py              # Business logic for inventory operations (add/update/delete items) :contentReference[oaicite:17]{index=17}
├── email_notifications.py    # Email integration for sending notifications :contentReference[oaicite:18]{index=18}
├── decorators.py             # Role-based access control decorators :contentReference[oaicite:19]{index=19}
├── encryption.py             # Encryption and decryption using Fernet :contentReference[oaicite:20]{index=20}
├── validators.py             # Input validation functions :contentReference[oaicite:21]{index=21}
├── gui/                     # GUI modules built with Tkinter
│   ├── app.py               # Main GUI application class that orchestrates screen navigation :contentReference[oaicite:22]{index=22}
│   ├── login_frame.py       # Login screen for user authentication :contentReference[oaicite:23]{index=23}
│   ├── main_menu_frame.py   # Primary navigation hub for the application
│   ├── inventory_frame.py   # Inventory management screen with item details and actions :contentReference[oaicite:24]{index=24}
│   ├── users_frame.py       # Screen for managing user accounts :contentReference[oaicite:25]{index=25}
│   ├── audit_frame.py       # View and export audit logs :contentReference[oaicite:26]{index=26}
│   ├── alert_frame.py       # Displays inventory alerts for expired or low-stock items :contentReference[oaicite:27]{index=27}
│   ├── account_frame.py     # Allows users to update account settings like username, password, and email :contentReference[oaicite:28]{index=28}
│   └── scrollable_frame.py  # Utility for creating scrollable areas within the GUI :contentReference[oaicite:29]{index=29}
└── utils/                   # Utility modules for common functionality
    ├── encryption.py        # Data encryption utilities (shared with root encryption module) :contentReference[oaicite:30]{index=30}
    ├── validators.py        # Common input validation functions :contentReference[oaicite:31]{index=31}
    └── decorators.py        # Role-based access control implementations :contentReference[oaicite:32]{index=32}

Usage Guide
Login
Launch the application and log in using your credentials. A default admin user is created on first run (username: admin, password: pass).

Navigation
Once logged in, the main menu provides access to:

Inventory Management: Manage inventory items including adding, updating, and deleting records.

User Management: Admins can manage user accounts.

Audit Logs: View the history of critical operations.

Alerts: Monitor expired items and low-stock warnings.

Account Settings: Update your username, password, and email address.

Inventory Operations
Use the Inventory screen to filter items, view details, adjust quantities, change descriptions, set expiration dates, and categorize items.

User Administration & Audit Logs
Only users with admin privileges can access full user management features and view audit logs that capture detailed records of system operations.

Email Notifications
Email notifications are sent based on the configured SMTP details in the .env file.