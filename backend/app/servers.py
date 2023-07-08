from chord.channel import Address
import os

# Metodo para cargar un archivo donde cada linea es un servidor de la forma ip:port
def load_servers():
    """Load servers from file"""
    global servers
    servers = []
    with open('servers.txt', 'r') as file:
        for line in file:
            servers.append(line.strip())
    return servers

# Metodo para dado un rango de ips crear un archivo con los servidores de la forma ip:port
def create_servers_file(ip_start, ip_end, port):
    """Create servers file"""
    servers = []
    ip_start = ip_start.split('.')
    ip_end = ip_end.split('.')
    for i in range(int(ip_start[3]), int(ip_end[3]) + 1):
        servers.append(f'{ip_start[0]}.{ip_start[1]}.{ip_start[2]}.{i}:{port}')
    with open('servers.txt', 'w') as file:
        for server in servers:
            file.write(server + '\n')

# Metodo para crear una clase del tipo Address dada una direccion ip de las que devuelve load_servers()
def create_address(ip):
    """Create address from ip"""
    ip = ip.split(':')
    return Address(ip[0], int(ip[1]))

# Metodo para crear una lista de Address dada una lista de direcciones ip de las que devuelve load_servers()
def create_addresses(ips):
    """Create addresses from ips"""
    addresses = []
    for ip in ips:
        addresses.append(create_address(ip))
    return addresses

# Metodo para dado un rango de puertos crear un archivo con los servidores de la forma ip:port
def create_servers_file_port(ip, port_start, port_end):
    """Create servers file"""
    servers = []
    for i in range(port_start, port_end + 1):
        servers.append(f'{ip}:{i}')
    with open('servers.txt', 'w') as file:
        for server in servers:
            file.write(server + '\n')

def get_servers(local):
    servers = []
    if local:
        if os.path.exists('servers.txt'):
            servers = create_addresses(load_servers())
    else:
        create_servers_file_port('127.0.0.1', 10000, 10002)
        servers = create_addresses(load_servers())
    
    if not local:
        if os.path.exists('servers.txt'):
            servers = create_addresses(load_servers())
        else:
            create_servers_file('172.21.0.1', '172.21.0.20', 8000)
            servers = create_addresses(load_servers())

    return servers