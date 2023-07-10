# Distributed Search Engine

#### @Krtucho Carlos Carret Miranda - C412
#### @prp97 Paula Rodriguez Perez - C412
#### @Selleen Roxana Pena Mendieta - C412

# Documentacion

## Arquitectura

Se implemento una arquitectura Publisher/Subscriber(Publicador/Subscriptor) donde todos los servidores van a estar a la espera de nuevas notificaciones, las cuales seran peticiones de alguna consulta por un nombre de un archivo o el contenido del mismo.

Tambien se impolementa una arquitectura peer-to-peer en forma de anillo haciendo uso de Chord, para la organizacion de todos los nodos en la red y la replicacion de la informacion.

## Peticiones y Comunicacion

Se utilizo la libreria de fastapi para crear los endpoints que nos permitiran a traves de conexiones http comunicar a todos los servidores. Se crean varias rutas, algunas para las consultas(query), otras para la comunicacion entre servidores pertenecientes a la red de Chord, otros para la replicacion entre estos servidores de la red Chord y otros para el manejo de descarga y subida de archivos.

## Creacion de los nodos

La clase ChordNode crea una instancia de nodo perteneciente a la red de Chord, en cada servidor que se corra(contenedor de Docker). Cada uno de estos nodos trae consigo una instancia de la clase channel(Canal de comunicacion entre los nodos de la red de Chord). El nodo principal(el coordinador que se supone q nunca se muera) tendra una instancia de channel que guardara constantemente los nodos que estan vivos, a cada x cantidad de segundos este servidor comprobara que los nodos sigan levantados y actualizara el diccionario de nodos levantados consecuentemente. Todos los demas nodos que no sean exactamente el nodo coordinador le haran peticiones a este y actualizaran su diccionario o lista de nodos que se encuentran actualmente en la red comunicandose por este canal de la clase Channel. El endpoint que se crea para preguntar por todos los archivos es el terminado en get_members.

Se pueden tener varios servidores coordinadores en la red. Todos realizan la misma funcion, lo que cuando van a verificar quien esta vivo en la red, entre ellos se sincronizan y saben ver quien esta vivo en el mismo intervalo de tiempo.

## Coordinación

Existe un servidor principal que sera el primero en conectarse a la red y se espera(segun lo que se informo) que no se le desconecte. Este funciona como canal de comunicacion entre los nodos que se encuentran en la red de Chord para estos saber cuales nodos se encuentran vivos, asi como sus respectivos ids.

## Replicacion

Ya que cada nodo conoce en cada instante su id y los nodos que se encuentran en la red, este sabe quien es su sucesor. Al entrar en la red cada nodo procede a replicar su informacion con su sucesor, constentemente este verifica que su sucesor se encuentre activo. Al terminar de replicarse envia un mensaje a su sucesor de que ya se ha replicado y que es su predecesor, de esta forma el sucesor se entera de que alguien replico su informacion en el y entonces a cada x cantidad de segundos este sucesor verifica que su precesesor siga vivo. En caso de carse el predecesor la informacion replicada en el sucesor ahora pasa a formar parte del sucesor y este busca replicarse en su sucesor y asi se repite el proceso por cada nodo. Tambien, recalcar que constantemente cada nodo verifica que no se haya caido su sucesor que tiene la info replicada para entonces.

## Tolerancia a fallos

Cada vez que se realiza alguna peticion a un servidor y este no responde, se utilizan vias para evitar que deje de funcionar el servidor desde donde se crea la peticion. Por ejemplo:

- Si se cae un nodo, su informacion ya fue replicada y se le informa lo antes posible a los demas nodos de la red que ese nodo abandono la red. Luego, su id quedaria libre y tambien se actualizarian en todos los servidores las listas de nodos que se encuentran activos en la red.
- Si se cae el sucesor, este nodo busca un nuevo sucesor.
- Si se cae el predecesor, la informacion del mismo ahora forma parte del sucesor.

