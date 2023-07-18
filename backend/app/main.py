from fastapi import FastAPI, Body
from pydantic import BaseModel
from typing import Optional, List
from math import floor
import copy
import json
import re
import requests # Para realizar peticiones a otros servers y descargar archivos

from file_handler import *
# from app.file_handler import *


from fastapi.middleware.cors import CORSMiddleware
from database import DataB, convert_str_to_text_class, Text
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

# Tipo de hash a utilizar
hash_type = "RANDOM"

try:
    if str(os.environ.get("LOCAL")) == "False":
        local=False
    print_debug(f"local: {local}")
except:
    local = True
#LO PONGO MANUAL
# local = True
# Docker
gateway = "172.21.0.1"

# Api Servers
servers:List[Address] = get_servers(local)

# servers = ['localhost']

# Clusters of n servers. Update when a new server joins
clusters = ['127.0.0.1']

# Chord
first_server_address_ip = '127.0.0.1' # Correrlo local   '172.20.10.2'
first_server_address_port = 10000  # Correrlo local

if not local:
    first_server_address_ip = str(os.environ.get('FIRST_SERVER')) #servers[0].ip if len(servers) > 0 else 'localhost' # Correrlo local
    first_server_address_port = 8000  # Correrlo local

# Chord Thread
stopped = False

server = '127.0.0.1'
port = 10002 # Correrlo local
# brenckman,m.   ting-yili
if not local:
    server = str(os.environ.get('IP')) # Correrlo con Docker
    port = int(os.environ.get('PORT')) # Correrlo con Docker

print("ROXANA SERVER = ", server)
print("ROXANA PORT = ", port)

TIMEOUT = 10
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
        if filepath == "None":
            filepath = "/txts/"
    except:
        pass

# Default Leader Port
DEFAULT_LEADER_PORT = 8000
if not local:
    try:
        DEFAULT_LEADER_PORT = int(os.environ.get('DEFAULT_LEADER_PORT'))
    except:
        pass

# Hash
if not local:
    try:
        hash_type = str(os.environ.get('HASH_TYPE'))
        print_debug(f"Hash type: {hash_type}")
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
    "http://172.17.0.1:8080",
    "http://172.17.0.2",
    "http://172.17.0.2:8080"
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
def send_notification(server:str, results_, notification_type = True): #ROXANA
    print("Notificatin type +++++++++++++++", notification_type)
    with lock:
        print("ENTRO EN SEND NOTIFICATION")
        print("Hilo en ejecución: {}".format(threading.current_thread().name))
        print(f"server = {node.node_address.ip}, PORT = {node.node_address.port}")
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
            # selected_name = selected_list[1] #ARREGLAR
            # selected_result = selected_list[0]
            # print("selected_name ", selected_name)
            # if selected_name:# El resultado que devolvio la peticion es el nombre del archivo
            for r_name in selected_list:
                print("r_name ", r_name)
                print("r_name[0] ", r_name[0])
                print("r_name[1] ", r_name[1])
                results_.append(r_name) #results.extend(r)  # Add matched documents to the shared list
            print("results in send_notification ", results_)
            # else:# El resultado que devolvio la peticion es el ranking de los posibles archivos
            #     for r_ranking in selected_result:
            #         print("r_ranking ", r_ranking)
            #         print("r_ranking[0] ", r_ranking[0])
            #         print("r_ranking[1] ", r_ranking[1])
            #         results_ranking.append(r_ranking)
        else: #REQUEST DOWNLOAD
            print("SENDIND REQUEST TO DOWNLOAD A FILE")
            print("selected_list[0] ", selected_list[0])
            print("selected_list[1] ", selected_list[1])
            results_.append(selected_list)
        

