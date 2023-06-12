from chord.channel import * #-
import random, math #-
from chord.constChord import * #-
#-
import requests

m = 5
n = 8

class ChordNode:
#-
  def __init__(self, chan: Channel, first_server_address: Address, node_address:Address):#-
    print(f"Started ChordNode for address: {node_address}") 
    self.is_leader = False
    self.leader = first_server_address
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
      self.chan    = Channel(nBits=chan["nBits"], address=chan["address"]) # ask channel to leader                        # Create ref to actual channel #-
      self.nBits   = chan["nBits"]                  # Num of bits for the ID space #-
      self.MAXPROC = chan["MAXPROC"]                # Maximum num of processes     #-

      # self.nodeID  = int(self.chan.join('node', node_address.ip, node_address.port)) # Find out who you are         #-
      self.nodeID = int(self.join_leader(node_address))
      self.FT      = [None for i in range(self.nBits+1)] # FT[0] is predecessor #-
      self.nodeSet = []                           # Nodes discovered so far     #-
      self.nodeSetDict = {}

    self.node_address = node_address

    # Replication
    self.successors = []
    self.predecessor = None

    self.pred_data = {}
    self.last_pred_data = {}
    self.pred_active = False
    self.pred_data_copied = False

    self.data = {}
    self.successor_active = False

    self.run()
    self.update_succesors()
    succ = self.get_succesor() # succ seria el id(llave)
    print("Members", self.chan.osmembers)
    if succ:
      member = self.chan.get_member(succ) # member seria una direccion(Address)
      self.make_replication(succ, member)

  def __repr__(self):
    return f"NODO: Address: {self.node_address} node_id: {self.nodeID} successors: {self.successors} predecessor: {self.predecessor}"

  def join_leader(self, node_address):
    # server = '{"ip":'+f'"{node_address.ip}", "port":{node_address.port}'+'}'
    # print("server", server)
    data = {"server_ip":node_address.ip, "server_port":node_address.port, "content":"JOIN"}#'{"server"'+f':server, "content":"JOIN"'+'}'
    print("data", data)
    r = requests.post(f"http://{self.leader.ip}:{self.leader.port}/chord/channel/join", json=data)
    
    # print(r)
    # print(r.text)
    if r.ok:
      # r_json = r.json()
      # node_id = r_json["no"]
      # print("r_text", r.text)
      return str(r.text)
    return None
  
  def get_files(self):
    pass

  def upload_content(self, file):
    pass

  def make_replication(self, next_id, next_address, content=None):
    if not content:
        # Si no se pasa ningun contenido, asumimos que se va a replicar el mismo en su sucesor
        for file in self.get_files():
            self.upload_content(file)
    else:
        self.upload_content(content)

  # Predecessor
  def merge(self):
    if self.pred_data:
      self.data[self.predecessor] = self.pred_data
    self.last_pred_data = self.pred_data
    self.pred_data = None

    return self.last_pred_data

  def remove_succesor(self, node_id):
    self.successors.pop(0)

  def update_succesors(self):
    if not self.is_leader:
      self.chan.osmembers = self.ask_members_to_leader()
      for node in self.chan.osmembers.keys():
        self.addNode(node)
    next_id, next_address = self.localSuccNode(self.nodeID)
    print("Next Node", " Next ID: ", next_id, " Next_address: ", next_address)

  def get_succesor(self):
    if len(self.successors) == 0:
      return None
    return self.successors[0]

  def check_pred_data(self, nodeId, node_Address: Address):
    return self.pred_data_copied and self.pred_data.get(nodeId)
  
  def restart_pred_data_info(self, nodeId, node_Address):
    self.pred_data[nodeId] = None
    self.pred_active = False
    self.pred_data_copied = False
    
#-
  def ask_leader_for_channel(self):
    print(self.leader)
    r = requests.get(f"http://{self.leader.ip}:{self.leader.port}/chord/channel/info/")
    print(r)
    print(r.text)
    # print(r.content)
    # if r.ok:
    #   print(r)
    #   print(r.text)
    #   print(r.json())
    
    return r.json()

  def ask_members_to_leader(self):
    # leader_address = self.chan[self.leader]
    if self.is_leader:
      return self.chan.osmembers
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
    assert nodeID in self.nodeSet, ''                                         #-
    del self.nodeSet[self.nodeSet.index(nodeID)]                              #-
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
    # if self.nodeSet.__contains__(self.nodeID-1):
    try:
      self.FT[0]  = self.nodeSet[self.nodeSet.index(self.nodeID)-1] # Predecessor
    except:
      self.FT[0] = self.nodeID
    self.FT[1:] = [self.finger(i) for i in range(1,self.nBits+1)] # Successors

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
