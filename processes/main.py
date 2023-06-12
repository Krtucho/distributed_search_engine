from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import requests # Para realizar peticiones a otros servers y descargar archivos
from file_handler import *
from fastapi.middleware.cors import CORSMiddleware
from database import DataB

import threading

#VARIABLES DE ENTORNO
# Api Servers
servers = ['localhost']

# Clusters of n servers. Update when a new server joins
clusters = ['localhost']
database = DataB()
port = 10001 #cambiar al cambiar de server
path_db = './databases/db_3.db' #cambiar al cambiar de server

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


# def search_file(id):
#     return [file["file"] for file in files if file["id"] == id]


def send_notification(cluster, text: str, results):
    print("ENTRO EN SEND NOTIFICATION")
    print("Hilo en ejecución: {}".format(threading.current_thread().name))
    print(cluster)
    server = f'http://{cluster}:{port}/api/files/search/{text}'
    print(server)
    r = requests.get(server, verify=False)
    
    print("R:")
    print(r)
    print(r.content)
    print(r.text)
    results.extend(r)  # Add matched documents to the shared list
    

def search_by_text(text: str):
    print(text)
    print("ENTRO EN SEARCH BY TEXT")
    threading_list = []
    ranking = [] # List with the ranking and query documents results
    results = []  # Shared list to store the matched document names
    # Construir ranking a partir de cada listado de archivos recibidos gracias al tf_idf
    # Search text in every server
    print("cantidad de clusters = ", len(clusters))
    # TODO: Paralelizar peticiones a todos los servidores para pedirles sus rankings. https://docs.python.org/es/3/library/multiprocessing.html
    for i, cluster in enumerate(clusters): # Esta parte sera necesaria hacerla sincrona para recibir cada respuesta en paralelo y trabajar con varios hilos
        t = threading.Thread(target=send_notification, args=(cluster, text, results), name="Hilo {}".format(i))
        threading_list.append(t)

    print("T.START")
    for t in threading_list:
        t.start()
    print("T.JOIN")
    for t in threading_list:
        t.join()
    
    print(results)
    # Make Ranking
    # Luego de esperar cierta cantidad de segundos por los rankings pasamos a hacer un ranking general de todo lo q nos llego
    # TODO: Si alguna pc se demora mucho en devolver el ranking, pasamos a preguntarle a algun intregrante de su cluster que es lo que sucede

    # Return Response
    # Retornamos el ranking general de todos los rankings combinados
    return decorate_data(results)

def decorate_data(results):
    final_string = {}
    for i, elem in enumerate(results):
        key = f"data_{i}"
        final_string[key] = {"name": elem, "url": "https://localhost:3000"}
    return final_string

def tf_idf(textt: str):
    pass # Paula

def match_by_name(text:str, datab):
    print("ENTRO EN MATCH BY NAME")
    print("Hilo en ejecución: {}".format(threading.current_thread().name))
    select_files = f"SELECT name FROM File WHERE File.name = '{text}'"
    result = datab.execute_read_query(select_files)
    print("RESULTADO ",result)
    return result

def init_servers(datab): # De los servers yo se su IP
    print("INIT SERVERS")
    datab.create_connection(path_db)
    datab.insert_file("Hakuna_Matata")
    datab.insert_file("El viejo y el mar")

class File(BaseModel):
    file_name: str
    server_number: int
    content: str
    # paginas:int
    # editorial: Optional[str]


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
    print("PORT (el port 2 es el server 1 (y al reves)) = ",port)
    print("Hilo en ejecución: {}".format(threading.current_thread().name))
    # Crea una nueva conexión en cada hilo
    print("CREAR NUEVA DATAB")
    datab = DataB()
    init_servers(datab)
    matched_documents = match_by_name(text, datab)
    # Cierra la conexión después de usarla
    datab.close_connection()

    if matched_documents == None:
        #Calcularel tf_idf
        return tf_idf(text)#{"data": id}
    else:
        return decorate_data(matched_documents)
   
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
    with open(getcwd() + "/" + file.filename, "wb") as myfile:
        content = await file.read()
        myfile.write(content)
        myfile.close()
    return "success"


@router.get("/file/{name_file}")
def get_file(name_file: str):
    return FileResponse(getcwd() + "/" + name_file)

# Cliente
# Metodo para que el cliente le pida un archivo a traves de una url al servidor con el que se esta comunicando
@router.get("/download/{url}")
def download_file(url: str):
    # Se le pide al servidor que se encuentra en url el archivo
    # server = f'{cluster}'
    # print(server)
    file = download_file(url=url)#requests.get(url, verify=False
    return FileResponse(getcwd() + "/" + file, media_type="application/octet-stream", filename=file)

# Server
@router.get("/api/download/{name_file}")
def download_file(name_file: str):
    return FileResponse(getcwd() + "/" + name_file, media_type="application/octet-stream", filename=name_file)

@router.delete("/delete/{name_file}")
def delete_file(name_file: str):
    try:
        remove(getcwd() + "/" + name_file)
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
    rmtree(getcwd() + folder_name)
    return JSONResponse(content={
        "removed": True
    }, status_code=200)

app.include_router(router)
print("EMPEZAMOS")
init_servers(database)