def search_to_download(number: str): #ROXANA
    print("ENTRO EN SEARCH TO DOWNLOAD")
    print(number)
    threading_list = []
    results_files_download = [] # List with the ranking and query documents results
    for i, member in enumerate(node.chan.osmembers.items()): # Esta parte sera necesaria hacerla sincrona para recibir cada respuesta en paralelo y trabajar con varios hilos
        print(f"MEMBER {member}")
        print(f"ESTOY EN EL LLAMADO DE LOS HILOS: IP = {member[1].ip}")
        print(f"server = {node.node_address.ip}")
        # if member[1].ip == node.node_address.ip:continue 
        if member[1].port == node.node_address.port:continue  # para correrlo local
        server = f'http://{member[1].ip}:{member[1].port}/api/download/{number}'
        t = threading.Thread(target=send_notification, args=(server, results_files_download, False), name="Hilo {}".format(i))
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
    results_ = []  # Shared list to store the matched document names and List with the ranking and query documents results
    # Construir ranking a partir de cada listado de archivos recibidos gracias al tf_idf
    # Search text in every server
    # TODO: Paralelizar peticiones a todos los servidores para pedirles sus rankings. https://docs.python.org/es/3/library/multiprocessing.html
    for i, member in enumerate(node.chan.osmembers.items()): # Esta parte sera necesaria hacerla sincrona para recibir cada respuesta en paralelo y trabajar con varios hilos
        print(f"MEMBER {member}")
        print(f"ESTOY EN EL LLAMADO DE LOS HILOS: IP = {member[1].ip}")
        print(f"server = {node.node_address.ip}, PORT = {node.node_address.port}")
        # Si se esta probando con docker o varias pcs la condicion del if es q no sea el mismo ip
        #if member[1].ip == node.node_address.ip:continue 
        # Si se esta probando local entonces la condicion del if es q no sea el mismo port
        if member[1].port == node.node_address.port:continue 
        server = f'http://{member[1].ip}:{member[1].port}/api/files/search/{text}'
        t = threading.Thread(target=send_notification, args=(server, results_), name="Hilo {}".format(i))
        threading_list.append(t)
        print("T.START")
        t.start()
        
    for t in threading_list:
        print("T.JOIN")
        t.join()
    
    print("search_by_text results_name ",results_)
    #print("search_by_text results_ranking ",results_ranking)
    # Make Ranking 
    # Luego de esperar cierta cantidad de segundos por los rankings pasamos a hacer un ranking general de todo lo q nos llego
    # TODO: Si alguna pc se demora mucho en devolver el ranking, pasamos a preguntarle a algun intregrante de su cluster que es lo que sucede
    
    # Return Response
    # Retornamos el ranking general de todos los rankings combinados
    
    print("@@@@@@@ results_ name AND ranking ", results_)

    #print("@@@@@@@ results_ranking ", results_ranking)

    unique_result = []
    for i in results_:
        if i not in unique_result:
            print(f"-------for i in results_: i = {i} ")
            unique_result.append(i)


    # for i in results_ranking:
    #     if i not in results_name:
    #         results_name.append(i)

    #results_name_str = decorate_data(results_name)
    results_name_str = decorate_data(unique_result)
    # results_ranking_str = decorate_data(results_ranking)

    print("@@@@@@@ results_name_str ", results_name_str)

    # print("@@@@@@@ results_ranking_str ", results_ranking_str)

    # result = results_name_str + results_ranking_str
    
    # return results_name_str, results_ranking_str

    # return result

    # for i in results_ranking_str:
    #     if i not in results_name_str:
    #         results_name_str.add(i)

    return results_name_str

