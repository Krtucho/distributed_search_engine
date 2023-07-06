#!/bin/bash
servers_amount=$1
gateway=172.21.0.
network_name=fastapi-quasar
for (( i=1; i<=$servers_amount; i++ ))
do
 let suma=$i+1
<<<<<<< HEAD
 sudo docker run -it --rm --name backend-$suma --network $network_name --ip $gateway$suma -e IP=$gateway$suma -e PORT=8000 fastapi-files
 
 echo "backend-$suma ip-$gateway$suma"
done

let frontend_servers_amount=$servers_amount+2
let server_index = 2 
sudo docker run -it --name frontend --rm --network $network_name --ip $gateway$frontend_servers_amount -e API_SERVER=$gateway$server_index dockerize-quasar-ip
=======
 sudo docker run -it --rm --name backend-$suma --network fastapi-quasar --ip $gateway$suma -e IP=$gateway$suma -e PORT=8000 fastapi-files
 
 echo "backend-$suma ip-$gateway$suma"
done
>>>>>>> roxy_branch
