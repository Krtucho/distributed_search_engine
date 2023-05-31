import requests

def extract_filename(file_path: str):
    index = len(file_path) -1
    filename = ""
    while file_path[index] != '/' and index >= 0:
        filename = file_path[index] + filename
        index -= 1
    return filename

def download_file(url):
    # url = 'http://localhost:8000/download/main.py'
    kb_size = 2 # 1024 for 1mb
    chunk_size = kb_size * 1024  # Descargar archivos de 1 MB por fragmento

    response = requests.get(url, stream=True)

    file_name = extract_filename(url)
    with open(file_name, 'wb') as f:
        for chunk in response.iter_content(chunk_size):
            if chunk:  # filtra los fragmentos vacios
                f.write(chunk)

    return file_name

# import urllib.request
# req = urllib.request.Request('http://localhost:8000/download/main.py',
#                              headers={'Range': 'bytes=40-'})
# g = urllib.request.urlopen(req)
# f = g.read(100)
# print(f)

# import requests

# headers = {'Range':'bytes=50-'}
# response = requests.get(f'http://localhost:8000/file/main.py', headers=headers, stream=True)

# print(response)
# print(response.text)
# print(response.content)