def decorate_data(results): #ROXANA
    print("ENTRO A DECORATE DATA")
    print("results ", results)
    result = []
    # final_string = {}
    for i, elem in enumerate(results):
        final_string = {}
        print("*final_string ", final_string)
        print(f"i={i}, elem= {elem}")
        print("elem[0] ", elem[0])
        print("elem[1] ", elem[1])
        # final_string[f"id_{i}"] = elem[0]
        # final_string[f"name_{i}"] = elem[1]
        # # final_string[f"url__{i}"] = 'https://localhost:3000'
        # final_string[f"url_{i}"] = f'https://{server}:{port}'
        final_string[f"id"] = elem[0]
        final_string[f"name"] = elem[1]
        # final_string[f"url__{i}"] = 'https://localhost:3000'
        # final_string[f"url"] = f'https://{server}:{port}'
        final_string[f"url"] = f'http://{server}:{port}/download/{str(elem[0])}'
        result.append(final_string)
    # print("final string ", final_string)
    print("*********---------------------------------------", result)
    # return final_string
    return result


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

    print("-------------RESULTADO ALL AUTHORS",result_3)
    print("-------------RESULTADO por AUTHOR, Title",result_1)
    print("-------------RESULTADO ALL Titles",result_4)
    print("-------------RESULTADO TITULOS SELECCIONADOS ", result_2)
    return result_1 + result_2 


####### SRI #######
def tf_idf(textt: str):
    # http://localhost:10000/files/search/brenckman,m.
    # print("---------------Entro en tf_idf")
    ranking = vec_mod.run(textt)
    result = []
    
    # print("---------------------")
    # print("ranking", ranking)
    # print("-------------")

    for id, rank in ranking: #new_rank no esta definido. PONGO MOMENTANEAMENTE ranking
        print(" entro for del tf_idf ++++++++++++++++")
        db_query = f"SELECT ID, Title FROM File WHERE File.ID = '{str(id)}'"
        for i in database.execute_read_query(db_query):
            # print("***** ", i)
            result.append(i)
            # print()
            # print(result)
    
    # print("---------------------")
    # print("result", result)
    # print("-------------")

    return result
    # pass # Paula
###################


def check_database(number):
    query = f"SELECT ID FROM File WHERE File.ID = '{number}'"
    result_ID = database.execute_read_query(query)
    return result_ID
    
#asignar los documentos a cada server segun el orden en la lista
def assign_documents(start, end, datab, name_db): #ROXANA
    print("ENTRO AL assign_documents")
    docs_to_add = []
    #toma los documentos desde el ultimo ID de server hasta el propio ID del nuevo server incluyendolo
    for  i in range(start,end):
        docs_to_add.append(f"document_{i}.txt")

    print(f"docs_to_add en assign_documents = {docs_to_add},  len = {len(docs_to_add)}")
    # Annade los docs a la BD y calcula el SRI
    add_to_database(datab,name_db, docs_to_add, True) 

    #text_list = convert_str_to_text_class(PATH_TXTS,docs_to_add)
    ##A cada servidor le toca un archivo.db que se asigna en dependencia de su puerto
    #print("DATABASE_DIR ", DATABASE_DIR + "/"+ name_db)
    #datab.create_connection(DATABASE_DIR + "/"+ name_db) #MODIFICAR CAMBIAR ITERACION
    #for file in text_list:
    #    datab.insert_file(file)
    #
    ########## SRI #########
    #vec_mod.doc_terms_data(text_list) # se le pasa la lista de archivos que se le pasa a la base de datos de ese server
                                      # aqui empieza a calc os tf idf
    # print(vec_mod.doc_terms)
    #######################

    node.update_server_files(docs_to_add, [])
    # node.run() #CARLOS
    # print("Node Run")
    # # t1 = threading.Thread(target=node.run)
    # t2 = threading.Thread(target=chord_replication_routine)

    # # t1.start()
    # t2.start()
    # print("SALIO DEL assign_documents")

