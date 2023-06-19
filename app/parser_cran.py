import re

def get_data_from(filename):
    with open(filename, 'r') as file:
        data = file.read()
        
    documents = re.split(r'\.I \d+', data)
    documents = [doc.strip() for doc in documents if doc.strip()]
    result = []
    for i, doc in enumerate(documents, start=1):
        doc_id_text = i
        title = re.search(r'\.T\n([\s\S]*?)\.A\n', doc, re.DOTALL)
        author = re.search(r'\.A\n([\s\S]*?)\.B\n', doc, re.DOTALL)
        body = re.search(r'\.W\n(.+)', doc, re.DOTALL)
        
        if doc_id_text and title and author and body:
            title_text = title.group(1).strip()
            author_text = author.group(1).strip()
            body_text = body.group(1).strip()
            result.append((doc_id_text, title_text, author_text, body_text))
    return result 
            
def create_txt_files(filename, path_save):
    result = get_data_from(filename)
    for doc in result:
        with open(f'{path_save}/document_{doc[0]}.txt', 'w') as output_file:
            output_file.write(f'ID: {doc[0]}\n')
            output_file.write(f'Title: {doc[1]}\n')
            output_file.write(f'Author: {doc[2]}\n')
            output_file.write(f'Body:\n{doc[3]}\n')
            print(f'Created document_{doc[0]}.txt')

#current_dir = os.path.dirname(os.path.abspath(__file__))
#path_cran = os.path.join(current_dir, "collections/cran/cran.all.1400")
#create_txt_files(path_cran, current_dir)
