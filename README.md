# distributed_search_engine

# Documentacion

## Arquitectura

Se implemento una arquitectura Publisher/Subscriber(Publicador/Subscriptor) donde todos los servidores van a estar a la espera de nuevas notificaciones, las cuales seran peticiones de alguna consulta por un nombre de un archivo o el contenido del mismo.

Tambien se impolementa una arquitectura peer-to-peer en forma de anillo haciendo uso de Chord, para la organizacion de todos los nodos en la red y la replicacion de la informacion.

## Peticiones y Comunicacion

Se utilizo la libreria de fastapi para crear los endpoints que nos permitiran a traves de conexiones http comunicar a todos los servidores. Se crean varias rutas, algunas para las consultas(query), otras para la comunicacion entre servidores pertenecientes a la red de Chord, otros para la replicacion entre estos servidores de la red Chord y otros para el manejo de descarga y subida de archivos.

## Creacion de los nodos

La clase ChordNode crea una instancia de nodo perteneciente a la red de Chord, en cada servidor que se corra(contenedor de Docker). Cada uno de estos nodos trae consigo una instancia de la clase channel(Canal de comunicacion entre los nodos de la red de Chord). El nodo principal(el coordinador que se supone q nunca se muera) tendra una instancia de channel que guardara constantemente los nodos que estan vivos, a cada x cantidad de segundos este servidor comprobara que los nodos sigan levantados y actualizara el diccionario de nodos levantados consecuentemente. Todos los demas nodos que no sean exactamente el nodo coordinador le haran peticiones a este y actualizaran su diccionario o lista de nodos que se encuentran actualmente en la red comunicandose por este canal de la clase Channel. El endpoint que se crea para preguntar por todos los archivos es el terminado en get_members.

## Coordinación

Existe un servidor principal que sera el primero en conectarse a la red y se espera(segun lo que se informo) que no se le desconecte. Este funciona como canal de comunicacion entre los nodos que se encuentran en la red de Chord para estos saber cuales nodos se encuentran vivos, asi como sus respectivos ids.

## Replicacion

Ya que cada nodo conoce en cada instante su id y los nodos que se encuentran en la red, este sabe quien es su sucesor. Al entrar en la red cada nodo procede a replicar su informacion con su sucesor, constentemente este verifica que su sucesor se encuentre activo. Al terminar de replicarse envia un mensaje a su sucesor de que ya se ha replicado y que es su predecesor, de esta forma el sucesor se entera de que alguien replico su informacion en el y entonces a cada x cantidad de segundos este sucesor verifica que su precesesor siga vivo. En caso de carse el predecesor la informacion replicada en el sucesor ahora pasa a formar parte del sucesor y este busca replicarse en su sucesor y asi se repite el proceso por cada nodo. Tambien, recalcar que constantemente cada nodo verifica que no se haya caido su sucesor que tiene la info replicada para entonces.

## Tolerancia a fallos

Cada vez que se realiza alguna peticion a un servidor y este no responde, se utilizan vias para evitar que deje de funcionar el servidor desde donde se crea la peticion. Por ejemplo:

- Si se cae un nodo, su informacion ya fue replicada y se le informa lo antes posible a los demas nodos de la red que ese nodo abandono la red. Luego, su id quedaria libre y tambien se actualizarian en todos los servidores las listas de nodos que se encuentran activos en la red.
- Si se cae el sucesor, este nodo busca un nuevo sucesor.
- Si se cae el predecesor, la informacion del mismo ahora forma parte del sucesor.

## Para correr rapidamente un servidor de backend en una red que creemos

```bash
>sudo docker network create fastapi-quasar
>sudo docker network inspect fastapi-quasar
```

Con el comando anterior les va a salir info de la red. Buscan en el array de Config el campo de Gateway y poner ip a los servidores que se creen con la imagen que se crea a continuacion que pertenezcan a este mismo rango:

```bash
>sudo docker build -t fastapi-files .
```

Esto anterior para crear la imagen y luego la corremos:

```bash
>sudo docker run -it --rm --name backend --network $fastapi-quasar --ip $gateway$ip -e FIRST_SERVER=ip_de_server_principal -e IP=$gateway$ip -e PORT=8000 -e LOCAL=False fastapi-files
```

sudo docker run -it --rm --name backend --network $fastapi-quasar --ip $gateway$ip -e FIRST_SERVER=ip_de_server_principal -e IP=$gateway$ip -e PORT=8000 -e LOCAL=False -v $path_donde_tengan_la_carpeta_nltk_data>:/usr/share/nltk_data fastapi-files

## Backend

```bash
>cd backend

>sudo docker build -t fastapi-files .

>sudo docker run -d --name backend fastapi-files

>sudo docker run -it --rm --name backend --network $fastapi-quasar --ip $gateway$ip -e FIRST_SERVER=ip_de_server_principal -e IP=$gateway$ip -e PORT=8000 -e LOCAL=False fastapi-files
``

## Frontend

```bash
>sudo docker build -t dockerize-quasar-ip .

>sudo docker run -d --rm --name frontend --network fastapi-quasar -e API_SERVER=$server_ip:$server_port dockerize-quasar-ip
```

## Network

```bash
>sudo docker network create fastapi-quasar

>sudo docker network connect fastapi-quasar backend

>sudo docker network connect fastapi-quasar frontend
```

## Run Script(Beta)

Primeramente construir las imagenes:

```bash
>bash ./script.sh
```

## Run Script(Beta) Full
Este script si realiza todo el proceso y no es necesario hacer sudo docker build... para construir las imagenes de docker:

```bash
>bash ./script_full.sh
```

## Correr proyecto localmente

### Backend

Acceder a backend/app/main.py poner la variables local en True
Modificar las demas variables a conveniencia

#### Para correr 1 server

```bash
>cd backend/app
>uvicorn main:app --host 0.0.0.0 --port 10000
```

#### Para correr mas de 1 server

Abrir archivo main.py y en la variable port asignar el valor del puerto del nuevo servidor a correr y escribir en la consola el mismo comando pero cambian su puerto.

Por ejemplo, si deseamos crear los servidores con puertos 10001 y 10002, ademas el servidor que creamos anteriormente(que seria el coordinador) hacemos:
Primeramente cambiamos la variable port del archivo main.py a 10001.

```python
server = 'localhost'
port = 10001 # Correrlo local
```

y hacemos:

```bash
>cd backend/app
>uvicorn main:app --host 0.0.0.0 --port 10001
```

Luego cambiamos la variable port del archivo main.py a 10002:

```python
server = 'localhost'
port = 10002 # Correrlo local
```

y hacemos:

```bash
>cd backend/app
>uvicorn main:app --host 0.0.0.0 --port 10002
```
