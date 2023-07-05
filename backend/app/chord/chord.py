from chord.channel import * #-
import random, math #-
from chord.constChord import * #-
#-
import requests, os

from logs.logs_format import *

m = 5
n = 8

class ChordNode:
#-
  def __init__(self, chan: Channel, first_server_address: Address, node_address:Address, file_path="downloads/"):#-
    print(f"Started ChordNode for address: {node_address}") 
    self.is_leader = False
    self.leader = first_server_address
    # self.is_
    # self.socket = socket # Para enviar peticiones(paquetes) y recibir respuestas. En este caso se utilizara la instancia de fastapi
    if node_address == first_server_address:
      self.is_leader = True
      # Build channel properties
      self.chan = Channel(nBits=m, address=node_address)
      self.nBits   = self.chan.nBits                  # Num of bits for the ID space #-
      self.MAXPROC = self.chan.MAXPROC                # Maximum num of processes     #-
      self.nodeID  = int(self.chan.join('node', node_address.ip, node_address.port)) # Find out who you are         #-
      self.FT      = [None for i in range(self.nBits+1)] # FT[0] is predecessor #-
      self.nodeSet = []                           # Nodes discovered so far     #-
      self.nodeSetDict = {}

    if not self.is_leader:
      chan = self.ask_leader_for_channel()
      # Wait x seconds if leader is down

      print("Chan", chan)
      if not chan:
        # Leader
        while not chan:
          self.update_leaders_list()
          chan = self.ask_leader_for_channel()

      self.chan    = Channel(nBits=chan["nBits"], address=chan["address"]) # ask channel to leader                        # Create ref to actual channel #-
      self.nBits   = chan["nBits"]                  # Num of bits for the ID space #-
      self.MAXPROC = chan["MAXPROC"]                # Maximum num of processes     #-

      self.nodeID  = int(self.chan.join('node', node_address.ip, node_address.port)) # Find out who you are         #-


      self.FT      = [None for i in range(self.nBits+1)] # FT[0] is predecessor #-
      self.nodeSet = []                           # Nodes discovered so far     #-
      self.nodeSetDict = {}

    self.node_address = node_address

    # Replication
    self.successors = self.FT
    self.predecessor = None

    self.pred_data = {}
    self.last_pred_data = {}
    self.pred_active = False
    self.pred_data_copied = False

    self.data = {}
    self.successor_active = False

    self.file_path = file_path
    try:
      print("Listing Dir", os.listdir(self.file_path))
      self.data[self.nodeID] = os.listdir(self.file_path)
    except:
      print("Error Listing Dir")
    # self.data[self.nodeID] = [file for file in  os.listdir(self.file_path)]

    # Leaders
    self.leaders_list = set()

    if self.nodeID <= 0: # ID was not ok when joined to the network
      while self.nodeID <= 0:
        self.update_leaders_list()
      if self.nodeID <= 0: # I
        print_log("Error trying to get ID")
        return
    
    self.run()
    # Leaders
    self.update_leaders_list()
    self.update_succesors()
    succ = self.get_succesor() # succ seria el id(llave)
    print("Members", self.chan.osmembers)
    if succ:
      member = Address.extract_ip_port(self.chan.get_member(succ)) # member seria una direccion(Address)
      self.make_replication(succ, member)

  def __repr__(self):
    return f"NODO: Address: {self.node_address} node_id: {self.nodeID} successors: {self.successors} predecessor: {self.predecessor}"

  def get_predecessor(self):
    return self.FT[0]

  # Leader
  def remove_leader_from_leaders_list(self, leader):
    try:
      self.leaders_list.remove(leader)
      return True
    except:
      return False

  # Leader
  def add_leader_to_leaders_list(self, leader):
    return self.leaders_list.add(leader)
  
  # Leader
  def ask_for_leaders(self, leader):
    r = requests.get("http://{leader.ip}:{leader.port}/endpoint")

    # Update leaders_list

  # Leader
  def update_leaders_list(self):
    if self.leader: # Remueve el lider actual del conjunto de lideres xq se supone que se haya caido
      remove_
    # Search for next Leader in leaders_list
    if len(self.leaders_list) > 0:
      # Si se sabe de al menos otro lider en la red, pasamos a actualizar nuestro lider por ese y le hacemos las preguntas
      self.leader = self.leaders_list[0]
      self.ask_for_leaders(self.leader)
    else: # Si no se encuentra otro lider en la red, hacemos broadcasting buscando cual es el nodo con mayor id
      max_id_node = 0
      alive_servers = []
      for ip in Address.get_ips_in_range(self.node_address.ip, 8):
        # Haz requests por cada ip buscando quien esta vivo
        r = requests.get()
        # ve actualizando el nodo con mayor id
        max_id_node = max(max_id_node, "id_del_nodo")

      
      
      if len(alive_servers) <= 0: # Si no se encuentra ningun server vivo
        self.leader = self.node_address
      else:
        # Obten el nodo con mayor id
        # Luego de quedarte con el mayor pregunta si aun esta vivo y asume q ese sera el nuevo lider
        # Tb preguntale si el ya es lider o si conoce al lider. En ese caso ya puedes tirar directo primero para el q te
        # dijo que era el lider. Sino se asume que el lider sera el
        pass
      


  def join_leader(self, node_address):
    # server = '{"ip":'+f'"{node_address.ip}", "port":{node_address.port}'+'}'
    # print("server", server)
    data = {"server_ip":node_address.ip, "server_port":node_address.port, "content":"JOIN"}#'{"server"'+f':server, "content":"JOIN"'+'}'
    # print("data", data)
    r = None
    try:
      r = requests.post(f"http://{self.leader.ip}:{self.leader.port}/chord/channel/join", json=data)
      
      # print(r)
      # print(r.text)
      if r.ok:
        # r_json = r.json()
        # node_id = r_json["no"]
        # print("r_text", r.text)
        return str(r.text)
    except:
      self.update_leaders_list()
      return False
  
  def get_files(self):
    print(self.data[self.nodeID])
    # TODO: Se supone que luego en self.data[self.nodeID] se encuentre una lista con las replicas de todos los servidores caidos y de el mismo 
    file_list = [self.data[node_id] for node_id in self.data.keys()]
    files = []
    for list_file in file_list:
      files.extend(list_file)
    # files = file_list.#[file for file in file_list]
    # print(files)
    return files#[data for data in self.data[node_id]]#self.data[self.nodeID]

  def upload_content(self, next_id, next_address, file):
    return file

  def set_confirmation(self, next_id, next_address, files):
    data = {"node_id":self.nodeID, "ip":self.node_address.ip, "port":self.node_address.port, "files":files}
    try:
      r = requests.post(f"http://{next_address.ip}:{next_address.port}/chord/succ/data/done", json=data)
    except Exception as e:
      print(e)
  
  def make_replication(self, next_id, next_address, content=None):
    print("Making Replication")
    if not content:
        # Si no se pasa ningun contenido, asumimos que se va a replicar el mismo en su sucesor
        files = []
        for file in self.get_files():
          self.upload_content(next_id, next_address, file)
          files.append(file)
        print(next_address)
        self.set_confirmation(next_id, next_address, files)
    else:
        if next_address == self.node_address:
          return
        
        try:
          if self.node_is_alive(self.get_succesor()):
            # Upload only predecessor content: file
            files = []
            for file in content:
              self.upload_content(next_id, next_address, file)
              files.append(file)
            self.set_confirmation(next_id, next_address, files)
          else:
            # Find new successor
            self.update_succesors()
            # Upload all content
            files = []
            for file in content:
              self.upload_content(next_id, next_address, file)
              files.append(file)
            for file in self.get_files():
              self.upload_content(next_id, next_address, file)
              files.append(file)
            # print(next_address)
            self.set_confirmation(next_id, next_address, files)
        except:
          pass


        # files = self.upload_content(next_id, next_address, content, predecessor_content=True)

  def remove_succesor(self, node_id):
    self.successors.pop(0)

  def update_succesors(self):
    print("Before Update", self.chan.osmembers)
    if not self.is_leader:
      self.chan.osmembers = self.ask_members_to_leader()
      print("After update", self.chan.osmembers)
      for node in self.chan.osmembers.keys():
        self.addNode(node)
    next_id, next_address = self.localSuccNode(self.nodeID)
    print("Next Node", " Next ID: ", next_id, " Next_address: ", next_address)

  def get_succesor(self):
    # if self.FT[1] == None or self.FT[1] == self.nodeID:#len(self.successors) == 0:
    #   return None
    # Retorname el id del sucesor de self.nodeID en self.nodeSet
    if len(self.nodeSet) == 0:
      return int(self.nodeID)
    for node in self.nodeSet:
      if node > self.nodeID:
        return node
    return self.nodeSet[0]
    # self.nodeSet
    # return self.FT[1]

  def check_pred_data(self, nodeId, node_Address: Address):
    if node_Address == self.node_address:
      return True
    print("Inside Check Pred Data ID: ", nodeId, node_Address, self.pred_data_copied, self.pred_data.get(nodeId))
    return self.pred_data_copied and self.pred_data.get(nodeId)
  
  def confirm_pred_data_info(self, node_id, node_address, files=None):
    # if self.get_predecessor() == node_id:
    self.predecessor = (node_id, node_address)
    self.pred_data[node_id] = files
    self.pred_active = True
    self.pred_data_copied = True

  def restart_pred_data_info(self, nodeId):
    self.pred_data[nodeId] = None
    self.pred_active = False
    self.pred_data_copied = False
    self.predecessor = None

  # Predecessor
  def merge(self):
    if self.pred_data:
      self.data[self.predecessor[0]] = self.pred_data
    self.last_pred_data = self.pred_data
    self.pred_data = None

    return self.last_pred_data

  def remove_predecessor(self):
    self.predecessor = None
    
