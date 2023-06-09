import ipaddress
import random
import threading

from chord.utils import hash_key

lock = threading.Lock() 

class Address:
	def __init__(self, ip, port) -> None:
		self.ip = ip
		self.port = port

	def __eq__(self, __value: object) -> bool:
		# print("Compare->", self, __value)
		if isinstance(__value, Address):
			# print("Inside isinstance")
			return self.ip == __value.ip and self.port == __value.port
		return False
	
	def __repr__(self) -> str:
		return f"ip:{self.ip}, port:{self.port}"
	
	def __hash__(self):
		return hash((self.ip, self.port))
	
	@staticmethod
	def extract_ip_port(address):
		if isinstance(address, Address):
			return address
		try:
			return Address(address["ip"], address["port"])
		except Exception as e:
			print(e)

	@staticmethod
	def get_ips_in_range(ip_address, network_bits=24):
		ip_network = ipaddress.IPv4Network(f"{ip_address}/{network_bits}", strict=False)
		return [Address(str(ip), 8000) for ip in ip_network.hosts()]
	
	@staticmethod
	def get_ips_in_range_locals(ip_address, network_bits=24):
		return [Address('127.0.0.1', port) for port in range(10000, 10255)]

class PubMessage:
	def __init__(self, address:Address, msg) -> None:
		self.address = address
		self.msg = msg

class TransportLayer():
	def __init__(self, hostsIPs, hostsPorts) -> None:
		hosts:list[Address]= []

class Channel():
	def __init__(self, nBits=5, hostIP='redis', portNo=6379, address=Address("127.0.0.1", 8000), hash_type="RANDOM"):
		# self.channel   = 5#redis.StrictRedis(host=hostIP, port=portNo, db=0)
		self.osmembers:dict = {}
		self.nBits     = nBits
		self.MAXPROC   = pow(2, nBits)
		self.address = address
		self.hash_type = hash_type

	def get_member(self, node_id:int):
		node_id:str = str(node_id)
		# print("INSIDE GET_MEMBER", "Osmembers:", self.osmembers)
		# print("INSIDE GET_MEMBER", "osmembers on node_id: ", self.osmembers[node_id], "Osmembers:", self.osmembers)

		try:
			# print("INSIDE GET_MEMBER AND TRY", "osmembers on node_id: ", self.osmembers[node_id], "Osmembers:", self.osmembers)
			return self.osmembers[str(node_id)]
		except:
			return None
		
	def get_members(self, type='node'):
		print("members keys", self.osmembers.keys())
		print(self.osmembers)
		return set(self.osmembers.keys())
           
	def remove_member(self, node_id):
		self.osmembers.pop(str(node_id))

	def join(self, subgroup, address, port):
		with lock:
			newpid = 0
			# members = self.channel.smembers('members')
			if self.hash_type == "SHA1":
				newpid = hash_key(str(address))
			else: # SHA1
				newpid = random.choice(list(set([str(i) for i in range(self.MAXPROC)]) - self.get_members()))
			# if len(members) > 0:
			# 	xchan = [[str(newpid), other] for other in members] + [[other, str(newpid)] for other in members]
			# 	for xc in xchan:
			# 		self.channel.rpush('xchan',pickle.dumps(xc))
			# Coordination...
			# self.channel.sadd('members',str(newpid))
			# self.channel.sadd(subgroup, str(newpid))
			self.osmembers[str(newpid)] = Address(address, port)
			return str(newpid)
		
		# members = self.channel.smembers('members')
		# newpid = random.choice(list(set([str(i) for i in range(self.MAXPROC)]) - self.get_members()))
		# if len(members) > 0:
		# 	xchan = [[str(newpid), other] for other in members] + [[other, str(newpid)] for other in members]
		# 	for xc in xchan:
		# 		self.channel.rpush('xchan',pickle.dumps(xc))
		# Coordination...
		# self.channel.sadd('members',str(newpid))
		# self.channel.sadd(subgroup, str(newpid))
		# self.osmembers[newpid] = Address(address, port)
		# return str(newpid)

	def publish(self, caller, dst, message):
		# print("On publish method", )
		address = Address.extract_ip_port(self.osmembers[dst])
		return PubMessage(address=address, msg=message)

	def sendTo(self, caller, destinationSet, message):
		# caller = self.osmembers[os.getpid()]
		# assert self.channel.sismember('members', str(caller)), ''
		# if not is_member(caller, 'members'):
        #     return

		ans = []
		for i in destinationSet:
			# assert self.channel.sismember('members', str(i)), ''
		    # if not is_member(caller, 'members'):
			#     return 
            # self.channel.rpush([str(caller),str(i)], pickle.dumps(message) )
			ans.append(self.publish(caller, i, message))

		return ans

	def recvFromAny(self, caller, timeout=0):
		# caller = self.osmembers[os.getpid()]
		# assert self.channel.sismember('members', str(caller)), ''
		members = self.get_members()#self.channel.smembers('members')
		# xchan = [[str(i),str(caller)] for i in members]
		# msg = self.channel.blpop(xchan, timeout)
		# if msg:
		# 	return [msg[0].split("'")[1],pickle.loads(msg[1])]
        
        # Check for messages from anybody
        # Return those messages