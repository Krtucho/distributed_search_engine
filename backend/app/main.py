from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List
from math import floor

import requests # Para realizar peticiones a otros servers y descargar archivos

from file_handler import *
# from app.file_handler import *


from fastapi.middleware.cors import CORSMiddleware
from database import DataB, convert_text_to_text_class
import threading, time, os

# Logs
from logs.logs_format import *

#### SRI ####
from vector_model import VectorModel
from pathlib import Path
import database
# import os
#############


# Logs
from logs.logs_format import *

from servers import *

# Variable para decir si es esta corriendo en local o en docker
local = True

# Docker
gateway = "172.21.0.1"

# Api Servers
servers:List[Address] = get_servers(local)

# servers = ['localhost']

# Clusters of n servers. Update when a new server joins
clusters = ['localhost']

# Chord
first_server_address_ip = servers[0].ip if len(servers) > 0 else 'localhost' # Correrlo local
first_server_address_port = 8000  # Correrlo local

if local:
    first_server_address_ip = 'localhost' # Correrlo local
    first_server_address_port = 10000  # Correrlo local

# Chord Thread
stopped = False

server = 'localhost'
port = 10000 # Correrlo local

if not local:
    server = str(os.environ.get('IP')) # Correrlo con Docker
    port = int(os.environ.get('PORT')) # Correrlo con Docker

# print(port)
TIMEOUT = 20
if not local:
    try:
        TIMEOUT = int(os.environ.get('TIMEOUT')) # Correrlo con Docker
    except:
        pass

# Files
filepath = "/downloads/"
if not local:
    try:
        filepath = str(os.environ.get('FILEPATH')) # Correrlo con Docker
    except:
        pass


app = FastAPI()

#ROXANA
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
lock = threading.Lock() 
ports = [10002] #MODIFICAR CAMBIAR LISTA [10001,10002,10003]
PATH_TXTS = os.path.join(CURRENT_DIR, "txts")
#files_name = ['document_1.txt', 'document_2.txt', 'document_3.txt'] #LOs 3 servidores tendran los mismos docs
DATABASE_DIR = os.path.join(CURRENT_DIR, "databases")
database_files = ['db_1.db', 'db_2.db', 'db_3.db']
database = DataB()
server_ip = '0.0.0.0' #NECESITO SABER EL IP DE CADA SERVIDOR Y TENERLO EN UNA VARIABLE
servers_list = {'0.0.0.0', '0.0.0.1', '0.0.0.2'} # NECESITO SABER EL TOTAL DE SERVIDORES DE LA RED
n_doc = 9 #1400 # NUMERO TOTAL DE DOCUMENTOS DE LA RED
# 499: greensite,a.l.
# 348: van driest,e.r.
# 139: mcmillan,f.a.


############ SRI ############
vec_mod = VectorModel()

######## SRI ########
# vm = VectorModel()
# path = Path("txts") # play
# files_name=["document_1.txt","document_2.txt","document_102.txt","document_56.txt","document_387.txt"]

# documents_list = convert_text_to_text_class(path=path, files_name=files_name)

# 

#############################


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

def process_results(result):
    pass

def send_notification(port, text: str, results): #ROXANA
    with lock:
        print("ENTRO EN SEND NOTIFICATION")
        print("Hilo en ejecución: {}".format(threading.current_thread().name))
        print(clusters[0])
        server = f'http://{clusters[0]}:{port}/api/files/search/{text}'
        print(server)
        result = requests.get(server, verify=False)
        print("\R:")
        print("result ",result)
        print("result.content ",result.content)
        print("result.text ",result.text)
        print("result.text[0] ",result.text[0])
        print("R/")

        #try:
        #    # Process your response content here
        #    # Make sure all properties and objects are serializable
        #    processed_results = process_results(result)
        #    # Extend the processed results to the shared list
        #    results.extend(processed_results)
        #except Exception as e:
        #    # Handle any specific serialization errors here
        #    # Log the error or take appropriate action
        #    print(f"Serialization Error: {e}")
        ## ... rest of your code ...
        for r in result:
            print("r ", r)
            print("r[0] ", r[0])
            print("r[1] ", r[1])
            results.append(r) #results.extend(r)  # Add matched documents to the shared list
        print("results in send_notification ", results)

    
def search_by_text(text: str): #ROXANA
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
    
    print("search_by_text results ",results) 
    # Make Ranking 
    # Luego de esperar cierta cantidad de segundos por los rankings pasamos a hacer un ranking general de todo lo q nos llego
    # TODO: Si alguna pc se demora mucho en devolver el ranking, pasamos a preguntarle a algun intregrante de su cluster que es lo que sucede
    
    _ranking = [] # aqui tiene q estar la union de los rankings de todos los servidores

    ranking_ord = sorted(_ranking, key=lambda x: x[1], reverse=True)

    visited = set()
    new_rank = []

    for t in ranking_ord:
        if t[0] not in visited:
            new_rank.append(t)
            visited.add(t[0])
    
    result = []

    for id, rank in new_rank:
        db_query = f"SELECT * FROM File WHERE File.ID = '{str(id)}'"
        result.append(database.execute_read_query(db_query))
    
    # return result

    # Return Response
    # Retornamos el ranking general de todos los rankings combinados
    return decorate_data(results)

