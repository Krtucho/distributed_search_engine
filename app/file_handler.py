import requests

url = 'http://localhost:8000/download/main.py'
kb_size = 2 # 1024 for 1mb
chunk_size = kb_size * 1024  # Descargar archivos de 1 MB por fragmento

response = requests.get(url, stream=True)

with open('large_file.zip', 'wb') as f:
    for chunk in response.iter_content(chunk_size):
        if chunk:  # filtra los fragmentos vacios
            f.write(chunk)