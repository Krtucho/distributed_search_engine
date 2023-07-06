from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List

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
first_server_address_ip = 'localhost' # Correrlo local 
first_server_address_port = 10000  # Correrlo local 10000

if local:
    first_server_address_ip = 'localhost' # Correrlo local
    first_server_address_port = 10000  # Correrlo local

# Chord Thread
stopped = False

server = 'localhost'
port = 10001 # Correrlo local

if not local:
    server = str(os.environ.get('IP')) # Correrlo con Docker
    port = int(os.environ.get('PORT')) # Correrlo con Docker

#if local: #ROXANA
#    server = str(os.environ.get('IP')) # Correrlo local
#    port = int(os.environ.get('PORT')) # Correrlo local

print("SERVER IP ROXANA = ", server)#ROXANA
print("PORT ROXANA = ", port)

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
PATH_TXTS = os.path.join(CURRENT_DIR, "txts")
DATABASE_DIR = os.path.join(CURRENT_DIR, "databases")
lock = threading.Lock()
database = DataB()
my_port = 10002
ports_list = [] #LISTA DE PUERTOS DE CADA NUEVO SERVIDOR DE LA RED
servers_ID_list = [] # NECESITO SABER EL TOTAL DE SERVIDORES DE LA RED y su ID
servers_IP_list = [] # con su IP

database_files = ['db_1.db', 'db_2.db', 'db_3.db']
change_db = 1

n_doc = 10 #1400 # NUMERO TOTAL DE DOCUMENTOS DE LA RED
# 499: greensite,a.l.
# 348: van driest,e.r.
# 139: mcmillan,f.a.


############ SRI ############
vec_mod = VectorModel()
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


def send_notification(port, text: str, results): #ROXANA
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

        selected_list = result.json()
        print("selected list ", selected_list)

        if notification_type: #REQUEST SEARCH
            selected_name = selected_list[1]
            selected_result = selected_list[0]
            print("selected_name ", selected_name)
            if selected_name:# El resultado que devolvio la peticion es el nombre del archivo
                for r_name in selected_result:
                    print("r_name ", r_name)
                    print("r_name[0] ", r_name[0])
                    print("r_name[1] ", r_name[1])
                    results_name.append(r_name) #results.extend(r)  # Add matched documents to the shared list
                print("results in send_notification ", results_name)
            else:# El resultado que devolvio la peticion es el ranking de los posibles archivos
                for r_ranking in selected_result:
                    print("r_ranking ", r_ranking)
                    print("r_ranking[0] ", r_ranking[0])
                    print("r_ranking[1] ", r_ranking[1])
                    results_ranking.append(r_ranking)
        else: #REQUEST DOWNLOAD
            print("SENDIND REQUEST TO DOWNLOAD A FILE")
            print("selected_list[0] ", selected_list[0])
            print("selected_list[1] ", selected_list[1])
            results_name.append(selected_list)
        

def search_to_download(number: str): #ROXANA
    print("ENTRO EN SEARCH TO DOWNLOAD")
    print(number)
    threading_list = []
    results_files_download = [] # List with the ranking and query documents results
    for i, port in enumerate(ports_list): # Esta parte sera necesaria hacerla sincrona para recibir cada respuesta en paralelo y trabajar con varios hilos
        server = f'http://{clusters[0]}:{port}/api/download/{number}'
        t = threading.Thread(target=send_notification, args=(server, results_files_download, [], False), name="Hilo {}".format(i))
        threading_list.append(t)
        print("T.START")
        t.start()
        
    for t in threading_list:
        print("T.JOIN")
        t.join()

    print("results_files_download ", results_files_download)
    print("len(results_files_download)=", len(results_files_download))
    response = None
    for result in results_files_download:
        if type(result) != bool:
            response = copy.copy(result)
            break
    print("response ", response)
    return response


def search_by_text(text: str): #ROXANA
    print("ENTRO EN SEARCH BY TEXT")
    print(text)
    threading_list = []
    ranking = [] # List with the ranking and query documents results
    results = []  # Shared list to store the matched document names
    # Construir ranking a partir de cada listado de archivos recibidos gracias al tf_idf
    # Search text in every server
    # TODO: Paralelizar peticiones a todos los servidores para pedirles sus rankings. https://docs.python.org/es/3/library/multiprocessing.html
    for i, port in enumerate(ports_list): # Esta parte sera necesaria hacerla sincrona para recibir cada respuesta en paralelo y trabajar con varios hilos
        server = f'http://{clusters[0]}:{port}/api/files/search/{text}'
        t = threading.Thread(target=send_notification, args=(server, results_name, results_ranking), name="Hilo {}".format(i))
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

def decorate_data(results): #ROXANA
    print("ENTRO A DECORATE DATA")
    final_string = {}
    for i, elem in enumerate(results):
        key = f'data_{i}'
        final_string[key] = {'name': elem, 'url': 'https://localhost:3000'}
    return final_string

def match_by_name(text:str, datab): #ROXANA
    print("ENTRO EN MATCH BY NAME")
    print("Hilo en ejecución: {}".format(threading.current_thread().native_id))
    #select_files_title = f"SELECT Title FROM File WHERE File.Title = '{text}'"
    select_files_author = f"SELECT Author FROM File WHERE File.Author = '{text}'"
    #result_1 = datab.execute_read_query(select_files_title)
    result_2 = datab.execute_read_query(select_files_author)
    #print("RESULTADO TITLE",result_1)
    print("RESULTADO AUTHOR",result_2)
    return result_2 #,result_1

    return result
    # pass # Paula
