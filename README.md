# distributed_search_engine

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