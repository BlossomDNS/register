import json
import sqlite3

"""
For Manipulatng the databasedb

SQL stuff

My java professor is cool

"""


class dataSQL:
    def __init__(self, dbfile):
        """
        Initialize a DatabaseManager with the specified SQLite database file.

        Parameters:
        - dbfile (str): The path to the SQLite database file.
        """
        self.dbfile = dbfile
        self.connection = sqlite3.connect(self.dbfile)
        self.cursor = self.connection.cursor()

        self.create_tables()

    def create_tables(self):
        self.cursor.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token TEXT UNIQUE,
                username TEXT,
                email TEXT,
                password TEXT
            );

            CREATE TABLE IF NOT EXISTS subdomains (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token TEXT,
                subdomain TEXT,
                FOREIGN KEY (token) REFERENCES users(token) ON DELETE CASCADE
            );
        ''')

    def connect(self) -> sqlite3.Connection:
        """
        Establish a connection to the SQLite database.

        Returns:
        - sqlite3.Connection: A database connection object.
        """
        return sqlite3.connect(self.dbfile)

    def close(self):
        """
        Commit any pending changes and close the database connection.
        """
        self.connection.commit()
        self.connection.close()

    def use_database(self, query: str, values: tuple = None):
        """
        Execute a database query and return the result.

        Parameters:
        - query (str): The SQL query to execute.
        - values (tuple, optional): A tuple of parameter values to bind to the query.

        Returns:
        - result: The result of the query execution. If it's a SELECT query, it returns the first row as a tuple; otherwise, it returns None.
        """
        self.connection = self.connect()

        res = self.connection.execute(query, values)
        returned_value = None
        if "select" in query.lower():
            returned_value = res.fetchone()
        self.close()
        return returned_value

    def subdomains_from_token(self, session):
        """
        Retrieve a list of subdomains owned by a user with a specific session token.

        Parameters:
        - session: User's session token.

        Returns:
        - domain_list: A list of subdomains owned by the user or an empty list if none are found.
        """
        self.connection = self.connect()
        self.cursor = self.connection.cursor()

        query = f"SELECT subdomain FROM subdomains WHERE token = ?"
        print(query)
        self.cursor.execute(query, (session, ))

        rows = self.cursor.fetchall()

        domain_list = [row[0] for row in rows]
        print(domain_list)

        self.cursor.close()
        self.connection.close()
        
        return domain_list

    def get_from_token(self, need, session):
        """
        Retrieve a specific field (e.g., user information) from the 'users' table based on a session token.

        Parameters:
        - need (str): The field to retrieve (e.g., 'username', 'email').
        - session: User's session token.

        Returns:
        - value: The value of the requested field or None if not found.
        """
        out = self.use_database(
            f"SELECT {need} from users where token = ?", (session,)
        )
        return out[0]
    
    def new_subdomain(self, token, subdomain) -> bool: #inserts new_subdomain
        """
        Insert a new subdomain for a user.

        Parameters:
        - token: User's session token.
        - subdomain: The subdomain to be inserted.

        Returns:
        - success: True if the insertion is successful, False otherwise.
        """
        if self.token_exists(token=token): #check if there is a user in the first place
            self.connection = self.connect()
            self.connection.execute("INSERT INTO subdomains (token, subdomain) VALUES (?, ?)", (token, subdomain))
            self.close()
            return True
        else:
            return False
        
    
    def token_exists(self, token) -> bool:
        """
        Check if a user with the specified session token exists in the 'users' table.

        Parameters:
        - token: User's session token to check.

        Returns:
        - exists: True if the user exists, False otherwise.
        """
        self.connection = self.connect()
        self.cursor = self.connection.cursor()
        
        query = "SELECT COUNT(*) FROM users WHERE token = ?"
        self.cursor.execute(query, (token, ))

        count = self.cursor.fetchone()[0]
        
        self.cursor.close()
        self.close()

        if count > 0:
            return True
        else:
            return False
    
    def delete(self, subdomain) -> bool:
        """
        Delete a subdomain from the 'subdomains' table.

        Parameters:
        - subdomain: The subdomain to be deleted.

        Returns:
        - success: True if the deletion is successful, False otherwise.
        """
        try:
            self.connection = self.connect()
            self.cursor = self.connection.cursor()
            self.cursor.execute(f"DELETE FROM subdomains WHERE subdomain = '{subdomain}'")
            self.cursor.close()
            self.close()
            
            return True
        except:
            return False
    
    def owner_of_subdmain(self, subdomain) -> int:
        """
        Retrieve the session token (owner) of a specific subdomain.

        Parameters:
        - subdomain: The subdomain to query ownership for.

        Returns:
        - owner_token: The session token (as an integer) of the owner of the subdomain.
        """
        self.connection = self.connect()
        self.cursor = self.connection.cursor()
        self.cursor.execute(f'SELECT Token FROM subdomains WHERE subdomain = "{subdomain}";')
        token = self.cursor.fetchone()[0]
        self.cursor.close()
        self.close()
        return token
    
    def admin_fetchall(self) -> list:
        output = []
        self.connection = self.connect()
        self.cursor = self.connection.cursor()
        self.cursor.execute('SELECT * FROM subdomains;')
        subdomains = self.cursor.fetchall()

        for subdomain in subdomains:
            user = self.cursor.execute(f'SELECT username FROM users WHERE token = {subdomain[0]};').fetchone()[0]
            output.append(SQLRelationship(owner=user, subdomain=subdomain[1]))

        self.cursor.close()
        self.close()

        return output

class SQLRelationship:
    def __init__(self, owner, subdomain):
        self.owner = owner
        self.subdomain = subdomain
