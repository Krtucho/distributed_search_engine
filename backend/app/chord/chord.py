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

    
      self.chan    = Channel(nBits=chan["nBits"], address=chan["address"]) # ask channel to leader                        # Create ref to actual channel #-
      self.nBits   = chan.nBits                  # Num of bits for the ID space #-
      self.MAXPROC = chan.MAXPROC                # Maximum num of processes     #-
      self.nodeID  = int(self.chan.join('node')) # Find out who you are         #-
      self.FT      = [None for i in range(self.nBits+1)] # FT[0] is predecessor #-
      self.nodeSet = []                           # Nodes discovered so far     #-
      self.nodeSetDict = {}

    # Replication
    self.successors = []
    self.predecessor = None

    self.pred_data = {}
    self.last_pred_data = {}
    self.pred_active = False
    self.pred_data_copied = False

    self.data = {}
    self.successor_active = False

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
    pass

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
    chan = requests.get(f"http://{self.leader.ip}:{self.leader.port}/chord/channel/info/")


  def get_members(self):
    r = requests.get(f"http://{self.chan.address.ip}:{self.chan.address.port}/chord/channel/members/")
    if r.ok():
      osmembers = r["osmembers"]
      self.chan.osmembers = osmembers
      return osmembers
    return None

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
    succ = (self.nodeID + pow(2, i-1)) % self.MAXPROC    # succ(p+2^(i-1))
    lwbi = self.nodeSet.index(self.nodeID)               # own index in nodeset
    upbi = (lwbi + 1) % len(self.nodeSet)                # index next neighbor
    for k in range(len(self.nodeSet)):                   # go through all segments
      if self.inbetween(succ, self.nodeSet[lwbi]+1, self.nodeSet[upbi]+1):
        return self.nodeSet[upbi]                        # found successor
      (lwbi,upbi) = (upbi, (upbi+1) % len(self.nodeSet)) # go to next segment
    return None                                                                #-

  def recomputeFingerTable(self):
    self.FT[0]  = self.nodeSet[self.nodeSet.index(self.nodeID)-1] # Predecessor
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
    others = self.chan.get_members() - set([str(self.nodeID)])#list(self.chan.channel.smembers('node') - set([str(self.nodeID)])) #-
    for i in others: #-
      self.addNode(i) #-
      servers:list[PubMessage] = self.chan.sendTo([i], (JOIN)) #-
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
