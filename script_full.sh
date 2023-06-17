#!/bin/bash
gateway=172.21.0.1
network_name=fastapi-quasar
for i in 1 2 3 4 5 6 7 8 9
do
 sudo docker run -it --rm --name backend-$i --network mi_red --ip 192.168.0.2 -e IP= -e PORT=10000 fastapi-files
 echo "backend-$i"
done