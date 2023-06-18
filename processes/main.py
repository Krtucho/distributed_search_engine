from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import requests # Para realizar peticiones a otros servers y descargar archivos
from file_handler import *
from fastapi.middleware.cors import CORSMiddleware
from database import DataB, Text, convert_text_to_text_class
import threading
import os
import shutil


lock = threading.Lock()# Create a lock object
#VARIABLES DE ENTORNO
# Api Servers
servers = ['localhost']

# Clusters of n servers. Update when a new server joins
clusters = ['localhost']
database = DataB()
#port = 10001 #cambiar al cambiar de server
DATABASE_DIR = '/home/roxy/Roxana-linux/SD/distributed_search_engine/processes/databases/'
DOWNLOAD_DIR = os.path.join(os.getcwd() + "/", "downloads")

database_files = ['db1.db', 'db2.db', 'db3.db']
ports = [10002] #MODIFICAR CAMBIAR LISTA [10001,10002,10003]
path_txts = '/home/roxy/Roxana-linux/SD/distributed_search_engine/processes/txts'
files_name = ['document_1.txt', 'document_2.txt', 'document_3.txt'] #LOs 3 servidores tendran los mismos docs
app = FastAPI()

# Configuración de CORS
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://172.17.0.3",
    "http://172.17.0.3:8080",
    "http://172.17.0.1",
    "http://172.17.0.1:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


files = [
    {
    "id":0, 
    "file":{"file_name": "Archivo de Roxana", "server_number": 0}
    },
    { 
    "id":1, 
    "file":{"file_name": "Archivo de Paula", "server_number": 0}
    },
    {
    "id":2, 
    "file":{"file_name": "Archivo de Krtucho", "server_number": 0}
    }
]

def send_notification(port, text: str, results):
    with lock:
        print("ENTRO EN SEND NOTIFICATION")
        print("Hilo en ejecución: {}".format(threading.current_thread().name))
        print(clusters[0])
        server = f'http://{clusters[0]}:{port}/api/files/search/{text}'
        print(server)
        r = requests.get(server, verify=False)
        print("\R:")
        print(r)
        print(r.content)
        print(r.text)
        print("R/")
        results.extend(r)  # Add matched documents to the shared list
    
    
def search_by_text(text: str):
    print("ENTRO EN SEARCH BY TEXT")
    print(text)
    threading_list = []
    ranking = [] # List with the ranking and query documents results
    results = []  # Shared list to store the matched document names
    # Construir ranking a partir de cada listado de archivos recibidos gracias al tf_idf
    # Search text in every server
    # TODO: Paralelizar peticiones a todos los servidores para pedirles sus rankings. https://docs.python.org/es/3/library/multiprocessing.html
    for i, port in enumerate(ports): # Esta parte sera necesaria hacerla sincrona para recibir cada respuesta en paralelo y trabajar con varios hilos
        t = threading.Thread(target=send_notification, args=(port, text, results), name="Hilo {}".format(i))
        threading_list.append(t)
        print("T.START")
        t.start()
        
    for t in threading_list:
        print("T.JOIN")
        t.join()
    
    print(results)
    # Make Ranking
    # Luego de esperar cierta cantidad de segundos por los rankings pasamos a hacer un ranking general de todo lo q nos llego
    # TODO: Si alguna pc se demora mucho en devolver el ranking, pasamos a preguntarle a algun intregrante de su cluster que es lo que sucede

    # Return Response
    # Retornamos el ranking general de todos los rankings combinados
    return decorate_data(results)

def decorate_data(results):
    print("ENTRO A DECORATE DATA")
    final_string = {}
    for i, elem in enumerate(results):
        key = f'data_{i}'
        final_string[key] = {'name': elem, 'url': 'https://localhost:3000'}
    return final_string

def tf_idf(textt: str):
    pass # Paula

def match_by_name(text:str, datab):
    print("ENTRO EN MATCH BY NAME")
    print("Hilo en ejecución: {}".format(threading.current_thread().native_id))
    #select_files_title = f"SELECT Title FROM File WHERE File.Title = '{text}'"
    select_files_author = f"SELECT Author FROM File WHERE File.Author = '{text}'"
    #result_1 = datab.execute_read_query(select_files_title)
    result_2 = datab.execute_read_query(select_files_author)
    #print("RESULTADO TITLE",result_1)
    print("RESULTADO AUTHOR",result_2)
    return result_2 #,result_1

