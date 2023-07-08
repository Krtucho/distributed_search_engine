from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List
from math import floor
import copy

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
#############

import datetime

# Logs
from logs.logs_format import *

from servers import *

# Variable para decir si es esta corriendo en local o en docker
local = True

try:
    local=bool(os.environ.get("LOCAL"))
except:
    local = True
#LO PONGO MANUAL
local = True
# Docker
gateway = "172.21.0.1"

# Api Servers
servers:List[Address] = get_servers(local)

# servers = ['localhost']

# Clusters of n servers. Update when a new server joins
clusters = ['127.0.0.1']

# Chord
first_server_address_ip = '127.0.0.1' # Correrlo local
first_server_address_port = 10000  # Correrlo local

if not local:
    first_server_address_ip = str(os.environ.get('FIRST_SERVER')) #servers[0].ip if len(servers) > 0 else 'localhost' # Correrlo local
    first_server_address_port = 8000  # Correrlo local

# Chord Thread
stopped = False

server = '127.0.0.1'
port = 10002 # Correrlo local

if not local:
    server = str(os.environ.get('IP')) # Correrlo con Docker
    port = int(os.environ.get('PORT')) # Correrlo con Docker

print("ROXANA SERVER = ", server)
print("ROXANA PORT = ", port)

TIMEOUT = 20
if not local:
    try:
        TIMEOUT = int(os.environ.get('TIMEOUT')) # Correrlo con Docker
    except:
        pass

# Files
filepath = "/txts/"
if not local:
    try:
        filepath = str(os.environ.get('FILEPATH')) # Correrlo con Docker
    except:
        pass

# Default Leader Port
DEFAULT_LEADER_PORT = 8000
if not local:
    try:
        DEFAULT_LEADER_PORT = str(os.environ.get('DEFAULT_LEADER_PORT'))
    except:
        pass

app = FastAPI()

#ROXANA
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PATH_TXTS = os.path.join(CURRENT_DIR, "txts")
DATABASE_DIR = os.path.join(CURRENT_DIR, "databases")
lock = threading.Lock()
database = DataB()
ports_list = [] #LISTA DE PUERTOS DE CADA NUEVO SERVIDOR DE LA RED
servers_ID_list = [] # NECESITO SABER EL TOTAL DE SERVIDORES DE LA RED y su ID
servers_IP_list = [] # con su IP
name_db = ''

############ SRI ############
vec_mod = VectorModel()
#############################

