# from dataset import Dataset
from vector_model import VectorModel

from pathlib import Path
import database
import os

from typing import List

# dataset = Dataset()

# dataset.build_dataset('cranfield')

vm = VectorModel()

def convert_file_to_text(file_path: Path) -> str:
    _file = open(file_path, 'r')
    text = "".join(_file.readlines()) 
    _file.close()

    return text 

# path = Path("txts") #  console

path = Path("backend/app/txts") # play

print(path)

# files_name=list(path.iterdir())  

# for i in files_name:
#     print(i)
# print(files_name)

# print(convert_file_to_text("/document_1.txt"))

# print(convert_file_to_text(files_name[0]))

files_name=["document_1.txt","document_2.txt","document_102.txt","document_56.txt","document_387.txt"]

documents_list = database.convert_text_to_text_class(path=path, files_name=files_name)

for i in documents_list:
    print(i.body)

vm.doc_terms_data(documents_list)

query = "heat"

print(vm.run(query))

##########################

# vm.doc_terms_data(dataset.documents_cont[:10])

# query = dataset.print_query_data('cranfield')

# # print(vm.run(query[1])[:6])

# vm.doc_terms_data(dataset.documents_cont[10:])

# print(vm.run(query[1])[:6])

# uvicorn main:app --host 0.0.0.0 --port 10000
# https://localhost:100000/files/search{