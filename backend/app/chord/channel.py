import random

class Address:
	def __init__(self, ip, port) -> None:
		self.ip = ip
		self.port = port

	def __eq__(self, __value: object) -> bool:
		print("Compare->", self, __value)
		if isinstance(__value, Address):
			print("Inside isinstance")
			return self.ip == __value.ip and self.port == __value.port
		return False
	
	def __repr__(self) -> str:
		return f"ip:{self.ip}, port:{self.port}"

class PubMessage:
	def __init__(self, address:Address, msg) -> None:
		self.address = address
		self.msg = msg

class TransportLayer():
	def __init__(self, hostsIPs, hostsPorts) -> None:
		hosts:list[Address]= []

class Channel():
	def __init__(self, nBits=5, hostIP='redis', portNo=6379, address=Address("localhost", 8000)):
		# self.channel   = 5#redis.StrictRedis(host=hostIP, port=portNo, db=0)
		self.osmembers:dict = {}
		self.nBits     = nBits
		self.MAXPROC   = pow(2, nBits)
		self.address = address

	def get_member(self, node_id):
		try:
			return self.osmembers[node_id]
		except:
			return None
		
	def get_members(self, type='node'):
		return set(self.osmembers.keys())
           
	def join(self, subgroup, address, port):
		# members = self.channel.smembers('members')
		newpid = random.choice(list(set([str(i) for i in range(self.MAXPROC)]) - self.get_members()))
		# if len(members) > 0:
		# 	xchan = [[str(newpid), other] for other in members] + [[other, str(newpid)] for other in members]
		# 	for xc in xchan:
		# 		self.channel.rpush('xchan',pickle.dumps(xc))
		# Coordination...
        # self.channel.sadd('members',str(newpid))
		# self.channel.sadd(subgroup, str(newpid))
		self.osmembers[newpid] = Address(address, port)
		return str(newpid)
    
    
	def publish(self, caller, dst, message):
		return PubMessage(Address(self.osmembers[dst].address, self.osmembers[dst].port))

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