#Este metodo carga la base de datos del server al ser levantado este
def init_servers(datab): # De los servers yo se su IP
    print("INIT SERVERS")
    text_list = convert_text_to_text_class(path_txts,files_name)
    #A cada servidor le toca un archivo.db que se asigna en dependencia de su puerto
    datab.create_connection(DATABASE_DIR+database_files[0]) #MODIFICAR CAMBIAR ITERACION
    for file in text_list:
        datab.insert_file(file)
    print("SALIO DEL INIT")
   

class File(BaseModel):
    file_name: str
    server_number: int
    content: str
    # paginas:int
    # editorial: Optional[str]

# Obtener el número de puerto
@app.on_event("startup")
async def startup_event():
    print(f"La aplicación se está ejecutando...")

@app.get("/")
def index():
    
    import os

    my_variable = os.environ.get('CLUSTERS')
    
    if my_variable is not None:
        print(f"El valor de la variable de entorno MY_VARIABLE es {my_variable}")
    else:
        print("La variable de entorno MY_VARIABLE no está definida.")
    return {
        "data":[
            {"name": "Hello World!", "url":"https://localhost:3000"}
        ]
    }

# Cliente
# @app.get('/files/{id}')
# def show_file(id: int):
#     return search_file(id)#{"data": id}

# Cliente
@app.get('/files/search/{text}')
def show_file(text: str):
    print("ENTRO EN SHOW FILE")
    return search_by_text(text)#{"data": id}

# Server
# Este es el que llama al TF-IDF
@app.get('/api/files/search/{text}')
def search_file_in_db(text: str):
    print("ENTRO A SEARCH FILE IN DB")
    print("Hilo en ejecución: {}".format(threading.current_thread().name))
    #datab = DataB() #crear una nueva database en cada hilo
    #init_servers(datab)
    matched_documents = match_by_name(text, database)

    if matched_documents == None:
        #Calcularel tf_idf
        return tf_idf(text)#{"data": id}
    else:
        return matched_documents
   
@app.post("/files")
def add_file(file: File):
    return {"msg": f"File {file.file_name} a"}


# Uploading Files
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from os import getcwd, remove
from shutil import rmtree

router = APIRouter()


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    with open(os.getcwd() + "/" + file.filename, "wb") as myfile:
        content = await file.read()
        myfile.write(content)
        myfile.close()
    return "success"


@router.get("/file/{name_file}")
def get_file(name_file: str):
    return FileResponse(os.getcwd() + "/" + name_file)

# Cliente
# Metodo para que el cliente le pida un archivo a traves de una url al servidor con el que se esta comunicando
@router.get("/download/{filename}")
def download_file(filename: str):
    # Se le pide al servidor que se encuentra en url el archivo
    #file = download_file(url=url)#requests.get(url, verify=False
    actual_path = os.getcwd() + "/txts/" + filename + ".txt"
    response = FileResponse(actual_path, media_type="application/octet-stream", filename=filename)
    shutil.copy(actual_path, os.path.join(DOWNLOAD_DIR, filename))
    return response

# Server
@router.get("/api/download/{name_file}")
def download_file_from_server(name_file: str):
    return FileResponse(os.getcwd() + "/" + name_file, media_type="application/octet-stream", filename=name_file)

@router.delete("/delete/{name_file}")
def delete_file(name_file: str):
    try:
        remove(os.getcwd() + "/" + name_file)
        return JSONResponse(content={
            "removed": True
        }, status_code=200)
    except FileNotFoundError:
        return JSONResponse(content={
            "removed": False,
            "message": "File not found"
        }, status_code=404)

@router.delete("/folder")
def delete_file(folder_name: str = Form(...)):
    rmtree(os.getcwd() + folder_name)
    return JSONResponse(content={
        "removed": True
    }, status_code=200)

app.include_router(router)
print("EMPEZAMOS")
init_servers(database)