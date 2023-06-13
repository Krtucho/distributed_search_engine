import random

class Address:
    def __init__(self, ip, port) -> None:
          self.ip = ip
          self.port = port

class TransportLayer():
    def __init__(self, hostsIPs, hostsPorts) -> None:
           hosts:list[Address]= []

class Channel():
    def __init__(self, nBits=5, hostIP='redis', portNo=6379):
		self.channel   = 5#redis.StrictRedis(host=hostIP, port=portNo, db=0)
		self.osmembers = {}
		self.nBits     = nBits
		self.MAXPROC   = pow(2, nBits)
                
    def join(self, subgroup):
		# members = self.channel.smembers('members')
		newpid = random.choice(list(set([str(i) for i in range(self.MAXPROC)]) - members))
		# if len(members) > 0:
		# 	xchan = [[str(newpid), other] for other in members] + [[other, str(newpid)] for other in members]
		# 	for xc in xchan:
		# 		self.channel.rpush('xchan',pickle.dumps(xc))
		# Coordination...
        # self.channel.sadd('members',str(newpid))
		# self.channel.sadd(subgroup, str(newpid))
		return str(newpid)
    
    def get_members(self, type='node'):
        return 
    
    def sendTo(self, caller, destinationSet, message):
		# caller = self.osmembers[os.getpid()]
		# assert self.channel.sismember('members', str(caller)), ''
		# if not is_member(caller, 'members'):
        #     return

        for i in destinationSet: 
			# assert self.channel.sismember('members', str(i)), ''
		    # if not is_member(caller, 'members'):
			#     return 
            self.channel.rpush([str(caller),str(i)], pickle.dumps(message) )
            publish(caller, i, message)

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