#En la lista de servers_list inicialmente esta vacia y a medida que se conectan en la red los nuevos servers
# es q se agregan a la lista y se le asignan nuevos documentos.Para esto se tiene en cuenta el ID de los
# documentos y el ID de los servers.
def init_servers(datab, name_db):
    print("ENTRO A init_servers")
    miembros = node.chan.osmembers
    print(f"GET MEMBERS = {node.get_members()}")
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
            print(f"----------i = {i}")
            print(f"----------n - 2 = {n -2}")
            if i <= n - 2:
                rango = f'{start}_{newserver_id + 1}'
                succ_ip = new_members[i + 1][1]['ip']
                succ_port = new_members[i + 1][1]['port']
                print(f"ENTRO A SUCESOR = {succ_ip}:{succ_port}")
                server_str = f'http://{succ_ip}:{succ_port}/api/remove_doc/{rango}'
                requests.delete(server_str, verify=False)

        new_id = int(new_members[i][0])
        try:
        # if n == 1:
            new_ip = new_members[i][1].ip
            new_port = new_members[i][1].port
        except:
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


    #REPLICAR LOS DOCS DEL PREV 
    print("Node Run")
    t2 = threading.Thread(target=chord_replication_routine)
    t2.start()

    # coord
    t3 = threading.Thread(target=check_alive)
    t3.start()

    print("SALIO DEL INIT")

def delete_db(directory, file_name):
    file_path = os.path.join(directory, file_name)
    if os.path.exists(file_path):
        os.remove(file_path)
        print("El archivo se ha eliminado exitosamente.")
    else:
        print("El archivo no existe.")

def add_to_database(datab, name_db, files: List[str], vec_mod_cond:bool):
    text_list = convert_str_to_text_class(PATH_TXTS,files)
    #A cada servidor le toca un archivo.db que se asigna en dependencia de su puerto
    print("DATABASE_DIR ", DATABASE_DIR + "/"+ name_db)
    if name_db != "":
        delete_db(DATABASE_DIR, name_db)
        datab.create_connection(DATABASE_DIR + "/"+ name_db) #MODIFICAR CAMBIAR ITERACION
    
    for file in text_list:
        datab.insert_file(file)
    
    if vec_mod_cond:
        ######### SRI #########
        vec_mod.doc_terms_data(text_list) # se le pasa la lista de archivos que se le pasa a la base de datos de ese server
                                          # aqui empieza a calc os tf idf
        # print(vec_mod.doc_terms)
        #######################

def replication_files1(next_address):
    print(f"-------ENTRO EN replication_files 1")
    current_id = node.nodeID
    print(f" current_id = {current_id}")
    prev_adr = node.chan.get_member(node.get_predecessor())
    print(f"!!!!!!!!!!!!!!!!!!!prev = {prev_adr}")

    # 1- Actualizar el node.replay del succ del succ, ahora son los nuevos docs.
    print("----------------------------------PASO 1")
    # LLamar al succ y q este llame a su succ y actualice su node.replay
    try:
        print("1-")
        url = f'http://{next_address["ip"]}:{next_address["port"]}/api/update_succ_data'
    except:
        print("2-")
        url = f'http://{next_address.ip}:{next_address.port}/api/update_succ_data'

    print(f"url = {url}")
    response_data_node_succ = requests.get(url, verify=False)
    if response_data_node_succ.status_code == 200:
        print('Elementos replicados exitosamente')
    else:
        print('Error al replicar elementos')
    
    # 2- Actualizar el node.replay del succ, en vez de ser la data del node prev 
    # ahora sera la data del current node.
    print("----------------------------------PASO 2")
    try:
        print("1-")
        url = f'http://{next_address["ip"]}:{next_address["port"]}/api/update_replay_data'
    except:
        print("2-")
        url = f'http://{next_address.ip}:{next_address.port}/api/update_replay_data'

    separated_data = get_separated_data()
    print(f"separated_data[0] = {separated_data[0]}")
    current_data = list(separated_data[0].values())[0]
    print(f"current_data[0] = {current_data}")
    doc = "".join(current_data)
    
    print(f"url = {url}")
    url += f'/{doc}'
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        print('Elementos replicados exitosamente')
    else:
        print('Error al replicar elementos')

    # 3- Actualizar el node.replay del current node, seran los docs de prev node
    print("----------------------------------PASO 3")
    try:
        print("1-")
        url = f'http://{prev_adr["ip"]}:{prev_adr["port"]}/api/get_actual_data'
    except:
        print("2-")
        url = f'http://{prev_adr.ip}:{prev_adr.port}/api/get_actual_data'

    print(f"url = {url}")
    # obtener los doc del node preview
    response_data_prev = requests.get(url, verify=False) 
    if response_data_prev.status_code == 200:
        print('Elementos replicados exitosamente')
    else:
        print('Error al replicar elementos')
    
    print("!!!! TERMINO EL replication_files !!!!")