#-
  def ask_leader_for_channel(self):
    # print(self.leader)
    r = None
    try:
      r = requests.get(f"http://{self.leader.ip}:{self.leader.port}/chord/channel/info/")
      # print(r)
      # print(r.text)
      # print(r.content)
      # if r.ok:
      #   print(r)
      #   print(r.text)
      #   print(r.json())
      
      return r.json()
    except Exception as e:
      print(e)
      # Leader
      self.update_leaders_list()
      return None

  def ask_members_to_leader(self):
    # leader_address = self.chan[self.leader]
    if self.is_leader:
      for node in self.chan.osmembers.keys():
        self.addNode(node)
      return self.chan.osmembers
    
    try: # Checking if leader is ok, if not update_leaders
    r = requests.get(f"http://{self.leader.ip}:{self.leader.port}/chord/channel/members/")
    print(r)
    print(r.text)
    if r.ok:
      osmembers = r.json()["osmembers"]
      self.chan.osmembers = osmembers
      for node in self.chan.osmembers.keys():
        self.addNode(node)
      print("Ask members to leader", osmembers)
      return osmembers
    return None

  def get_members(self):
    # r = requests.get(f"http://{self.chan.address.ip}:{self.chan.address.port}/chord/channel/members/")
    # if r.ok():
    #   osmembers = r["osmembers"]
    #   self.chan.osmembers = osmembers
    #   return osmembers
    # return None
    return set(self.ask_members_to_leader())

  def inbetween(self, key, lwb, upb):                                         #-
    if lwb <= upb:                                                            #-
      return lwb <= key and key < upb                                         #-
    else:                                                                     #- 
      return (lwb <= key and key < upb + self.MAXPROC) or (lwb <= key + self.MAXPROC and key < upb)                        #-