def decorate_data(results): #ROXANA
    print("ENTRO A DECORATE DATA")
    print("results ", results)
    final_string = {}
    for i, elem in enumerate(results):
        print(f"i={i}, elem= {elem}")
        key = f'data_{i}'
        final_string[key] = {'name': elem, 'url': 'https://localhost:3000'}
    print("final string ", final_string)
    return final_string

def match_by_name(text:str): #ROXANA
    print("ENTRO EN MATCH BY NAME")
    print("Hilo en ejecución: {}".format(threading.current_thread().native_id))
    #select_files_title = f"SELECT Title FROM File WHERE File.Title = '{text}'"
    select_files_author = f"SELECT ID, Author FROM File WHERE File.Author = '{text}'"
    select_all_authors = f"SELECT ID, Author FROM File"
    result_1 = database.execute_read_query(select_all_authors)
    result_2 = database.execute_read_query(select_files_author)

    print("RESULTADO ALL AUTHORS",result_1)
    print("RESULTADO AUTHOR",result_2)
    return result_2 #,result_1

####### SRI #######
def tf_idf(textt: str):
    return vec_mod.run(textt)
    # pass # Paula
###################

#asignar los documentos a cada server segun el orden en la lista
def assign_documents(index): #ROXANA
    print("ENTRO A ASSIGN DOCUMENTS")
    files_list = []
    start = index*floor(n_doc/len(servers_list))
    end = (index + 1)*floor(n_doc/len(servers_list))
    contenido = os.listdir(PATH_TXTS)
    for doc in contenido[start:end]:
        print("doc ", doc)
        files_list.append(doc)
    return files_list

def check_database(number):
    query = f"SELECT ID FROM File WHERE File.ID = '{number}'"
    result_ID = database.execute_read_query(query)
    return result_ID

# Este metodo carga la base de datos del server al ser levantado este
# Asumo que conozco los IPs de cada servidor y la cantidad de servidores 
def init_servers(datab): #ROXANA
    print("INIT SERVERS")
    for i, s in enumerate(servers_list):
        print("index ", i)
        print(f"s == server_ip: {s}=={server_ip}")
        if s == server_ip:
            files_list = assign_documents(i)
            print("files_list ", files_list)
            print("PATH_TXTS ", PATH_TXTS)
            text_list = convert_text_to_text_class(PATH_TXTS,files_list)
            #A cada servidor le toca un archivo.db que se asigna en dependencia de su puerto
            print(DATABASE_DIR + "/"+ database_files[0])
            datab.create_connection(DATABASE_DIR + "/"+ database_files[0]) #MODIFICAR CAMBIAR ITERACION
            for file in text_list:
                datab.insert_file(file)

            ######### SRI #########
            vm.doc_terms_data(documents_list) # se le pasa la lista de archivos que se le pasa a la base de datos de ese server
                                              # aqui empieza a calc os tf idf
            #######################

    # node.run() #CARLOS
    print("Node Run")
    # t1 = threading.Thread(target=node.run)
    t2 = threading.Thread(target=chord_replication_routine)

    # t1.start()
    t2.start()

    print("SALIO DEL INIT")


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
    node_id:int
    ip:str
    port:int

class FilesModel(AddressModel):
    files:List[str] = []


@app.on_event("startup") #ROXANA
async def startup_event():
    print(f"La aplicación se está ejecutando...")

@app.get("/")
def index():
    
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
@app.get('/files/search/{text}') #ROXANA
def show_file(text: str):
    print("ENTRO EN SHOW FILE")
    return search_by_text(text)#{"data": id}

# Server
# Este es el que llama al TF-IDF
@app.get('/api/files/search/{text}') 
def search_file_in_db(text: str): #ROXANA
    print("ENTRO A SEARCH FILE IN DB")
    print("Hilo en ejecución: {}".format(threading.current_thread().name))
    #datab = DataB() #crear una nueva database en cada hilo
    #init_servers(datab)
    matched_documents = match_by_name(text)

    print("matched documents ", matched_documents)
    if matched_documents == None:
        #Calcularel tf_idf
        return tf_idf(text)#{"data": id}
    else:
        return matched_documents


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
def send_notification_app(message: Message):
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
    nodeID = None
    if node.is_leader:
        nodeID  = int(node.chan.join('node', message.server_ip, message.server_port)) # Find out who you are         #-
        node.addNode(nodeID)
        node.recomputeFingerTable()
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

# Confirmar que ya se replico la informacion en el siguiente nodo
@app.post('/chord/succ/data/done')
def post_data(files: FilesModel):
    print("Replication Done!", files.files)
    return node.confirm_pred_data_info(files.node_id, Address(files.ip, files.port), files.files)#node.check_pred_data(address.node_id, Address(address.ip, address.port))#return {"osmembers":channel.osmembers, "nBits":channel.nBits, "MAXPROC":channel.MAXPROC }#search_by_text(text)#{"data": id}

