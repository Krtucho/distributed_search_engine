import re

def create_txt_files(filename, path_save):
    with open(filename, 'r') as file:
        data = file.read()
        
    documents = re.split(r'\.I \d+', data)
    documents = [doc.strip() for doc in documents if doc.strip()]
    
    for i, doc in enumerate(documents, start=1):
        doc_id_text = i
        title = re.search(r'\.T\n([\s\S]*?)\.A\n', doc, re.DOTALL)
        author = re.search(r'\.A\n([\s\S]*?)\.B\n', doc, re.DOTALL)
        body = re.search(r'\.W\n(.+)', doc, re.DOTALL)# 
        
        if doc_id_text and title and author and body:
            title_text = title.group(1).strip()
            author_text = author.group(1).strip()
            body_text = body.group(1).strip()
            
            with open(f'{path_save}/document_{doc_id_text}.txt', 'w') as output_file:
                output_file.write(f'ID: {doc_id_text}\n')
                output_file.write(f'Title: {title_text}\n')
                output_file.write(f'Author: {author_text}\n')
                output_file.write(f'Body:\n{body_text}\n')
                
            print(f'Created document_{doc_id_text}.txt')
        else:
            print(f'Skipped document {i} due to missing data.')

path_cran = '/home/roxy/Roxana-linux/SD/distributed_search_engine/processes/collections/cran/cran.all.1400'
path_save = '/home/roxy/Roxana-linux/SD/distributed_search_engine/processes/txts'
create_txt_files(path_cran, path_save)