#-
  def addNode(self, nodeID):                                                  #-
    self.nodeSet.append(int(nodeID))                                          #-
    self.nodeSet = list(set(self.nodeSet))                                    #-
    self.nodeSet.sort()                                                       #-
#-
  def delNode(self, nodeID):                                                  #-
    print("Assert_node_id: ", nodeID)
    assert int(nodeID) in self.nodeSet, ''                                        #-
    del self.nodeSet[self.nodeSet.index(int(nodeID))]                              #-
    self.nodeSet.sort()                                                       #-
#-
  def finger(self, i):
    print("Inside finger", type(self.nodeID), type(self.MAXPROC), type(pow(2, i-1)))

    succ = (int(self.nodeID) + pow(2, i-1)) % self.MAXPROC    # succ(p+2^(i-1))
    lwbi = self.nodeSet.index(self.nodeID)               # own index in nodeset
    upbi = (lwbi + 1) % len(self.nodeSet)                # index next neighbor
    for k in range(len(self.nodeSet)):                   # go through all segments
      if self.inbetween(succ, self.nodeSet[lwbi]+1, self.nodeSet[upbi]+1):
        return self.nodeSet[upbi]                        # found successor
      (lwbi,upbi) = (upbi, (upbi+1) % len(self.nodeSet)) # go to next segment
    return None                                                                #-

  def recomputeFingerTable(self):
    print("Recomputing FingerTable...")
    # if self.nodeSet.__contains__(self.nodeID-1):
    try:
      self.FT[0]  = self.nodeSet[self.nodeSet.index(self.nodeID)-1] # Predecessor
    except:
      self.FT[0] = self.nodeID
    self.FT[1:] = [self.finger(i) for i in range(1,self.nBits+1)] # Successors
    print(self.FT)

  def localSuccNode(self, key):
    if len(self.nodeSet) <= 1:
      return None, None
    if self.inbetween(key, self.FT[0]+1, self.nodeID+1): # key in (FT[0],self]
      return self.nodeID, self.chan.get_member(self.nodeID)                                 # node is responsible
    elif self.inbetween(key, self.nodeID+1, self.FT[1]): # key in (self,FT[1]]
      return self.FT[1], self.chan.get_member(self.FT[1])                               # successor responsible
    for i in range(1, self.nBits+1):                     # go through rest of FT
      if self.inbetween(key, self.FT[i], self.FT[(i+1) % self.nBits]):
        return self.FT[i], self.chan.get_member(self.FT[i])                                # key in [FT[i],FT[i+1]) 