# Se cayo el nodo siguiente a mi o detras de mi
# Si next_node = True => se cayo el nodo siguiente a mi
# Si next_node = False => se cayo el nodo detras de mi
def replication_files2(next_address):
    print(f"-------ENTRO EN replication_files 2")
    print("-----------------next address ", next_address)

    if len(node.get_members()) == 1: #ES el unico nodo que queda
        
        new_data_combined = list(node.data.values())[0]
        print(f"list(node.data.values())[0] = {new_data_combined}, len = {len(new_data_combined)}")
        replay_list = list(node.replay.values())[0]
        print(f"replay_list = {replay_list}, len = {len(replay_list)}")
        new_data_combined.extend(replay_list)
        print(f"new_data_combined = {new_data_combined}, len = {len(new_data_combined)}")

        node.update_server_files(new_data_combined, [])
    else:
        try:
            print("1-")
            url = f'http://{next_address["ip"]}:{next_address["port"]}/api/update_all_data'
        except:
            print("2-")
            url = f'http://{next_address.ip}:{next_address.port}/api/update_all_data'
        
        print(f"(((((((((((((( url = {url}")
        separated_data = get_separated_data()
        print(f"separated_data[0] = {separated_data[0]}")
        current_data = list(separated_data[0].values())[0]
        print(f"current_data[0] = {current_data}")
        doc = "".join(current_data)
        
        url += f'/{doc}'
        print("-------------- url de replication files 2 ---------------- ", url)
        response = requests.get(url, verify=False) #AQUI HUBO ERROR, múltiples intentos de conexión y todos ellos fallaron. 
        print("/////////////////////////, ", response)
        
        if response.status_code == 200:
            print('Elementos replicados exitosamente')
        else:
            print('Error al replicar elementos')
        
        print("SEGUNDA PARTE")
        try:
            print("1-")
            url = f'http://{next_address["ip"]}:{next_address["port"]}/api/update_succ_data'
        except:
            print("2-")
            url = f'http://{next_address.ip}:{next_address.port}/api/update_succ_data'
        
        print(f"url = {url}")
        response_data_node_succ = requests.get(url, verify=False)
        if response_data_node_succ.status_code == 200:
            print('Elementos replicados exitosamente')
        else:
            print('Error al replicar elementos')
  

@app.get('/api/update_all_data/{doc}')
def update_all_data (doc:str):
    # node.data = node.data.extend(node.replay)
    # for item in node.replay:
    #     node.data 
    print("node data *************",  node.data)
    print()
    print("node replay *************",  node.replay)
    print()
    node.data.update(node.replay)
    print("node data *************",  node.data)
    print()
    update_replay_data(doc)

# Actualiza en el sucesor de mi sucesor el data.replay
@app.get('/api/update_succ_data')
def api_update_succ_data():
    print("ENTRO A api_update_succ_data")
    succ_adr = node.chan.get_member(node.get_succesor())

    separated_data = get_separated_data()
    print(f"separated_data[0] = {separated_data[0]}")
    current_data = list(separated_data[0].values())[0]
    print(f"current_data = {current_data}, len = {len(current_data)}")
    print()
    print(f"separated_data[1] = {separated_data[1]}")
    current_replay = list(separated_data[1].values())[0]
    print(f"current_replay = {current_replay}, len = {len(current_replay)}")
    try:
        print("1-")
        url = f'http://{succ_adr["ip"]}:{succ_adr["port"]}/api/update_replay_data'
    except:
        print("2-")
        url = f'http://{succ_adr.ip}:{succ_adr.port}/api/update_replay_data'

    print(f"utl = {url}")
    doc = "".join(current_data)
    url += f'/{doc}'
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        print('Elementos replicados exitosamente')
    else:
        print('Error al replicar elementos')
    print("SALIO DEL api_update_succ_data")

