# Documentacion
## Arquitectura

Se implemento una arquitectura Publisher/Subscriber(Publicador/Subscriptor) donde todos los servidores van a estar a la espera de nuevas notificaciones, las cuales seran peticiones de alguna consulta por un nombre de un archivo o el contenido del mismo.

Tambien se impolementa una arquitectura peer-to-peer en forma de anillo haciendo uso de Chord, para la organizacion de todos los nodos en la red y la replicacion de la informacion.

## Peticiones y Comunicacion
Se utilizo la libreria de fastapi para crear los endpoints que nos permitiran a traves de conexiones http comunicar a todos los servidores. Se crean varias rutas, algunas para las consultas(query), otras para la comunicacion entre servidores pertenecientes a la red de Chord, otros para la replicacion entre estos servidores de la red Chord y otros para el manejo de descarga y subida de archivos.