Lideres
- Si se cae un servidor que es lider, todos los que lo tenian a el como su lider buscaran a un nuevo lider. Para ello primeramente cada uno de los nodos pregunta si existe otro lider en su lista de lideres conocidos. Sino existe pregunta a todos los servidores de la red que se encuentren en cierto rango de ip si conocen a alguien que sea lider. Si lo conocen, este pasa a ser su nuevo lider; sino, por cada uno de los nodos de la red que esten vivos se va buscando el de mayor id, este nodo sera el nuevo lider. En caso de que solamente se encuentre un nodo en la red preguntando a todos los demas nodos y ninguno le responda, este nodo pasa a ser lider de si mismo y de toda la red en general.
- Para garantizar que si se desconecta gran parte de la red y la misma luego se une aun continuen funcionando nuestros servidores, se lleva a cabo un proceso de descubrimiento de los nodos en la red por parte de los lideres. Este proceso de descubrimiento consiste en pasar preguntando a todos los nodos de la red en cierto rango de ip si se encuentran vivos. Si responden se actualiza la lista de nodos vivos, ademas se pregunta si son lideres. Si lo son, se agragan a la lista de lideres conocidos de este nodo.

## Inicio Rapido(Quick Start)

## Para correr rapidamente un servidor de backend en una red que creemos
### Primero sera necesario instalar Docker
https://www.docker.com/

### Descargar Python e instalar las libreria de nltk
https://www.python.org/downloads/
https://www.nltk.org/install.html

### Documentos de nltk
Descargar documentos de nltk y copiarlos a la carpeta 

/home/<user_name>/nltk_data

### Crear Red de Docker

```bash
>sudo docker network create fastapi-quasar
```
### Buscar info de la red y Correr Servidor Backend

```bash
>sudo docker network inspect fastapi-quasar
```

Con el comando anterior les va a salir info de la red. Buscan en el array de Config el campo de Gateway y poner ip a los servidores que se creen con la imagen que se crea a continuacion que pertenezcan a este mismo rango:

```bash
>cd backend
>sudo docker build -t fastapi-files .
```

Esto anterior para crear la imagen y luego la corremos:

```bash
>sudo docker run -it --rm --name backend --network $fastapi-quasar --ip $gateway$ip -e FIRST_SERVER=ip_de_server_principal -e IP=$gateway$ip -e PORT=8000 -e LOCAL=False fastapi-files
```

Variables de entorno y parametros que nos interesan:
```
--name <nombre_del_servidor>
--network <nombre_de_la_red_de_Docker>
--ip <ip_del_servidor_en_la_red_de_Docker>
-e FIRST_SERVER=<ip_de_server_principal> 
-e IP=<ip_del_servidor_en_red_de_Docker>
-e PORT=<puerto_del_servidor_en_red_de_Docker>
-e LOCAL=<correr_server_de_forma_local_o_en_Docker>
```

### Correr Servidor Frontend
Primeramente creamos la imagen de Docker:
```bash
>cd frontend
>sudo docker build -t dockerize-quasar-ip .
```

Luego corremos nuestro servidor de frontend o visual con:

```bash
>sudo docker run -d --rm --name frontend --network fastapi-quasar --ip $gateway$ip -e API_SERVER=$server_ip:$server_port dockerize-quasar-ip
```
Variables de entorno y parametros que nos interesan:
```
--name <nombre_del_servidor>
--network <nombre_de_la_red_de_Docker>
--ip <ip_del_servidor_en_la_red_de_Docker>
-e API_SERVER=<ip_del_servidor_backend_para_peticiones> 
```

Para mas detalles ver la seccion siguiente

# Mas Detalles

## Backend
Se iran describiendo las variables de entorno que se le pueden pasar al servidor de Backend 1 a una y al final de la seccion se presentara un listado de las mismas.