@app.get('/api/update_replay_data/{doc}')
def api_update_replay_data(doc:str):
    print(f"--------------ENTRO EN api/api_update_replay_data")
    return update_replay_data(doc)

def update_replay_data(doc:str):
    print(f"--------------ENTRO EN update_replay_data")
    indices = get_indexes(doc)
    new_replay = []
    for i in indices:
        temp = f"document_{i}.txt"
        new_replay.append(temp)
    
    print(f"node.data antes de hacer sorted = {node.data}")
    print()
    print(f"node.replay antes de hacer sorted = {node.replay}")
    data_list = list(node.data.values())[0]
    node.update_server_files(data_list, new_replay)
    # AGREGAR A LA BD los archivos de la nueva replica!
    add_to_database(database,"", new_replay, True)
    print(f"NUEVOS DATOS REPLICADOS = {new_replay}, len = {len(new_replay)}")

# def get_prev_adr(prev_id):
#     print("-----------ENTRO A get_prev_adr")
#     print(f"prev_id = {prev_id}")
#     miembros = node.get_members()
#     print(f"miembros = {miembros}")
#     for n in node.chan.osmembers.items():
#         print(f"node in osmembers is {n}")
#         print(f"n[0] == str(prev_id)  = {n[0] == str(prev_id)}")
#         if n[0] == str(prev_id):
#             result = n[1]
#             print(f"result = {result}")
#             return result
#     print(f"result = {result}")
#     return result

# @app.get('/api/replication_docs/{doc}')
# def replication_docs(doc: str):
#     print(f"--------------ENTRO EN api/replication_docs")
#     indices = get_indexes(doc)
#     for data in indices:
#         database.insert_file(data)
#     actual_docs = get_all_data()
#     print(f"actual_docs = {actual_docs}")
#     node.update_server_files(actual_docs)
#     return True

# @app.delete('/api/delete_prev_doc/{doc}')
# def delete_prev_doc(doc:str):
#     print(f"--------------ENTRO EN api/delete_prev_doc")
#     indices = get_indexes(doc)
#     for i in indices:
#         database.remove_file(i)
    
#     actual_docs = get_all_data()
#     node.update_server_files(actual_docs)
#     print(f"Documentos eliminados: {indices}")
#     print(f"Documentos restantes en la base de datos: {actual_docs}")

#     return {'deleted_docs': indices, 'remaining_docs': list(actual_docs)}
    
def get_indexes(doc:str):
    pattern = r"document_(\d+)\.txt" 
    matches = re.finditer(pattern, doc)
    indices = [int(match.group(1)) for match in matches]
    return indices

# @app.get('/api/replication/{rango}') # ROXANA
# def api_replication(rango:str):
#     print(f"-------------ENTRO EN API REPLICATION")
#     print(f"RANGO = {rango}")
#     new_docs_replicated = []
#     pos = rango.find('_')
#     print("pos = ", pos)
#     prev_id = int(rango[:pos])
#     print("prev_id = ", prev_id)
#     newserver_id = int(rango[pos + 1:])
#     print("newserver_id = ", newserver_id)
    
#     for  i in range(prev_id,newserver_id):
#         new_docs_replicated.append(f"document_{i}.txt")

#     print(f"new_docs_replicated = {new_docs_replicated}, len = {len(new_docs_replicated)}")
#     text_list = convert_str_to_text_class(PATH_TXTS,new_docs_replicated)

#     for file in text_list:
#         database.insert_file(file)
    
#     check_files = f"SELECT ID FROM File"
#     result = database.execute_read_query(check_files)
#     docs_to_add = []
#     for i in result:
#         doc = f"document_{i[0]}.txt"
#         docs_to_add.append(doc)
        
