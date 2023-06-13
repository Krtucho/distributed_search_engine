<<<<<<< HEAD
# distributed_search_engine

```bash
>sudo docker build -t fastapi-files .

>sudo docker run -d --name fastapi-test1 -p 80:80 fastapi-files
```
=======
# distributed_search_engine

```bash
>sudo docker build -t fastapi-files .

>sudo docker run -d --name fastapi-test1 -p 80:80 fastapi-files
```


## Backend

```bash
>cd backend

>sudo docker build -t fastapi-files .

>sudo docker run -d --name backend fastapi-files
```

# Frontend
```bash
>sudo docker build -t dockerize-quasar-ip .

>sudo docker run -d --name frontend dockerize-quasar-ip
```

# Network
```bash
>sudo docker network create fastapi-quasar

>sudo docker network connect fastapi-quasar backend

>sudo docker network connect fastapi-quasar frontend
```
>>>>>>> roxy_branch
