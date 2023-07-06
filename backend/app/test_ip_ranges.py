import ipaddress
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
		return [Address(str(ip), 80) for ip in ip_network.hosts()]
	
a = Address.get_ips_in_range("172.21.0.2")
for ip in a:
	print(ip)
# print(a)