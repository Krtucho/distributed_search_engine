import numpy as np
from ir_datasets import load
from ir_datasets.datasets.base import Dataset
import lexemizer


class Dataset:
    def __init__(self):
        self.dataset: Dataset = None

        self.documents_cont: list = None
        self.documents_title: list = None
        self.terms: list = None

        self.docslen: int = 0
        self.dataset_name: str = None
        self.lexemizer = lexemizer.Lexemizer()


    def build_dataset(self, dataset: str):
        '''
        Build the dataset and get the documents
        :param dataset: dataset name
        '''
        self.clean_data()
        self.dataset_name = dataset

        self.documents_cont= []
        self.documents_title= []
        self.dataset: Dataset = load(dataset)

        for doc in self.dataset.docs_iter():
            self.documents_cont.append((doc.doc_id, doc.text))

            self.documents_title.append((doc.doc_id, doc.title))
            
        self.docslen = self.dataset.docs_count()


    def clean_data(self):
        self.dataset: Dataset = None
        if self.documents_cont:
            self.documents_cont.clear()
            self.documents_title.clear()
        if self.terms:
            self.terms.clear()
        self.docslen: int = 0
        self.dataset_name: str = None
        self.lexemizer = lexemizer.Lexemizer()
        

    def get_docs_data(self) -> list:
        return [{'id': data.doc_id, 'text': data.text, 'title': data.title} for data in self.dataset.docs_iter()]


    def get_query_data(dataset: str) -> list:
        '''
        :param dataset: dataset name
        :return: list of queries with their id and text
        '''
        return [{'id': str(id+1), 'query': data.text} for id, data in enumerate(load(dataset).queries_iter())]


    def print_query_data(self, dataset: str) -> list:
        '''
        :param dataset: dataset name
        :return: list of queries with their id and text in a readable format
        '''
        # return [data['id'] + ': ' + data['query'] for data in Dataset.get_query_data(dataset)]
        return [data['query'] for data in Dataset.get_query_data(dataset)]


    def normalize(self, txt: str) -> list:
        """
        Elimina stopwords, .... 
        """
        return self.lexemizer.normalize(document)