#- 
  def run(self): #-
    # self.chan.bind(self.nodeID) #-
    self.addNode(self.nodeID) #-

    others = (self.chan.get_members() if self.is_leader else self.get_members()) - set([str(self.nodeID)])#list(self.chan.channel.smembers('node') - set([str(self.nodeID)])) #-
    print("others", others)
    for i in others: #-
      self.addNode(i) #-
      servers:list[PubMessage] = self.chan.sendTo(self.nodeID, [i], (JOIN)) #-
      for server in servers:
        requests.post(f"http://{server.address.ip}:{server.address.port}/")
    self.recomputeFingerTable() #-
 #-


 # Leader
  def node_is_alive(self, node_id):
    address = self.chan.get_member(node_id)
    r = None
    try:
      r = requests.get(f"http://{address.ip}:{address.port}", timeout=3)
    except Exception as e:
      print(e)

    if r and r.ok:
      return True
    else:
      return False
 
  def check_live_nodes(self):
    has_changed: bool = False
    print("Check for live nodes \n", "NodeSet: ",self.nodeSet, " ChannelMembers: ", self.chan.osmembers)
    try:
      for node in self.chan.osmembers.keys():
        if int(node) == self.nodeID:
          continue
        print_info("Checking node: "+ node)
        if not self.node_is_alive(node):
          self.delNode(node)
          self.chan.remove_member(node)
          has_changed = True
    except Exception as e:
      print(e)
      has_changed = True

    if has_changed:
      self.recomputeFingerTable()
   
 #-
# class ChordClient: #-
#   def __init__(self, chan):                #-
#     self.chan    = chan #-
#     self.nodeID  = int(self.chan.join('client')) #-
#  #-
#   def run(self): #-
#     self.chan.bind(self.nodeID) #-
#     procs = [int(i) for i in list(self.chan.channel.smembers('node'))] #-
#     procs.sort() #-
#     print(['%04d' % k for k in procs]) #-
#     p = procs[random.randint(0,len(procs)-1)] #-
#     key = random.randint(0,self.chan.MAXPROC-1) #-
#     print(self.nodeID, "sending LOOKUP request for", key, "to", p) #-
#     self.chan.sendTo([p],(LOOKUP_REQ, key)) #-
#     msg = self.chan.recvFrom([p]) #-
#     while msg[1][1] != p: #-
#       p = msg[1][1] #-
#       self.chan.sendTo([p],(LOOKUP_REQ, key)) #-
#       msg = self.chan.recvFrom([p]) #-
#     print(self.nodeID, "received final answer from", p) #-
#     self.chan.sendTo(procs, (STOP)) #-
#  #-
