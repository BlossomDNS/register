import sqlite3

"""
For Manipulatng the databasedb

SQL stuff

My java professor is cool

"""

class dataSQL:
    def __init__(self, dbfile):
        self.dbfile = dbfile
        self.connection = sqlite3.connect("database.db")

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
        self.connection.close()
        return returned_value