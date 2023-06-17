from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import requests # Para realizar peticiones a otros servers y descargar archivos
from file_handler import *
from fastapi.middleware.cors import CORSMiddleware
#from processes.database import DataB 
import threading

#### SRI ####
from vector_model import VectorModel
from pathlib import Path
import database
import os
#############


#VARIABLES DE ENTORNO
# Api Servers
servers = ['localhost']

# Clusters of n servers. Update when a new server joins
clusters = ['localhost']

port = 10002
#path_db = './db_1.db'

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


def send_notification(cluster, text: str):
    print(cluster)
    server = f'http://{cluster}:{port}/'
    print(server)
    r = requests.get(server, verify=False)


    # print(r)
    # print(r.content)
    # print(r.text)

def search_by_text(text: str):
    print("search_by_text, text: ", text)
    ranking = [] # List with the ranking and query documents results

    ####### testing #########
    r = tf
    #########################

    # Search text in every server
    # TODO: Paralelizar peticiones a todos los servidores para pedirles sus rankings. https://docs.python.org/es/3/library/multiprocessing.html
    for cluster in clusters: # Esta parte sera necesaria hacerla sincrona para recibir cada respuesta en paralelo y trabajar con varios hilos
        ranking.append(send_notification(cluster, text))

    # Make Ranking
    # Luego de esperar cierta cantidad de segundos por los rankings pasamos a hacer un ranking general de todo lo q nos llego
    # TODO: Si alguna pc se demora mucho en devolver el ranking, pasamos a preguntarle a algun intregrante de su cluster que es lo que sucede

    # Return Response
    # Retornamos el ranking general de todos los rankings combinados

######## SRI ########
vm = VectorModel()
path = Path("txts") # play
files_name=["document_1.txt","document_2.txt","document_102.txt","document_56.txt","document_387.txt"]

documents_list = database.convert_text_to_text_class(path=path, files_name=files_name)

vm.doc_terms_data(documents_list)
def tf_idf(textt: str):
    l = vm.run(textt)
    print(l)
    print("hola mundo")
    print(textt)
    return l
    # pass # Paula

#####################

#def match_by_name(datab,text:str):
#    select_files = f"SELECT name FROM File WHERE File.name = '{text}'"
#    result = datab.execute_read_query(select_files)
#    return result

#def init_servers(): # De los servers yo se su IP
#    print("INIT SERVERS")
#    datab = DataB()
#    datab.create_connection(path_db)
#    datab.insert_file("Hakuna Matata")
#    datab.insert_file("El viejo y el mar")

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
    print("show_file, text ", text)
    return search_by_text(text)#{"data": id}

# Server
# Este es el que llama al TF-IDF
@app.get('/api/files/search/{text}')
def search_file_in_db(text: str):
    print(text)
    threading_list = []
    # Construir ranking a partir de cada listado de archivos recibidos gracias al tf_idf
    #for i, cluster in enumerate(clusters):
    #    t = threading.Thread(target=match_by_name,args=(text,), name=f't{i}')
    #    threading_list.append(t)
    #    #matched = match_by_name(text)
    #for t in threading_list:
    #    t.start()
    #for t in threading_list:
    #    t.join()
    print("search_file_in_database")
    return tf_idf(text)#{"data": id}

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
    file = download_file(url=url)#requests.get(url, verify=False)


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