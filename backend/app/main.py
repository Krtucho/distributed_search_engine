from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

import requests # Para realizar peticiones a otros servers y descargar archivos

from file_handler import *
# from app.file_handler import *


from fastapi.middleware.cors import CORSMiddleware

import threading, time

# Api Servers
servers = ['localhost']

# Clusters of n servers. Update when a new server joins
clusters = ['localhost']

# Chord
first_server_address_ip = 'localhost'
first_server_address_port = 10001

# Chord Thread
stopped = False

server = 'localhost'
port = 10002

TIMEOUT = 20

# Files
filepath = "/downloads/"

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

class Message(BaseModel):
    server_ip: str
    server_port: int
    content: str

class AddressModel(BaseModel):
    ip:str
    port:int


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

# Chord
# Chord Variables
from chord.chord import *
from chord.channel import *

channel: Channel = None
node = ChordNode(channel, Address(first_server_address_ip, 
                                  first_server_address_port), 
                            Address(server, port))
channel = node.chan
# Chord endpoints
@app.post('/chord/receive/{text}')
def receive_notification(text: str):
    print(text)

     # Finger Table Routine
         # Create Thread for this process
        # Or create an endpoint
        # while True: #-

    # TODO: change this line for request from fastapi endpoint
    # Done! message = node.chan.recvFromAny() # Wait for any request #-
    # TODO: change this line for request from fastapi endpoint

    # sender  = message[0]              # Identify the sender #-
    # request = message[1]              # And the actual request #-
    # if request[0] != LEAVE: #and self.chan.channel.sismember('node',str(sender)): #-
    #     node.addNode(sender) #-
    # if request[0] == STOP: #-
    #     break #-
    # if request[0] == LOOKUP_REQ:                       # A lookup request #-
    #     nextID = node.localSuccNode(request[1])          # look up next node #-
    #     server = node.chan.sendTo([sender], (LOOKUP_REP, nextID)) # return to sender #-
    #     # node.make_request(server)
    #     data = {"server":server, "msg":(LOOKUP_REP, nextID)}
    #     requests.post(f"http://{server.address.ip}:{server.address.port}/")
    #     if not nextID in node.get_members():#node.chan.exists(nextID): #-
    #         node.delNode(nextID) #-
    # elif request[0] == JOIN: #-
    #     continue #-
    # elif request[0] == LEAVE: #-
    #     node.delNode(sender) #-
    # node.recomputeFingerTable() #-
    # print('FT[','%04d'%node.nodeID,']: ',['%04d' % k for k in node.FT]) #- 

    return text#{"data": id}

@app.post("/chord/send")
def send_notification(message: Message):
    return {"server":f"Server: {message.server}","msg": f"msg: {message.content}"}

# Chord Channel Endpoints
def parse_server(message:Message):
    temp = dict(message.server)
    print(temp)
    return temp

@app.post("/chord/channel/join")
def send_message(message: Message):
    print(message.server_ip, message.server_port, message.content)
    # parse_server(message)
    nodeID  = int(node.chan.join('node', message.server_ip, message.server_port)) # Find out who you are         #-
    # return {"server":f"Server: {message.server}","msg": f"msg: {message.content}"}
    return nodeID
@app.get('/chord/channel/info')
def get_channel_members():
    return {"osmembers":node.chan.osmembers, "nBits":node.chan.nBits, "MAXPROC":node.chan.MAXPROC, "address":node.chan.address }#search_by_text(text)#{"data": id}



@app.get('/chord/channel/members')
def get_channel_members():
    return {"osmembers":node.chan.osmembers, "nBits":node.chan.nBits, "MAXPROC":node.chan.MAXPROC }#search_by_text(text)#{"data": id}

# Chord Replication Endpoints
# Si el predecesor envia un mensaje para replicarse, el sucesor guarda la informacion del mismo
@app.get('/chord/succ/{text}')
def get_channel(text: str):
    return {"osmembers":channel.osmembers, "nBits":channel.nBits, "MAXPROC":channel.MAXPROC }#search_by_text(text)#{"data": id}

