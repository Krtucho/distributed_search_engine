import re

docs = ["document_1.txt", "document_2.txt", "document_3.txt"]
doc = "".join(docs)  # Concatenar los documentos en una cadena

pattern = r"document_(\d+)\.txt"  # Patrón de búsqueda para encontrar los índices
matches = re.finditer(pattern, doc)

indices = [int(match.group(1)) for match in matches]

print("Índices encontrados:", indices)


def replication_files(next_address):
    print(f"-------ENTRO EN replication_files")
    current_id = node.nodeID
    print(f" current_id = {current_id}")
    prev = node.get_predecessor()
    print(f"!!!!!!!!!!!!!!!!!!!prev = {prev}")

    # TOMA LOS DOCS DE SU PREVIEW (REPLICACION)
    docs_before_reply = get_actual_data() #dame sus documentos (no los de la replicacion)
    print(f"docs_before_reply = {docs_before_reply}, len = {len(docs_before_reply)} ")
    
    prev_address = get_prev_adr(prev)
    try:
        print("1-")
        prev_server_str = f'http://{prev_address["ip"]}:{prev_address["port"]}/api/get_actual_data'
    except:
        print("2-")
        prev_server_str = f'http://{prev_address.ip}:{prev_address.port}/api/get_actual_data'

    print(f"prev_server_str = {prev_server_str}")
    # obtener los doc del node preview
    response_actual_docs_prev = requests.get(prev_server_str, verify=False) #dame los doc de tu prev (no incluye su replicacion)
    actual_docs_prev = response_actual_docs_prev.json()
    print(f"valores actuales del preview del nodo actual = {actual_docs_prev}, len = {len(actual_docs_prev)}")
    text_list = convert_str_to_text_class(PATH_TXTS,actual_docs_prev)
    #insertarlos en la BD del node actual
    for file in text_list:
        database.insert_file(file)
    docs_after_reply = get_actual_data()
    print(f"docs_after_reply = {docs_after_reply}")
    print(f"actual data despues de replicar el prev en el actual = {docs_after_reply}, len = {len(docs_after_reply)}")
    #node.update_server_files(docs_after_reply)
    node.update_server_files(docs_before_reply, actual_docs_prev)

    # BORRA DEL SUCESOR LOS DOCS DEL Q ERA SU PREVIEW ANTES DE Q EL NUEVO ENTRARA
    print(f"next_address = {next_address}")
    try:
        url = f'http://{next_address.ip}:{next_address.port}/api/delete_prev_doc'
    except:
        url = f'http://{next_address["ip"]}:{next_address["port"]}/api/delete_prev_doc'

    print("------------------------------AQUIIIII")
    print(f"url para requests.delete() = {url}")
    doc = "".join(actual_docs_prev)
    url += f'/{doc}'
    response = requests.delete(url, verify=False)
    if response.status_code == 200:
        data = response.json()
        print('Elementos eliminados exitosamente')
        print('Documentos eliminados:', data['deleted_docs'])
        print('Documentos restantes:', data['remaining_docs'])
    else:
        print('Error al eliminar elementos')

    # COPIA SUS DOCS EN SU SUCESOR
    try:
        url = f'http://{next_address.ip}:{next_address.port}/api/replication_docs'
    except:
        url = f'http://{next_address["ip"]}:{next_address["port"]}/api/replication_docs'


    print("------------------------------AQUIIIII 2")
    print(f"url para requests.delete() = {url}")
    doc = "".join(docs_before_reply)
    url += f'/{doc}'
    response = requests.delete(url, verify=False)
    if response.status_code == 200:
        data = response.json()
        print('Elementos replicados exitosamente')
        print('Documentos replicados:', data['deleted_docs'])
        print('Documentos actuales:', data['actual_docs'])
    else:
        print('Error al replicar elementos')

    #if prev_id > current_id:# Si mi predecesor es mayor q yo entonces q empiece desde el principio q es 0
    #    rango = f'1_{current_id + 1}'
    #else:
    #    rango = f'{prev_id + 1}_{current_id + 1}'
    #print(f"RANGO = {rango}")
    #server_str = f'http://{next_address.ip}:{next_address.port}/api/replication/{rango}'
    #try:
    #    print("-------va a hacer el request api/replication")
    #    new_docs_replicated = requests.get(server_str, verify=False)
    #except:
    #    print(f"DIO ERROR EN EL REQUEST.GET")