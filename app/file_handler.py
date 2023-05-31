# import requests

# url = 'http://localhost:8000/download/main.py'
# kb_size = 2 # 1024 for 1mb
# chunk_size = kb_size * 1024  # Descargar archivos de 1 MB por fragmento

# response = requests.get(url, stream=True)

# with open('large_file.zip', 'wb') as f:
#     for chunk in response.iter_content(chunk_size):
#         if chunk:  # filtra los fragmentos vacios
#             f.write(chunk)

# import urllib.request
# req = urllib.request.Request('http://localhost:8000/download/main.py',
#                              headers={'Range': 'bytes=40-'})
# g = urllib.request.urlopen(req)
# f = g.read(100)
# print(f)

import requests

headers = {'Range':'bytes=50-'}
response = requests.get(f'http://localhost:8000/file/main.py', headers=headers, stream=True)

print(response)
print(response.text)
print(response.content)