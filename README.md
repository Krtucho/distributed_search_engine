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

>sudo docker run -it --rm --name backend -e DB_URL=mongodb://db:27017/test -e PORT=10000 fastapi-files

>sudo docker run -it -v /home/krtucho/School/4/SD/Project/distributed_search_engine/backend/app:/code/app --rm --name backend -e DB_URL=mongodb://db:27017/test -e PORT=10000 fastapi-files bash
```

# Frontend
```bash
>sudo docker build -t dockerize-quasar-ip .

>sudo docker run -d --name frontend dockerize-quasar-ip
```

# Network
```bash
>docker network create fastapi-quasar

>docker network connect fastapi-quasar backend

>docker network connect fastapi-quasar frontend
```