###################


def check_database(number):
    query = f"SELECT ID FROM File WHERE File.ID = '{number}'"
    result_ID = database.execute_read_query(query)
    return result_ID

# Este metodo carga la base de datos del server al ser levantado este
# Asumo que conozco los IPs de cada servidor y la cantidad de servidores 
#def init_servers(datab): #ROXANA
#    print("INIT SERVERS")
#    print("len(servers_list ", len(servers_list))
#    for i, s in enumerate(sorted(servers_list)):
#        print("index ", i)
#        print(f"s == server_ip: {s}=={server_ip}")
#        if s == server_ip:
#            files_list = assign_documents(i)
#            print("files_list ", files_list)
#            print("PATH_TXTS ", PATH_TXTS)
#            text_list = convert_text_to_text_class(PATH_TXTS,files_list)
#            #A cada servidor le toca un archivo.db que se asigna en dependencia de su puerto
#            print(DATABASE_DIR + "/"+ database_files[change_db])
#            datab.create_connection(DATABASE_DIR + "/"+ database_files[change_db]) #MODIFICAR CAMBIAR ITERACION
#            for file in text_list:
#                datab.insert_file(file)
#
#            ######### SRI #########
#            vec_mod.doc_terms_data(text_list) # se le pasa la lista de archivos que se le pasa a la base de datos de ese server
#                                              # aqui empieza a calc os tf idf
#            # print(vec_mod.doc_terms)
#            #######################
#
#    # node.run() #CARLOS
#    print("Node Run")
#    # t1 = threading.Thread(target=node.run)
#    t2 = threading.Thread(target=chord_replication_routine)
#
#    # t1.start()
#    t2.start()
#
#    print("SALIO DEL INIT")
    
#asignar los documentos a cada server segun el orden en la lista
def assign_documents(start, end, datab): #ROXANA
    print("ENTRO AL assign_documents")
    docs_to_add = []
    #toma los documentos desde el ultimo ID de server hasta el propio ID del nuevo server incluyendolo
    for  i in range(start,end):
        docs_to_add.append(f"document_{i}.txt")

    print("docs_to_add = ", docs_to_add)
    text_list = convert_text_to_text_class(PATH_TXTS,docs_to_add)
    #A cada servidor le toca un archivo.db que se asigna en dependencia de su puerto
    print(DATABASE_DIR + "/"+ database_files[change_db])
    datab.create_connection(DATABASE_DIR + "/"+ database_files[change_db]) #MODIFICAR CAMBIAR ITERACION
    for file in text_list:
        datab.insert_file(file)
    
    ######### SRI #########
    vec_mod.doc_terms_data(text_list) # se le pasa la lista de archivos que se le pasa a la base de datos de ese server
                                      # aqui empieza a calc os tf idf
    # print(vec_mod.doc_terms)
    #######################

    # node.run() #CARLOS
    print("Node Run")
    # t1 = threading.Thread(target=node.run)
    t2 = threading.Thread(target=chord_replication_routine)

    # t1.start()
    t2.start()
    print("SALIO DEL assign_documents")

#En la lista de servers_list inicialmente esta vacia y a medida que se conectan en la red los nuevos servers
# es q se agregan a la lista y se le asignan nuevos documentos.Para esto se tiene en cuenta el ID de los
# documentos y el ID de los servers.
def init_servers(datab):
    print("ENTRO A init_servers")
    miembros = node.chan.osmembers
    n = len(miembros.keys())
    print(miembros)
    newserver_id = int(list(miembros.keys())[n - 1])
    print("newserver_id = ", newserver_id)
    miembros = sorted(miembros.items()) #para ordenar los servers por ID
    
    print("miembros sorted ", miembros)
    #Actualizo las listas del nuevo nodo
    for i in range(n):
        print("key = ", miembros[i][0])
        if int(miembros[i][0]) == newserver_id: #Solo entra 1 vez
            start = 1
            if i > 0: 
                start = miembros[i - 1][0] + 1
                print("prev id = ", start)
            # Annadir a la BD del nuevo server los docs que le tocan
            assign_documents(start,newserver_id + 1, datab)
            # Quitar a la BD del sucesor del nuevo server los docs que le tocan al nuevo a traves de un endpoint
            if i < n - 1:
                succ_ip = miembros[i + 1][1].ip
                succ_port = miembros[i + 1][1].port
                server_str = f'http://{succ_ip}:{succ_port}/api/remove_doc/{start}_{newserver_id + 1}'
                requests.get(server_str, verify=False)

        servers_ID_list.append(int(miembros[i][0]))
        servers_IP_list.append(miembros[i][1].ip) 
        ports_list.append(miembros[i][1].port) #  my_port
        print("servers_ID_list ", servers_ID_list)
        print("servers_IP_list ", servers_IP_list)
        print("ports_list ", ports_list)

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
    matched_documents = match_by_name(text, database)
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

@app.delete('/api/remove_doc/{prev_id}_{newserver_id}') # ROXANA
def remove_doc_api(prev_id:int, newserver_id:int):
    print("ENTRO A REMOVE DOC API")
    for i in range(prev_id, newserver_id):
        print("remove doc = ", {i})
        database.remove_file(i)
    


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
        stopped = Tru

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
print("EMPEZAMOS")
init_servers(database)
#redistribute_data(database)