# Verificar si ya se replico la informacion en el siguiente nodo
@app.post('/chord/succ/data')
def verify_data(address: AddressModel):
    return node.check_pred_data(address.node_id, Address(address.ip, address.port))#return {"osmembers":channel.osmembers, "nBits":channel.nBits, "MAXPROC":channel.MAXPROC }#search_by_text(text)#{"data": id}


def chord_replication_routine():
    print("Started Node Replication Routine")
    print("Timeout: ", TIMEOUT)
    stopped = False
    try:
        while not stopped:
            # Obtener el sucesor
            next_id, next_address = node.get_succesor(), node.chan.get_member(node.get_succesor())#node.localSuccNode(node.nodeID)
            print("Successor", next_id, next_address)
            # Buscar si el siguiente nodo sigue activo
            # Verificar si ya se replico la informacion al sucesor
            # Al hacer la peticion verifico si sigue activo y ademas si ya se replico la info
            data = {}
            r = None
            if (not next_id == None ) and (not next_address == None):
                next_address = Address.extract_ip_port(next_address)
                data = {"node_id":node.nodeID, "ip":node.node_address.ip,"port": int(node.node_address.port)}
                try:
                    r = requests.post(f"http://{next_address.ip}:{next_address.port}/chord/succ/data", json=data, timeout=TIMEOUT)
                except Exception as e:
                    print("Error trying to verify data replication")
                    print(e)
            # Si no se ha replicado la informacion. Copiala
            if r:
                print("Inside Verifying Data Replication")
                text = bool(r.json())
                print(text)
                print(r.text)
                print(r.content)
                print(r.json())
                if not text:
                    #   Si no se ha replicado, replicalo!
                    node.make_replication(next_id, next_address)
            # Si el siguiente se cayo, vuelvela a copiar, busca primero el nodo
            else:
                node.update_succesors()
                node.succ = node.get_succesor()
                if node.succ:
                    node.make_replication(next_id, next_address)

            # Busca si el de atras ya existe:
            if node.predecessor:

                r = None
                # Busca si se cae el de atras
                try:
                    r = requests.get(f"http://{node.predecessor[1].ip}:{node.predecessor[1].port}/")
                except Exception as e:
                    print(e)
                # Si se cae el de atras
                if not r or not r.ok:
                    # Agrega al conjunto del actual el contenido que tenias del de atras que estaba replicado en ti
                    content = node.merge()
                    # Este nuevo contenido pasaselo a tu sucesor si es q no ha cambiado, si cambio, pasale el nuevo contenido mas
                    # el tuyo
                    node.make_replication(next_id, next_address, content)
                    # TODO: FixBug TypeError: 'NoneType' object does not support item assignment
                    node.restart_pred_data_info(node.predecessor[0])
            # else:
                # Si aun no se tiene predecesor, esperamos a que el venga a buscarnos

            # TODO: Agregar rutina de FixFinger para que se ejecute a cada rato
            node.recomputeFingerTable() #-
            print("FT", node.FT)
            # print('FT[','%04d'%node.nodeID,']: ',['%04d' % k for k in node.FT]) #- 
            
            if node.is_leader:
                node.check_live_nodes()

            print_info(node)

            # Reccess
            print(f"On Thread...Sleeping for {TIMEOUT} seconds")
            time.sleep(TIMEOUT)
    except KeyboardInterrupt as e:
        print("Stopping Chord Routine Thread...")
        stopped = True
    

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
@router.get("/download/{number}")
def download_file(number: str):
    print("ENTRO EN DOWNLOAD FILE")
    print("number ", number)
    doc = "document_" +number +".txt"
    file_path = Path(os.path.join(PATH_TXTS,doc))

    print("filepath ", filepath)
    if not file_path.exists(): #Comprueba si el archivo existe en la carpeta txts
        return {"error": f"File '{doc}' not found in the folder."}
    
    #Comprobar si el archivo esta en la base de datos del servidor
    result_ID = check_database(number)
    
    if len(result_ID) > 0:
        response = FileResponse(file_path,media_type="application/octet-stream", filename=doc)
    else:
        response = {"error": f"File '{doc}' not found in the database."}
    return response 

# Server
@router.get("/api/download/{number}")
def download_file_api(number: str):
    print("ENTRO EN API DOWNLOAD")
    filename = f"document_{number}.txt"
    print("FILENAME ", filename)

    #Comprobar si el archivo esta en la base de datos del servidor
    result_ID = check_database(number)
    if len(result_ID) > 0:
        response = FileResponse(getcwd() + "/txts" + "/"+filename, media_type="application/octet-stream", filename=filename)
    else:
        response = {"error": f"File '{filename}' not found in the database."}
    return response
    #return FileResponse(getcwd() + "/downloads" + "/"+filename, media_type="application/octet-stream", filename=filename)

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