# Configuración de CORS
origins = [
    "http://127.0.0.1",
    "http://127.0.0.1:8080",
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


# Si notification_type = True  => Se refiere a buscar archivos por su nombre o ranking
# Si notification_type = False  => Se refiere a devolver archivos para download
def send_notification(server:str, results_name, results_ranking, notification_type = True): #ROXANA
    with lock:
        print("ENTRO EN SEND NOTIFICATION")
        print("Hilo en ejecución: {}".format(threading.current_thread().name))
        print("clusters[0] = ",clusters[0])
        print("server = ", server)
        result = requests.get(server, verify=False)
         
        print("\R:")
        print("result ",result)
        print("result.content ",result.content)
        print("result.text ",result.text)
        print("result.text[0] ",result.text[0])
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
    results_ranking = [] # List with the ranking and query documents results
    results_name = []  # Shared list to store the matched document names
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
    
    print("search_by_text results_name ",results_name)
    print("search_by_text results_ranking ",results_ranking)
    # Make Ranking 
    # Luego de esperar cierta cantidad de segundos por los rankings pasamos a hacer un ranking general de todo lo q nos llego
    # TODO: Si alguna pc se demora mucho en devolver el ranking, pasamos a preguntarle a algun intregrante de su cluster que es lo que sucede
    
    # Return Response
    # Retornamos el ranking general de todos los rankings combinados
    results_name_str = decorate_data(results_name)
    results_ranking_str = decorate_data(results_ranking)

    return results_name_str, results_ranking_str

def decorate_data(results): #ROXANA
    print("ENTRO A DECORATE DATA")
    print("results ", results)
    final_string = {}
    for i, elem in enumerate(results):
        print("*final_string ", final_string)
        print(f"i={i}, elem= {elem}")
        print("elem[0] ", elem[0])
        print("elem[1] ", elem[1])
        final_string[f"id_{i}"] = elem[0]
        final_string[f"name_{i}"] = elem[1]
        # final_string[f"url__{i}"] = 'https://localhost:3000'
        final_string[f"url_{i}"] = f'https://{server}:{port}'
    print("final string ", final_string)
    return final_string


def decorate_data_rank(ranking: list): 
    print("ENTRO A DECORATE DATA")
    print("results ", ranking)
    final_string = {}
    for i, elem in enumerate(ranking):
        print(f"i={i}, elem= {elem}")
        final_string[f"id__{i}"] = elem[0]
        final_string[f"similarity__{i}"] = elem[1]
        # final_string[f"url__{i}"] = 'https://localhost:3000'
        final_string[f"url_{i}"] = f'https://{server}:{port}'
    print("final string ", final_string)
    return final_string


def match_by_name(text:str): #ROXANA
    print("ENTRO EN MATCH BY NAME")
    print("Hilo en ejecución: {}".format(threading.current_thread().native_id))
    #select_files_title = f"SELECT Title FROM File WHERE File.Title = '{text}'"
    select_files_author = f"SELECT ID, Title FROM File WHERE File.Author = '{text}'"
    select_all_authors = f"SELECT ID, Author FROM File"
    select_all_titles = f"SELECT ID, Title FROM File"
    result_1 = database.execute_read_query(select_files_author)
    result_2 = []
    result_3 = database.execute_read_query(select_all_authors)
    result_4 = database.execute_read_query(select_all_titles)
    print("result_4 ", result_4)
    if len(result_4) > 0:
        for index, t in enumerate(result_4):
            if text in t[1]:
                result_2.append(t)
            print("result[0]",t[0])
            print("result[1]",t[1])
            print()

    print("RESULTADO ALL AUTHORS",result_3)
    print("RESULTADO por AUTHOR, Title",result_1)
    print("RESULTADO ALL Titles",result_4)
    print("RESULTADO TITULOS SELECCIONADOS ", result_2)
    return result_1 + result_2 


####### SRI #######
def tf_idf(textt: str):
    # http://localhost:10000/files/search/brenckman,m.
    print("---------------Entro en tf_idf")
    ranking = vec_mod.run(textt)
    result = []
    
    print("---------------------")
    print("ranking", ranking)
    print("-------------")

    for id, rank in ranking: #new_rank no esta definido. PONGO MOMENTANEAMENTE ranking
        db_query = f"SELECT ID, Title FROM File WHERE File.ID = '{str(id)}'"
        for i in database.execute_read_query(db_query):
            print("***** ", i)
            result.append(i)
    
    print("---------------------")
    print("result", result)
    print("-------------")

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
def assign_documents(start, end, datab, name_db): #ROXANA
    print("ENTRO AL assign_documents")
    docs_to_add = []
    #toma los documentos desde el ultimo ID de server hasta el propio ID del nuevo server incluyendolo
    for  i in range(start,end):
        docs_to_add.append(f"document_{i}.txt")

    print("docs_to_add = ", docs_to_add)
    text_list = convert_text_to_text_class(PATH_TXTS,docs_to_add)
    #A cada servidor le toca un archivo.db que se asigna en dependencia de su puerto
    print("DATABASE_DIR ", DATABASE_DIR + "/"+ name_db)
    datab.create_connection(DATABASE_DIR + "/"+ name_db) #MODIFICAR CAMBIAR ITERACION
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
def init_servers(datab, name_db):
    print("ENTRO A init_servers")
    miembros = node.chan.osmembers
    n = len(miembros.keys())
    print("miembros = ", miembros)
    print("n = ", n)
    newserver_id = int(list(miembros.keys())[n - 1])
    
    print("newserver_id = ", newserver_id)
    name_db = f'db_{newserver_id}.db'
    print("name_db = ", name_db)
    new_members = []
    for m in miembros.items():
        m = (int(m[0]), m[1])
        new_members.append(m)
    print("miembros casteados a entero ", new_members)
    new_members = sorted(new_members) #para ordenar los servers por ID
    
    print("miembros sorted ", new_members)
    #Actualizo las listas del nuevo nodo
    for i in range(n):
        print("key = ", new_members[i][0])
        print("int(miembros[i][0]) == newserver_id = ", int(new_members[i][0]) == newserver_id)
        if int(new_members[i][0]) == newserver_id: #Solo entra 1 vez
            start = 1
            if i > 0:
                start = int(new_members[i - 1][0]) + 1
                print("prev id = ", start)
            # Annadir a la BD del nuevo server los docs que le tocan
            assign_documents(start,newserver_id + 1, datab, name_db)
            # Quitar a la BD del sucesor del nuevo server los docs que le tocan al nuevo a traves de un endpoint
            print("i <= n - 2 = ", i <= n - 2)
            if i <= n - 2:
                rango = f'{start}_{newserver_id + 1}'
                succ_ip = new_members[i + 1][1]['ip']
                succ_port = new_members[i + 1][1]['port']
                print(f"ENTRO A SUCESOR = {succ_ip}:{succ_port}")
                server_str = f'http://{succ_ip}:{succ_port}/api/remove_doc/{rango}'
                requests.delete(server_str, verify=False)

        new_id = int(new_members[i][0])
        if n == 1:
            new_ip = new_members[i][1].ip
            new_port = new_members[i][1].port
        else:
            new_ip = new_members[i][1]['ip']
            new_port = new_members[i][1]['port']

        print("new_members[i] = ", new_members[i])
        print("new_id = ", new_id)
        print("new_ip = ", new_ip)
        print("new_port = ", new_port)
        
        servers_ID_list.append(new_id)
        servers_IP_list.append(new_ip) 
        ports_list.append(new_port)

        print("servers_ID_list ", servers_ID_list)
        print("servers_IP_list ", servers_IP_list)
        print("ports_list ", ports_list)

    # coord
    t3 = threading.Thread(target=check_alive)
    t3.start()

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

class FilesModel(BaseModel):
    node_id:int
    ip:str
    port:int
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
    return search_by_text(text)#{"data": id} #DUDA ESPERAR A RESPUESTA DE CARLOS EN EL GRUPO

# Server
# Este es el que llama al TF-IDF
@app.get('/api/files/search/{text}') 
def search_file_in_db(text: str): #ROXANA
    print("----------------------ENTRO A SEARCH FILE IN DB")
    print("Hilo en ejecución: {}".format(threading.current_thread().name))
    #datab = DataB() #crear una nueva database en cada hilo
    #init_servers(datab)
    matched_documents = match_by_name(text)
    print("matched documents ", matched_documents)
    if matched_documents == []:
        #Calcularel tf_idf #{"data": id}
        return [tf_idf(text),False] #El booleano: PARA SABER SI LO QUE DEVUELVE EL METODO ES QUE MATCHEO CON NOMBRE O CON EL RANKING
    else:
        return [matched_documents, True]


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
                            Address(server, port),
                            default_leader_port = DEFAULT_LEADER_PORT)
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
        print_debug("Inside Join Endpoint: " + str(nodeID))
        print_info(node.nodeID)
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

