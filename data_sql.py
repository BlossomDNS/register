import json
import sqlite3

"""
For Manipulatng the databasedb

SQL stuff

My java professor is cool

"""


class dataSQL:
    def __init__(self, dbfile):
        self.dbfile = dbfile
        self.connection = sqlite3.connect(self.dbfile)
        self.cursor = self.connection.cursor()

        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS users (token TEXT, username TEXT, max INTEGER DEFAULT 1)"
        )
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS subdomains (token TEXT, subdomain TEXT)"
        )
        self.connection.commit()
        self.connection.close()

    def connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.dbfile)

    def close(self):
        self.connection.commit()
        self.connection.close()

    def use_database(self, query: str, values: tuple = None):
        self.connection = self.connect()

        res = self.connection.execute(query, values)
        returned_value = None
        if "select" in query.lower():
            returned_value = res.fetchone()
        self.close()
        return returned_value

    def subdomains_from_token(self, session):
        """
        args:
            session -> user's session (session[id])

        output:
            if NONE then []
            otherwise get a list of subdomains owned by x user
        """
        self.connection = self.connect()
        self.cursor = self.connection.cursor()

        query = f"SELECT subdomain FROM subdomains WHERE token = '{session}'"
        print(query)
        self.cursor.execute(query)

        rows = self.cursor.fetchall()

        domain_list = [row[0] for row in rows]
        print(domain_list)

        self.cursor.close()
        self.connection.close()
        
        return domain_list

    def get_from_token(self, need, session):
        out = self.use_database(
            f"SELECT {need} from users where token = ?", (session,)
        )
        return out[0]
    
    def new_subdomain(self, token, subdomain) -> bool: #inserts new_subdomain
        if self.token_exists(token=token): #check if there is a user in the first place
            self.connection = self.connect()
            self.connection.execute("INSERT INTO subdomains (token, subdomain) VALUES (?, ?)", (token, subdomain))
            self.close()
            return True
        else:
            return False
        
    
    def token_exists(self, token) -> bool:
        self.connection = self.connect()
        self.cursor = self.connection.cursor()
        
        query = f"SELECT COUNT(*) FROM users WHERE token = '{token}'"
        self.cursor.execute(query)

        count = self.cursor.fetchone()[0]
        
        self.cursor.close()
        self.close()

        if count > 0:
            return True
        else:
            return False
    
    def delete(self, subdomain) -> bool:
        try:
            self.connection = self.connect()
            self.cursor = self.connection.cursor()
            self.cursor.execute(f"DELETE FROM subdomains WHERE subdomain = '{subdomain}'")
            self.cursor.close()
            self.close()
            
            return True
        except:
            return False