from servers import *

create_servers_file("172.21.0.2", "172.21.0.20", 8000)

servers_list = create_addresses(load_servers())

print(servers_list)