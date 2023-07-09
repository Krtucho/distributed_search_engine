from servers import *

create_servers_file("172.21.0.2", "172.21.0.20", 8000)

servers_list = create_addresses(load_servers())

print(servers_list)

#sudo docker run -it --rm --name backend --network fastapi-quasar --ip 172.21.0.2 -e FIRST_SERVER=172.21.0.2 -e IP=172.21.0.2 -e PORT=8000 -e LOCAL=False -v /home/krtucho/nltk_data:/usr/share/nltk_data fastapi-files