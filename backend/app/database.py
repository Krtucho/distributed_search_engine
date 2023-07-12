import sqlite3
from sqlite3 import Error
import re
#import os
#from parser_cran import get_data_from
from pydantic import BaseModel


class Text(BaseModel):
    id : int
    title : str
    author : str
    body : str

    def __str__(self) -> str:
        return f"id:{self.id} title:{self.title} author:{self.author}"

class DataB:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.datab = ""
        
    def insert_file(self, text_file: Text):     
        create_users = """INSERT INTO
        File(ID,Title, Author, Body)
        VALUES
        (?, ?, ?, ?);
        """
        self.execute_query(create_users, text_file)
        
    def remove_file(self, id_doc: int):
        delete_file = f"""DELETE FROM File WHERE ID = {id_doc};"""
        self.execute_query(delete_file, "")

    def get_documents(self):
        docs = []
        query = "SELECT * FROM File;"
        result = self.execute_read_query(query)
        if result:
            for row in result:
                id = row[0]
                title = row[1]
                author = row[2]
                body = row[3]
                document = Text(id, title, author, body)
                docs.append(document)
        return docs

    def close_connection(self):
        self.cursor.close()
        self.connection.close()
      
    def open_connection(self):
        self.connection = sqlite3.connect(self.datab)
        self.cursor = self.connection.cursor()
        
    def create_connection(self, path):
        try:
            self.datab = path
            create_files_table = '''
                CREATE TABLE IF NOT EXISTS File (
                    ID INTEGER PRIMARY KEY ,
                    Title TEXT NOT NULL UNIQUE,
                    Author TEXT,
                    Body TEXT NOT NULL
                )
            '''
            self.execute_query(create_files_table, "")
            print("Connection to SQLiteDB successful")
        except Error as e:
            print(f"The error '{e}' ocurred")
            
    def execute_read_query(self, query):
        self.open_connection()
        print("QUERY ", query)
        result = None
        try:
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            return result
        except Error as e:
            print(f"The error '{e}' occurred")
        self.close_connection()

    def execute_query(self, query, text_file):
        self.open_connection()
        try:
            if text_file != "":
                self.cursor.execute(query, (text_file.id, text_file.title, text_file.author, text_file.body))
            else: 
                self.cursor.execute(query)
            self.connection.commit()
            print("Query executed successfully")
        except Error as e:
            print(f"The error '{e}' ocurred")
        self.close_connection()

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
            title_ = title.group(1)
            title_text = title_.replace('\n', ' ')
            author_text = author.group(1).strip()
            body_ = body.group(1)
            body_text = body_.replace('\n', ' ')
            text = Text(id = id_text, title = title_text,author = author_text, body = body_text)
            text_list.append(text)
    return text_list

#if __name__ == '__main__':
       #PARA PROBAR LOS METODOS
    #current_dir = os.path.dirname(os.path.abspath(__file__))
    #path =  os.path.join(current_dir, "databases/db44.db")
    #path_txts =  os.path.join(current_dir, "txts")
    #
    #files_name = ['document_1.txt', 'document_2.txt', 'document_3.txt']
    #text_list = convert_text_to_text_class(path_txts, files_name)
    #datab = DataB()
    #datab.create_connection(path)
    #for text in text_list:
    #    datab.insert_file(text)
    #
    #textlist = datab.get_documents()
    #for t in textlist:
    #    print(t)
    #author = text_list[0].author
    #query_ID = f"SELECT ID FROM File WHERE File.ID = '{0}'"
    #result_ID = datab.execute_read_query(query_ID)
    #print("result ID 0 ", result_ID)
    #print("len ", len(result_ID))
    #select_files = f"SELECT ID, Author FROM File WHERE File.Author = '{author}'"
#
    #title = 'experimental investigation'
    #select_title = f"SELECT ID, Title FROM File"
    #result = datab.execute_read_query(select_title)
    #print("RESULT ", result)
    #lista_titles = []
    #for i in result:
    #    if title in i[1]:
    #        lista_titles.append(i)
    #    print("result[0]",i[0])
    #    print("result[1]",i[1])
    #    print()
    #
    #print("lista_titles ", lista_titles)
    #