#     print(check_files)
#     print(f"documentos actuales en API REPLICATION = {docs_to_add}, len = {len(docs_to_add)}")
#     node.update_server_files(docs_to_add)

@app.get('/api/get_actual_data') # ROXANA
def api_get_actual_data():
    print("----------ENTRO EN api_get_actual_data")
    get_separated_data()

def get_all_data():
    print(f"-------------ENTRO EN get_all_data")
    check_files = f"SELECT ID FROM File"
    result = database.execute_read_query(check_files)
    docs_to_add = []
    for i in result:
        doc = f"document_{i[0]}.txt"
        docs_to_add.append(doc)
    
    print(f"actuals docs = {docs_to_add}, len = {len(docs_to_add)}")
    return docs_to_add

def get_separated_data():
    print("----------ENTRO EN get_separated_data")
    return [node.data, node.replay]

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
    print("-------------ENTRO EN SHOW FILE")
    print_debug(f"Searching Text... {text}")
    #buscar en el propio server primero
    response_me = decorate_data(find_in_myself(text))
    print(f"response_me = {response_me}")
    response_others =  search_by_text(text)#{"data": id} #DUDA ESPERAR A RESPUESTA DE CARLOS EN EL GRUPO
    print(f"response_others = {response_others}")
    response = unique(response_me, response_others)
    #response_me.extend(response_others)
    print(f"response_me unido con response_others = {response}")
    return response

def unique(response_me, response_others):
    print("--------------ENTRO EN UNIQUE")
    result = copy.copy(response_me)

    for elem in response_others:
        print(f"elem = {elem}")
        print(f"elem not in result = {elem not in result}")
        if elem not in result:
            result.append(elem)

    print(f" result = {result}")
    return result

def find_in_myself(text):
    print("----------------------ENTRO A find_in_myself")
    print("Hilo en ejecución: {}".format(threading.current_thread().name))
    matched_documents = match_by_name(text)
    print("!!!! find_in_myself !!! matched documents ", matched_documents)
    matched_rank = tf_idf(text)
    print("!!!! find_in_myself !!! matched rank", matched_rank)

    for i in matched_rank:
        if i not in matched_documents:
            matched_documents.append(i)

    # matched_documents = matched_documents + matched_rank

    # if matched_documents == []:
    #     #Calcularel tf_idf #{"data": id}
    #     return [matched_rank,False] #El booleano: PARA SABER SI LO QUE DEVUELVE EL METODO ES QUE MATCHEO CON NOMBRE O CON EL RANKING
    # else:
    #     return [matched_documents, True]

    print("!!!----find_in_myself---!!!! final matched documents ", matched_documents)

    #result = decorate_data(matched_documents)
    return matched_documents #[matched_documents, True]
    #return result
    
# Server
# Este es el que llama al TF-IDF
@app.get('/api/files/search/{text}') 
def search_file_in_db(text: str): #ROXANA
    print("----------------------ENTRO A SEARCH FILE IN DB")
    return find_in_myself(text)


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
                            default_leader_port = DEFAULT_LEADER_PORT,
                            LOCAL=local,
                            hash_type=hash_type)
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
        # node.recomputeFingerTable()
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
    print("--------------------ENTRO A REMOVE DOC API")
    pos = rango.find('_')
    print("pos = ", pos)
    prev_id = int(rango[:pos])
    print("prev_id = ", prev_id)
    newserver_id = int(rango[pos + 1:])
    print("newserver_id = ", newserver_id)
    remove_data = []
    for i in range(prev_id, newserver_id):
        print("remove doc = ", i)
        data = f"document_{i}.txt"
        remove_data.append(data)
        database.remove_file(i)
    
    new_data_list = []
    print(f"node.data = {node.data}")
    current_data = list(node.data.values())[0]
    print(f"node.nodeID = {node.nodeID}")

    print(f"current_data en el remove_doc_api = {current_data}")
    for d in current_data:
        if d not in remove_data:
            new_data_list.append(d)

    # ahora vm solamente con los doc que se quedan en el server 
    text_list_to_remove = convert_str_to_text_class(PATH_TXTS, remove_data)
    # for text in text_list_to_remove:
    #     vec_mod.delete_doc(text.id)
    # vec_mod.doc_terms.clear()
    # vec_mod.doc_terms_data(text_list) 
    vec_mod.delete_doc_list(text_list_to_remove) 
        
    print(f"new_data_list = {new_data_list}")
    print(f"node.replay = {node.replay}")
    replay_list = list(node.replay.values())[0]
    node.update_server_files(new_data_list, replay_list)

