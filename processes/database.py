import sqlite3
from sqlite3 import Error
from parser_cran import get_data_from
import re

class Text:
    def __init__(self, id, title, author, body):
        self.id = id
        self.title = title
        self.author = author
        self.body = body

class DataB:
    def __init__(self):
        self.connection = None #create_connection("./processes/sm_app.sqlite")
        
    def insert_file(self, text_file: Text):     
        create_users = """INSERT INTO
        File(Title, Author, Body)
        VALUES
        (?, ?, ?);
        """
        self.execute_query(create_users, text_file)
        
    def close_connection(self):
        self.connection.close()
        
    def create_connection(self, path):
        try:
            self.connection = sqlite3.connect(path)
            create_files_table = '''
                CREATE TABLE IF NOT EXISTS File (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Title TEXT NOT NULL UNIQUE,
                    Author TEXT,
                    Body TEXT NOT NULL
                )
            '''
            self.execute_query(create_files_table, "")
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

    def execute_query(self, query, text_file):
        print("ENtre aqui")
        cursor = self.connection.cursor()
        try:
            if text_file != "":
                cursor.execute(query, (text_file.title, text_file.author, text_file.body))
            else: 
                cursor.execute(query)
            self.connection.commit()
            print("Query executed successfully")
        except Error as e:
            print("ERROR EN EXECUTE QUERY")
            print(f"The error '{e}' ocurred")

#Este metodo se llama inicialmente al levantar los servidores y asignar a cada uno su BD.
# Aqui se toman los archivos .txt y se devuelven como objetos de la clase Text
def convert_text_to_text_class(path, files_name: list):
    text_list = []
    
    for file in files_name:
        with open(f"{path}/{file}", 'r') as file:
            data = file.read()
        id = re.search(r'ID: (\d+)', data)
        title = re.search(r'Title: ([\s\S]*?)\nAuthor: ', data, re.DOTALL)
        author = re.search(r'Author: ([\s\S]*?)\nBody:', data, re.DOTALL )
        body = re.search(r'Body:\n(.+)', data, re.DOTALL)
        if id and title and author and body:
            id_text = id.group(1).strip()
            #title_text = title.group(1).strip()
            title_ = title.group(1)
            title_text = title_.replace('\n', ' ')
            author_text = author.group(1).strip()
            #body_text = body.group(1).strip()
            body_ = body.group(1)
            body_text = body_.replace('\n', ' ')
            text = Text(id_text, title_text, author_text, body_text)
            text_list.append(text)
    return text_list

if __name__ == '__main__':
    path = './processes/databases/db3.db'
    path_txts = '/home/roxy/Roxana-linux/SD/distributed_search_engine/processes/txts'
    files_name = ['document_1.txt', 'document_2.txt', 'document_3.txt']
    text_list = convert_text_to_text_class(path_txts, files_name)
    datab = DataB()
    datab.create_connection(path)
    for text in text_list:
        datab.insert_file(text)
    
    query = text_list[2].author
    select_files = f"SELECT Author FROM File WHERE File.Author = '{query}'"
    a = f"SELECT Author FROM File "
    result = datab.execute_read_query(a)
    print("RESULT ", result)
