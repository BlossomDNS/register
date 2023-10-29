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

        self.connection.execute("CREATE TABLE IF NOT EXISTS users (token TEXT, username TEXT, subdomains TEXT)")
        self.connection.commit()
        self.connection.close()
    
    def connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.dbfile)
    
    def close(self):
        self.connection.commit()
        self.connection.close()
        
    def use_database(self, query: str, values:tuple=None):
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
        domains = self.use_database("SELECT subdomains from users where token = ?", (session,))
        print(domains[0])
        if domains[0] is None:
            return []
        return json.loads(domains[0].replace("'", '"'))
    
    def get_from_token(self, need, session):
        out = self.use_database("SELECT "+need+" from users where token = ?", (session,))
        return out[0]
