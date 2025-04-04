Table audit_log in database ems_inventory
+------------------+----------------------------------------------------------+------+-----+-------------------+-------------------+
| Field            | Type                                                     | Null | Key | Default           | Extra             |
+------------------+----------------------------------------------------------+------+-----+-------------------+-------------------+
| log_id           | int                                                      | NO   | PRI | NULL              | auto_increment    |
| username         | varchar(50)                                              | YES  |     | NULL              |                   |
| updated_object   | varchar(100)                                             | YES  |     | NULL              |                   |
| action_type      | enum('ADD','UPDATE','DELETE','LOGIN','LOGOUT', 'ACCESS') | NO   |     | NULL              |                   |
| action_timestamp | timestamp                                                | YES  |     | CURRENT_TIMESTAMP | DEFAULT_GENERATED |
| details          | text                                                     | YES  |     | NULL              |                   |
+------------------+----------------------------------------------------------+------+-----+-------------------+-------------------+

Table inventory in database ems_inventory
+-----------------+--------------+------+-----+-------------------+-----------------------------------------------+
| Field           | Type         | Null | Key | Default           | Extra                                         |
+-----------------+--------------+------+-----+-------------------+-----------------------------------------------+
| item_id         | int          | NO   | PRI | NULL              | auto_increment                                |
| item_name       | varchar(100) | NO   | MUL | NULL              |                                               |
| category        | varchar(50)  | NO   |     | NULL              |                                               |
| description     | text         | YES  |     | NULL              |                                               |
| quantity        | int          | NO   |     | NULL              |                                               |
| expiration_date | date         | YES  |     | NULL              |                                               |
| min_threshold   | int          | YES  |     | 1                 |                                               |
| last_updated    | timestamp    | YES  |     | CURRENT_TIMESTAMP | DEFAULT_GENERATED on update CURRENT_TIMESTAMP |
+-----------------+--------------+------+-----+-------------------+-----------------------------------------------+

Table users in database ems_inventory
+--------------------+-------------------------------+------+-----+------------------ +-----------------------------------------------+
| Field              | Type                          | Null | Key | Default           | Extra                                         |
+--------------------+-------------------------------+------+-----+-------------------+-----------------------------------------------+
| user_id            | int                           | NO   | PRI | NULL              | auto_increment                                |
| username           | varchar(50)                   | NO   | UNI | NULL              |                                               |
| password_encrypted | varchar(255)                  | NO   |     | NULL              |                                               |
| role               | enum('Admin','User','Viewer') | YES  |     | Viewer            |                                               |
| email              | varchar(100)                  | NO   | UNI | NULL              |                                               |
| created_at         | timestamp                     | YES  |     | CURRENT_TIMESTAMP | DEFAULT_GENERATED                             |
| updated_at         | timestamp                     | YES  |     | CURRENT_TIMESTAMP | DEFAULT_GENERATED on update CURRENT_TIMESTAMP |
+--------------------+-------------------------------+------+-----+-------------------+-----------------------------------------------+