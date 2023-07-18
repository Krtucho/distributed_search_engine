from servers import *

create_servers_file("172.21.0.2", "172.21.0.20", 8000)

servers_list = create_addresses(load_servers())

print(servers_list)

#sudo docker run -it --rm --name backend --network fastapi-quasar --ip 172.21.0.2 -e FIRST_SERVER=172.21.0.2 -e IP=172.21.0.2 -e PORT=8000 -e LOCAL=False -v /home/krtucho/nltk_data:/usr/share/nltk_data fastapi-files
# sudo docker run -d --rm --name frontend --network fastapi-quasar -e API_SERVER=$server_ip:$server_port dockerize-quasar-ip

INFO:     127.0.0.1:36860 - "GET /api/update_replay_data/document_1.txtdocument_2.txtdocument_3.txtdocument_4.txtdocument_5.txtdocument_6.txtdocument_7.txtdocument_8.txtdocument_9.txtdocument_10.txtdocument_11.txtdocument_12.txtdocument_13.txtdocument_14.txtdocument_15.txtdocument_16.txtdocument_17.txtdocument_18.txtdocument_19.txtdocument_20.txtdocument_21.txtdocument_22.txtdocument_23.txtdocument_24.txt HTTP/1.1" 500 Internal Server Error
ERROR:    Exception in ASGI application
Traceback (most recent call last):
  File "/home/krtucho/.local/lib/python3.7/site-packages/uvicorn/protocols/http/h11_impl.py", line 429, in run_asgi
    self.scope, self.receive, self.send
  File "/home/krtucho/.local/lib/python3.7/site-packages/uvicorn/middleware/proxy_headers.py", line 78, in __call__
    return await self.app(scope, receive, send)
  File "/home/krtucho/.local/lib/python3.7/site-packages/fastapi/applications.py", line 276, in __call__
    await super().__call__(scope, receive, send)
  File "/home/krtucho/.local/lib/python3.7/site-packages/starlette/applications.py", line 122, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/home/krtucho/.local/lib/python3.7/site-packages/starlette/middleware/errors.py", line 184, in __call__
    raise exc
  File "/home/krtucho/.local/lib/python3.7/site-packages/starlette/middleware/errors.py", line 162, in __call__
    await self.app(scope, receive, _send)
  File "/home/krtucho/.local/lib/python3.7/site-packages/starlette/middleware/cors.py", line 83, in __call__
    await self.app(scope, receive, send)
  File "/home/krtucho/.local/lib/python3.7/site-packages/starlette/middleware/exceptions.py", line 79, in __call__
    raise exc
  File "/home/krtucho/.local/lib/python3.7/site-packages/starlette/middleware/exceptions.py", line 68, in __call__
    await self.app(scope, receive, sender)
  File "/home/krtucho/.local/lib/python3.7/site-packages/fastapi/middleware/asyncexitstack.py", line 21, in __call__
    raise e
  File "/home/krtucho/.local/lib/python3.7/site-packages/fastapi/middleware/asyncexitstack.py", line 18, in __call__
    await self.app(scope, receive, send)
  File "/home/krtucho/.local/lib/python3.7/site-packages/starlette/routing.py", line 718, in __call__
    await route.handle(scope, receive, send)
  File "/home/krtucho/.local/lib/python3.7/site-packages/starlette/routing.py", line 276, in handle
    await self.app(scope, receive, send)
  File "/home/krtucho/.local/lib/python3.7/site-packages/starlette/routing.py", line 66, in app
    response = await func(request)
  File "/home/krtucho/.local/lib/python3.7/site-packages/fastapi/routing.py", line 238, in app
    dependant=dependant, values=values, is_coroutine=is_coroutine
  File "/home/krtucho/.local/lib/python3.7/site-packages/fastapi/routing.py", line 165, in run_endpoint_function
    return await run_in_threadpool(dependant.call, **values)
  File "/home/krtucho/.local/lib/python3.7/site-packages/starlette/concurrency.py", line 41, in run_in_threadpool
    return await anyio.to_thread.run_sync(func, *args)
  File "/home/krtucho/.local/lib/python3.7/site-packages/anyio/to_thread.py", line 32, in run_sync
    func, *args, cancellable=cancellable, limiter=limiter
  File "/home/krtucho/.local/lib/python3.7/site-packages/anyio/_backends/_asyncio.py", line 937, in run_sync_in_worker_thread
    return await future
  File "/home/krtucho/.local/lib/python3.7/site-packages/anyio/_backends/_asyncio.py", line 867, in run
    result = context.run(func, *args)
  File "/home/krtucho/School/4/SD/Project/distributed_search_engine/backend/app/main.py", line 734, in api_update_replay_data
    return update_replay_data(doc)
  File "/home/krtucho/School/4/SD/Project/distributed_search_engine/backend/app/main.py", line 761, in update_replay_data
    database.remove_file(i)
  File "/home/krtucho/School/4/SD/Project/distributed_search_engine/backend/app/database.py", line 34, in remove_file
    self.execute_query(delete_file, "")
  File "/home/krtucho/School/4/SD/Project/distributed_search_engine/backend/app/database.py", line 97, in execute_query
    self.close_connection()
  File "/home/krtucho/School/4/SD/Project/distributed_search_engine/backend/app/database.py", line 51, in close_connection
    self.cursor.close()
sqlite3.ProgrammingError: SQLite objects created in a thread can only be used in that same thread. The object was created in thread id 139815035053824 and this is thread id 139815026661120.