# Leader
@app.get('/chord/channel/leader')
def is_leader():
    return {"is_leader":node.is_leader, "node_id":node.nodeID}

@app.get('/chord/channel/get_leader')
def get_leader():
    leader_ip = None
    leader_port = None
    actual_leader = node.leader
    if actual_leader:
        leader_ip = actual_leader.ip
        leader_port = actual_leader.port
    # else:
    #     leader_ip = node.node_address.ip
    #     leader_port = node.node_address.port

    return {"is_leader":node.is_leader, "node_id":node.nodeID, "node_address_ip":node.node_address.ip, "node_address_port":node.node_address.port, "leader_ip":leader_ip, "leader_port":leader_port}


def chord_replication_routine():
    print("Started Node Replication Routine")
    print("Timeout: ", TIMEOUT)
    stopped = False
    discover_timeout = 3
    try:
        while not stopped:
            # Actualizar la lista de nodos con el lider
            node.update_succesors()
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
                    print("------------VA A ENTRAR EN REPLICATION FILES 1")
                    replication_files1(next_address)
            # Si el siguiente se cayo, vuelvela a copiar, busca primero el nodo
            else:
                node.update_succesors()
                node.succ = node.get_succesor()
                if node.succ:
                    node.make_replication(next_id, next_address)
                    print("------------VA A ENTRAR EN REPLICATION FILES 2")
                    replication_files2(next_address)
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
                    print("------------VA A ENTRAR EN REPLICATION FILES 3")
                    # NO HACE FALTA ANALIZAR EL CASO DE QUE SE CAYO MI ANTECESOR PQ YA SE INCLUYE CUANDO SE ANALIZA EL CASO CAUNDO SE CAE MI SUCESOR
                    #replication_files2(next_address, False)
                    # TODO: FixBug TypeError: 'NoneType' object does not support item assignment
                    print_debug("Predecessors" + str(node.predecessor))
                    node.restart_pred_data_info(node.predecessor[0])
            # else:
                # Si aun no se tiene predecesor, esperamos a que el venga a buscarnos

            # TODO: Agregar rutina de FixFinger para que se ejecute a cada rato
            # node.recomputeFingerTable() #-
            print("FT", node.FT)
            # print('FT[','%04d'%node.nodeID,']: ',['%04d' % k for k in node.FT]) #- 

            print_info(node)
            print_info("get_predecessor method: "+str(node.get_predecessor()))
            # Si es lider entonces:
            # Check for other leaders or nodes on the network
            # Discovering
            if not discover_timeout and node.is_leader:
                node.discover()
                print_log(f"Leaders List: {node.leaders_list}")
            # Update discover_timeout: Iteraciones requeridas para verificar quienes estan en la red,
            # asi como los que se hayan unido nuevos. Se utiliza para estar atentos a cuando:
            # se unan o desconecten redes.
            if discover_timeout <= 0:
                discover_timeout = 3

            discover_timeout -= 1
            print_log(f"Discover Timeout: {discover_timeout}")
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
            if node.is_leader and datetime.datetime.now().time().second/30 == 0:
                # print(node.clock)
                # print("-------------------------------Check alive-----------------------------")
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
    with open(getcwd() + "/txts/" + file.filename, "wb") as myfile:
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