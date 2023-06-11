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
        self.execute_query(create_users)
        
    def close_connection(self):
        self.connection.close()
        
    def create_connection(self, path):
        try:
            self.connection = sqlite3.connect(path)
            create_files_table = '''
                CREATE TABLE IF NOT EXISTS File (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT
                )
            '''
            self.execute_query(create_files_table)
            print("Connection to SQLiteDB successful")

        except Error as e:
            print("ERROR EN CREATE CONNECTION")
            print("PATH = ", path)
            print(f"The error '{e}' ocurred")
            
    def execute_read_query(self, query):
        print("SELF connection ", self.connection)
        print("QUERY ", query)
        cursor = self.connection.cursor()
        result = None
        try:
            cursor.execute(query)
            result = cursor.fetchall()
            return result
        except Error as e:
            print("ERROR EN EXECUTE READ QUERY")
            print(f"The error '{e}' occurred")

    def execute_query(self, query):
        print("ENtre aqui")
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            self.connection.commit()
            print("Query executed successfully")
        except Error as e:
            print("ERROR EN EXECUTE QUERY")
            print("The error '{e}' ocurred")

if __name__ == '__main__':
    path = './processes/databases/db_1.db'
    datab = DataB()
    datab.create_connection(path)
    datab.insert_file("Hakuna Matata")
    datab.insert_file("El viejo y el mar")
    query = "Hakuna Matata"
    select_files = f"SELECT name FROM File WHERE File.name = '{query}'"
    result = datab.execute_read_query(select_files)