@app.delete('/api/remove_doc/{rango}') # ROXANA
def remove_doc_api(rango:str):
    print("ENTRO A REMOVE DOC API")
    pos = rango.find('_')
    print("pos = ", pos)
    prev_id = int(rango[:pos])
    print("prev_id = ", prev_id)
    newserver_id = int(rango[pos + 1:])
    print("newserver_id = ", newserver_id)
    for i in range(prev_id, newserver_id):
        print("remove doc = ", i)
        database.remove_file(i)
    
    check_files = f"SELECT ID FROM File"
    result = database.execute_read_query(check_files)
    print("result check_files = ", result)
    
# Leader
@app.get('/chord/channel/leader')
def is_leader():
    return {"is_leader":node.is_leader, "node_ide":node.nodeID}

@app.get('/chord/channel/get_leader')
def get_leader():
    leader_ip = None
    leader_port = None
    actual_leader = node.leader
    if actual_leader:
        leader_ip = actual_leader.ip
        leader_port = actual_leader.port

    return {"is_leader":node.is_leader, "node_ide":node.nodeID, "leader_ip":leader_ip, "leader_port":leader_port}


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
                # print("Inside Verifying Data Replication")
                text = bool(r.json())
                # print(text)
                # print(r.text)
                # print(r.content)
                # print(r.json())
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
                    print_debug("Predecessors" + str(node.predecessor))
                    node.restart_pred_data_info(node.predecessor[0])
            # else:
                # Si aun no se tiene predecesor, esperamos a que el venga a buscarnos

            # TODO: Agregar rutina de FixFinger para que se ejecute a cada rato
            node.recomputeFingerTable() #-
            print("FT", node.FT)
            # print('FT[','%04d'%node.nodeID,']: ',['%04d' % k for k in node.FT]) #- 

            print_info(node)

            # Reccess
            print(f"On Thread...Sleeping for {TIMEOUT} seconds")
            time.sleep(TIMEOUT)
    except KeyboardInterrupt as e:
        print("Stopping Chord Routine Thread...")
        stopped = True