- El servidor esta configurado para intentar conectarse a un servidor principal <FIRST_SERVER> y cada vez que vaya a intentar conectarse con ciertos servidores para descrubrirlos lo intentara hacer por el puerto <DEFAULT_LEADER_PORT>.
- Por defecto la funcion de hash para otorgar un ID a los nodos es la funcion random de Python. Pero si se desea utilizar una funcion de hash sha1 se puede pasar la misma a <HASH_TYPE>
- Los servidores guardaran sus archivos en la ruta /txts/ pero con la variable <FILE_PATH> esto se puede modificar.
- Entre cada iteracion de nuestro hilo principal se hace una pequenna pausa para que no se esten haciendo peticiones todo el tiempo. Esto se puede modificar con <TIMEOUT>


Ahora las variables que ya vimos
- <FIRST_SERVER> es utilizado como el primer servidor al que intentara conectarse un nodo.
- Sera necesario suministrar una <IP>(ip) y un <PORT> (port) a nuestro algoritmo, que este debera de coincidir con el que le pasamos a la red de Docker
- Es muy importancia poner el valor de False a la variable <LOCAL> porque en caso de no hacerlo nuestro servidor funcionara de forma local, en este caso solo tendra comunicacion entre si mismo con sus respectivos puertos.

Luego las variables que tenemos son:
```
--name <nombre_del_servidor>
--network <nombre_de_la_red_de_Docker>
--ip <ip_del_servidor_en_la_red_de_Docker>
-e FIRST_SERVER=<ip_de_server_principal> 
-e IP=<ip_del_servidor_en_red_de_Docker>
-e PORT=<puerto_del_servidor_en_red_de_Docker>
-e LOCAL=<correr_server_de_forma_local_o_en_Docker>
-e DEFAULT_LEADER_PORT=<puerto_por_defecto_de_otros_servers>
-e HASH_TYPE=<tipo_hash_para_id_de_nodos_de_chord>
```

Comandos de docker y orden en que deberian ejecutarse:

```bash
>cd backend

>sudo docker build -t fastapi-files .

>sudo docker run -it --rm --name backend --network $fastapi-quasar --ip $gateway$ip -e FIRST_SERVER=ip_de_server_principal -e IP=$gateway$ip -e PORT=8000 -e LOCAL=False -v $path_donde_tengan_la_carpeta_nltk_data>:/usr/share/nltk_data fastapi-files
```

## Frontend
Hecho en Vue-Quasar
https://quasar.dev/

Variables Para el frontend:
- Todo servidor de frontend tiene un servidor de backend asociado que sera necesario asignarselo con <API_SERVER>. Cabe destacar que en caso de asignarselo los resultados pueden ser nulos o catastroficos.

Luego a modo de resumen, para el frontend:
```
-e API_SERVER=<ip_del_servidor_backend_para_peticiones>
```

```bash
>cd frontend

>sudo docker build -t dockerize-quasar-ip .

>sudo docker run -d --rm --name frontend --network fastapi-quasar -e API_SERVER=$server_ip:$server_port dockerize-quasar-ip
```

## Network
Comandos de Docker para probar por separado a unir y desconectar algun que otro servidor de la red, asi como otras funcionalidades:
```bash
>sudo docker network create fastapi-quasar

>sudo docker network ls

>sudo docker network inspect bridge

>sudo docker network inspect fastapi-quasar

>sudo docker network connect fastapi-quasar backend

>sudo docker network connect fastapi-quasar frontend
```

## Run Script(Beta)

Primeramente construir las imagenes. Luego este script nos creara varios servidores de backend y 1 server de frontend:

```bash
>bash ./script.sh <servers_amount>
```

Donde <servers_amount> sera la cantidad de servidores de backend que queremos levantar

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
### Frontend

Una vez tengamos creado uno o varios servidores de Backend pasamos a instalar las dependencias necesarias y luego podemos correro nuestro servidor Frontend. En caso de no querer hacerlo por esa via igual podemos utilizar Docker. Esta vez con Docker el comando sera mas sencillo.

```bash
>cd frontend
>sudo docker build -t dockerize-quasar-ip .
>sudo docker run -it --name frontend --rm -e API_SERVER=http://127.0.0.1:10000 dockerize-quasar-ip
```

Asumiendo que se levanto el server en en 127.0.0.1:10000
