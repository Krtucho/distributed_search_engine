import sqlite3
from sqlite3 import Error

class DataB:
    def __init__(self):
        self.connection = None #create_connection("./processes/sm_app.sqlite")
        
    def insert_file(self, file_name):
        create_users = f"""INSERT INTO
        File(name)
        VALUES
        ('{file_name}');
        """        
        execute_query(self.connection, create_users)
        
    
    def create_connection(self, path):
        try:
            self.connection = sqlite3.connect(path)
            create_files_table = '''
                CREATE TABLE IF NOT EXISTS File (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT
                )
            '''
            execute_query(self.connection, create_files_table)
            print("Connection to SQLiteDB successful")

        except Error as e:
            print(f"The error '{e}' ocurred")
            
    def execute_read_query(self, query):
        cursor = self.connection.cursor()
        result = None
        try:
            cursor.execute(query)
            result = cursor.fetchall()
            return result
        except Error as e:
            print(f"The error '{e}' occurred")
 

def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLiteDB successful")
    except Error as e:
        print(f"The error '{e}' ocurred")
        
    return connection

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print("The error '{e}' ocurred")



if __name__ == '__main__':
    path = './processes/db_1.db'
    datab = DataB()
    datab.create_connection(path)
    datab.insert_file("Hakuna Matata")
    datab.insert_file("El viejo y el mar")
    query = "Hakuna Matata"
    select_files = f"SELECT name FROM File WHERE File.name = '{query}'"
    result = datab.execute_read_query(select_files)