def check_alive():
    stopped = False
    try:
        while not stopped:
            if node.is_leader and datetime.datetime.now().time().minute/5 == 0:
                # print(node.clock)
                print("-------------------------------Check alive-----------------------------")
                node.check_live_nodes()
                # time.sleep(10)
    except KeyboardInterrupt as e:
        stopped = True


# Uploading Files
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from os import getcwd, remove
from shutil import rmtree

router = APIRouter()


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    with open(getcwd() + "/txts" + file.filename, "wb") as myfile:
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
    file_name = "document_" +number +".txt"
    response = find_download(number) # VA A BUSCAR SI EL CURRENT SERVER TIENE EL ARCHIVO
    print("type(response) = ",type(response))
    print("type(response) == bool ", type(response) == bool)
    if type(response) == bool: #SI NO SE ENCONTRO EL ARCHIVO
        response = search_to_download(number) # SE LO PIDE A LOS DEMAS SERVERS
        if response is None:
            response = {"error": f"File '{file_name}' not found in the database."}
    
    print("response in download_file ", response)
    
    file_response = FileResponse(response[0], media_type="application/octet-stream", filename=response[1])
    print("type(file_response) ", type(file_response))
    return file_response 

def find_download(number:str):
    print("ENTRO EN FIND DOWNLOAD")
    print("number ", number)
    file_name = "document_" +number +".txt"
    file_path = Path(os.path.join(PATH_TXTS,file_name))

    print("file_path ", file_path)
    if not file_path.exists(): #Comprueba si el archivo existe en la carpeta txts
        return {"error": f"File '{file_name}' not found in the folder."}
    
    #Comprobar si el archivo esta en la base de datos del servidor
    result_ID = check_database(number)
    print("len(result_ID)=",len(result_ID))
    if len(result_ID) > 0:
        response = [file_path,file_name]
    else:
        response = False
    print("response en FIND DOWNLOAD ", response)
    return response


# Server
@router.get("/api/download/{number}")
def download_file_api(number: str):
    print("ENTRO EN API DOWNLOAD")
    return find_download(number)
    
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
init_servers(database, name_db)
#redistribute_data(database)