# Verificar si ya se replico la informacion en el siguiente nodo
@app.get('/chord/succ/data')
def get_channel(address: AddressModel):
    return node.check_pred_data(Address(address.ip, address.port))#return {"osmembers":channel.osmembers, "nBits":channel.nBits, "MAXPROC":channel.MAXPROC }#search_by_text(text)#{"data": id}



def chord_replication_routine():
    print("Started Node Replication Routine")
    print("Timeout: ", TIMEOUT)
    stopped = False
    try:
        while not stopped:
            # Obtener el sucesor
            next_id, next_address = node.localSuccNode(node.nodeID)
            print("Successor", next_id, next_address)
            # Buscar si el siguiente nodo sigue activo
            # Verificar si ya se replico la informacion al sucesor
            # Al hacer la peticion verifico si sigue activo y ademas si ya se replico la info
            data = {}
            r = None
            if (not next_id == None ) and (not next_address == None):
                data = {"ip":next_address.ip,"port": next_address.port}
                r = requests.get(f"http://{next_id}:{next_address}/chord/succ/data", data=data, timeout=TIMEOUT)

            # Si no se ha replicado la informacion. Copiala
            if r:
                text = r.text()
                if not text == "True":
                    #   Si no se ha replicado, replicalo!
                    node.make_replication(next_id, next_address)
            # Si el siguiente se cayo, vuelvela a copiar, busca primero el nodo
            else:
                node.update_succesors()
                succ = node.get_succesor()
                if succ:
                    node.make_replication(next_id, next_address)

            # Busca si el de atras ya existe:
            if node.predecessor:

                # Busca si se cae el de atras
                r = requests.get(f"http://{node.predecessor.ip}:{node.predecessor.port}/")
                # Si se cae el de atras
                if not r.ok:
                    # Agrega al conjunto del actual el contenido que tenias del de atras que estaba replicado en ti
                    content = node.merge()
                    # Este nuevo contenido pasaselo a tu sucesor si es q no ha cambiado, si cambio, pasale el nuevo contenido mas
                    # el tuyo
                    node.make_replication(next_id, next_address, content)
            # else:
                # Si aun no se tiene predecesor, esperamos a que el venga a buscarnos

            # TODO: Agregar rutina de FixFinger para que se ejecute a cada rato
            node.recomputeFingerTable() #-
            print("FT", node.FT)
            # print('FT[','%04d'%node.nodeID,']: ',['%04d' % k for k in node.FT]) #- 
            
            print(node)

            # Reccess
            print(f"On Thread...Sleeping for {TIMEOUT} seconds")
            time.sleep(TIMEOUT)
    except KeyboardInterrupt as e:
        print("Stopping Chord Routine Thread...")
        stopped = True

def init_servers():
    # node.run()
    print("Node Run")
    # t1 = threading.Thread(target=node.run)
    t2 = threading.Thread(target=chord_replication_routine)

    # t1.start()
    t2.start()
    

# Uploading Files
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from os import getcwd, remove
from shutil import rmtree

router = APIRouter()


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    with open(getcwd() + "/downloads" + file.filename, "wb") as myfile:
        content = await file.read()
        myfile.write(content)
        myfile.close()
    return "success"


@router.get("/file/{name_file}")
def get_file(name_file: str):
    return FileResponse(getcwd() + "/downloads" + name_file)

# Cliente
# Metodo para que el cliente le pida un archivo a traves de una url al servidor con el que se esta comunicando
@router.get("/download/{url}")
def download_file(url: str):
    # Se le pide al servidor que se encuentra en url el archivo
    # server = f'{cluster}'
    # print(server)
    file = download_file(url=url)#requests.get(url, verify=False)


    return FileResponse(getcwd() + "/downloads" + file, media_type="application/octet-stream", filename=file)

# Server
@router.get("/api/download/{name_file}")
def download_file(name_file: str):
    return FileResponse(getcwd() + "/downloads" + name_file, media_type="application/octet-stream", filename=name_file)

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

init_servers()