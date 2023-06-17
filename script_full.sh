#!/bin/bash
servers_amount=$1
gateway=172.21.0.
network_name=fastapi-quasar


for (( i=1; i<=$servers_amount; i++ ))
do
 let suma=$i+1
 sudo docker run -it --rm --name backend-$suma --network fastapi-quasar --ip $gateway$suma -e IP=$gateway$suma -e PORT=8000 fastapi-files
 
 echo "backend-$suma ip-$gateway$suma"
done