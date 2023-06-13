<<<<<<< HEAD
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

import requests # Para realizar peticiones a otros servers y descargar archivos

# Api Servers
servers = ['localhost']

# Clusters of n servers. Update when a new server joins
clusters = ['localhost']

port = 8000

app = FastAPI()


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


def search_file(id):
    return [file["file"] for file in files if file["id"] == id]


def send_notification(cluster, text: str):
    print(cluster)
    server = f'http://{cluster}:{port}/'
    print(server)
    r = requests.get(server, verify=False)
    print(r)
    print(r.content)
    print(r.text)

def search_by_text(text: str):
    print(text)
    # Search text in every server
    for cluster in clusters:
        send_notification(cluster, text)

    # Make Ranking

    # Return Response


def tf_idf(textt: str):
    pass # Paula

class File(BaseModel):
    file_name: str
    server_number: int
    content: str
    # paginas:int
    # editorial: Optional[str]


@app.get("/")
def index():
    return {"msg": "Hello World!"}


@app.get('/files/{id}')
def show_file(id: int):
    return search_file(id)#{"data": id}

# Cliente
@app.get('/files/search/{text}')
def show_file(text: str):
    return search_by_text(text)#{"data": id}

# Server
# Este es el que llama al TF-IDF
@app.get('/files/search/{text}')
def search_file_in_db(text: str):
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


@router.get("/download/{name_file}")
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

=======
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

import requests # Para realizar peticiones a otros servers y descargar archivos

from file_handler import *

# Api Servers
servers = ['localhost']

# Clusters of n servers. Update when a new server joins
clusters = ['localhost']

port = 8000

app = FastAPI()


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
    print(text)
    ranking = [] # List with the ranking and query documents results
    # Search text in every server
    # TODO: Parallizar peticiones a todos los servidores para pedirles sus rankings. https://docs.python.org/es/3/library/multiprocessing.html
    for cluster in clusters: # Esta parte sera necesaria hacerla sincrona para recibir cada respuesta en paralelo y trabajar con varios hilos
        ranking.append(send_notification(cluster, text))

    # Make Ranking
    # Luego de esperar cierta cantidad de segundos por los rankings pasamos a hacer un ranking general de todo lo q nos llego
    # TODO: Si alguna pc se demora mucho en devolver el ranking, pasamos a preguntarle a algun intregrante de su cluster que es lo que sucede

    # Return Response
    # Retornamos el ranking general de todos los rankings combinados


def tf_idf(textt: str):
    pass # Paula

class File(BaseModel):
    file_name: str
    server_number: int
    content: str
    # paginas:int
    # editorial: Optional[str]


@app.get("/")
def index():
    return {"msg": "Hello World!"}

# Cliente
# @app.get('/files/{id}')
# def show_file(id: int):
#     return search_file(id)#{"data": id}

# Cliente
@app.get('/files/search/{text}')
def show_file(text: str):
    return search_by_text(text)#{"data": id}

# Server
# Este es el que llama al TF-IDF
@app.get('/api/files/search/{text}')
def search_file_in_db(text: str):
    # Construir ranking a partir de cada listado de archivos recibidos gracias al tf_idf
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

>>>>>>> roxy_branch
app.include_router(router)