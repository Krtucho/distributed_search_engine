from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

# Api Servers


app = FastAPI()


files = [
    {
    "id":0, 
    "file":{"file_name": "Archivo de Roxana", "server_number": 0}
    },
    {
    "id":1, 
    "file":{"file_name": "Archivo de Paula", "server_number": 0}
    },
    {
    "id":2, 
    "file":{"file_name": "Archivo de Krtucho", "server_number": 0}
    }
]


def search_file(id):
    return [file["file"] for file in files if file["id"] == id]


class File(BaseModel):
    file_name: str
    server_number: int
    # paginas:int
    # editorial: Optional[str]


@app.get("/")
def index():
    return {"msg": "Hello World!"}


@app.get('/files/{id}')
def show_file(id: int):
    return search_file(id)#{"data": id}


@app.post("/files")
def add_file(file: File):
    return {"msg": f"File {file.file_name} a"}