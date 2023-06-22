# distributed_search_engine

# Documentacion
## Arquitectura

Se implemento una arquitectura Publisher/Subscriber(Publicador/Subscriptor) donde todos los servidores van a estar a la espera de nuevas notificaciones, las cuales seran peticiones de alguna consulta por un nombre de un archivo o el contenido del mismo.

Tambien se impolementa una arquitectura peer-to-peer en forma de anillo haciendo uso de Chord, para la organizacion de todos los nodos en la red y la replicacion de la informacion.

## Peticiones y Comunicacion
Se utilizo la libreria de fastapi para crear los endpoints que nos permitiran a traves de conexiones http comunicar a todos los servidores. Se crean varias rutas, algunas para las consultas(query), otras para la comunicacion entre servidores pertenecientes a la red de Chord, otros para la replicacion entre estos servidores de la red Chord y otros para el manejo de descarga y subida de archivos.

## Para correr rapidamente un servidor de backend en una red que creemos
>sudo docker network create fastapi-quasar
>sudo docker network inspect fastapi-quasar

Con el comando anterior les va a salir info de la red. Buscan en el array de Config el campo de Gateway y poner ip a los servidores que se creen con la imagen que se crea a continuacion que pertenezcan a este mismo rango:

>sudo docker build -t fastapi-files .
Esto anterior para crear la imagen y luego la corremos:

>sudo docker run -it --rm --name backend --network $fastapi-quasar --ip $gateway$ip -e FIRST_SERVER=ip_de_server_principal -e IP=$gateway$ip -e PORT=8000 fastapi-files

## Backend

```bash
>cd backend

>sudo docker build -t fastapi-files .

>sudo docker run -d --name backend fastapi-files

>sudo docker run -it --rm --name backend -e DB_URL=mongodb://db:27017/test -e PORT=10000 fastapi-files
```

## Frontend
```bash
>sudo docker build -t dockerize-quasar-ip .

>sudo docker run -d --name frontend dockerize-quasar-ip
```

## Network
```bash
>sudo docker network create fastapi-quasar

>sudo docker network connect fastapi-quasar backend

>sudo docker network connect fastapi-quasar frontend
```
## Run Script(Beta)
Primeramente construir las imagenes.
```bash
>bash ./script.sh
```

## Run Script(Beta) Full
Este script si realiza todo el proceso y no es necesario hacer sudo docker build... para construir las imagenes de docker
```bash
>bash ./script_full.sh
```

## Correr proyecto localmente
### Backend
Acceder a backend/app/main.py poner la variables local en True
Modificar las demas variables a conveniencia

#### Para correr 1 server:
```bash
>cd backend/app
>uvicorn main:app --host 0.0.0.0 --port 10000
```

#### Para correr mas de 1 server:
abrir archivo main.py y en la variable port asignar el valor del puerto del nuevo servidor a correr y escribir en la consola el mismo comando pero cambian su puerto.

Por ejemplo, si deseamos crear los servidores con puertos 10001 y 10002, ademas el servidor que creamos anteriormente(que seria el coordinador) hacemos:
Primeramente cambiamos la variable port del archivo main.py a 10001 

```python
server = 'localhost'
port = 10001 # Correrlo local
```

y hacemos:
```bash
>cd backend/app
>uvicorn main:app --host 0.0.0.0 --port 10001
```

Luego cambiamos la variable port del archivo main.py a 10002 
```python
server = 'localhost'
port = 10002 # Correrlo local
```


y hacemos:
```bash
>cd backend/app
>uvicorn main:app --host 0.0.0.0 --port 10002
```