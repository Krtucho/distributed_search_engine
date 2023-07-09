import hashlib

def hash_key(key: str) -> int:
    """
    Función de hash que calcula el hash SHA-1 de una cadena de caracteres y devuelve un número entero que se utiliza como la clave del nodo en la red Chord.
    """
    sha1 = hashlib.sha1(key.encode('utf-8'))
    hash_value = int(sha1.hexdigest(), 16) # convierte el hash SHA-1 en un número entero
    return hash_value

# class Address(object):
# 		def __init__(self,ip,port):
# 			self.ip=ip
# 			self.port=port
# 		def __str__(self):
# 			return f"tcp://{self.ip}:{self.port}"

# print(hash_key(""))