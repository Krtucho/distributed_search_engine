from math import log
import re
import numpy as np
import nltk
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import wordnet, stopwords


class VectorModel:
    def __init__(self):
        super().__init__()
        
        # Términos del contenido de los documentos
        # {terms: {docs: {freq, tf, idf, w}}}    
        self.doc_cont_terms = dict()

        # Términos de los nombres de los documentos 
        # {terms: {docs: {freq, tf, idf, w}}}   
        self.doc_name_terms = dict()

        # Términos de la consulta
        # {terms: {w}}
        self.query_terms = dict()

        # similitud entre los términos de la consulta y los términos dentro del contenido de los documentos
        self.query_cont_sim = dict()

        # similitud entre los términos de la consulta y los términos en el nombre de los documentos
        self.query_name_sim = dict()


    def query_cont(self, query: str):
        """
        Calcula el idf de los términos de la consulta
        """
        terms_freq = self.get_frequency(self.normalize(query))

        max = self.get_max_frequency(terms_freq)

        for term in terms_freq:
            idf = 0
            for freq in self.doc_cont_terms[term].values():
                idf = freq['idf']
            if max != 0:
                self.query_terms[term] = (
                    0.5 + (0.5) * ((terms_freq[term])/(max)))*idf
            else:
                self.query_terms[term] = 0


    def doc_name(self, doc_names: list):
        """
        Calcula freq, tf, idf de los términos en el nombre de los documentos
        """
        for doc in doc_names:

            terms_freq = self.get_frequency(self.normalize(doc))

            max = self.get_max_frequency(terms_freq)

            for term in terms_freq:
                if not self.doc_name_terms.get(term):
                    self.doc_name_terms[term] = {doc['id']: {
                        'freq': terms_freq[term], 'tf': terms_freq[term]/max, 'idf': 0, 'w': 0}}
                else:
                    self.doc_name_terms[term][doc['id']] = {
                        'freq': terms_freq[term], 'tf': terms_freq[term]/max, 'idf': 0, 'w': 0}

        for term in self.doc_name_terms:
            for doc in self.doc_name_terms[term]:
                self.doc_name_terms[term][doc]['idf'] = log(
                    len(doc_names) / len(self.doc_name_terms[term]), 10)
                self.doc_name_terms[term][doc]['w'] = self.doc_name_terms[term][doc]['tf'] * \
                    self.doc_name_terms[term][doc]['idf']


    def doc_data(self, doc_cont: list):
        """
        Calcula freq, tf, idf de los términos en el contenido de los documentos
        """
        for doc in doc_cont:

            terms_freq = self.get_frequency(self.normalize(doc))

            max = self.get_max_frequency(terms_freq)

            for term in terms_freq:
                if not self.doc_cont_terms.get(term):
                    self.doc_cont_terms[term] = {doc['id']: {
                        'freq': terms_freq[term], 'tf': terms_freq[term]/max, 'idf': 0, 'w': 0}}
                else:
                    self.doc_cont_terms[term][doc['id']] = {
                        'freq': terms_freq[term], 'tf': terms_freq[term]/max, 'idf': 0, 'w': 0}

        for term in self.doc_cont_terms:
            for doc in self.doc_cont_terms[term]:
                self.doc_cont_terms[term][doc]['idf'] = log(
                    len(doc_cont) / len(self.doc_cont_terms[term]), 10)
                self.doc_cont_terms[term][doc]['w'] = self.doc_cont_terms[term][doc]['tf'] * \
                    self.doc_cont_terms[term][doc]['idf']


    def normalize(self, text: str) -> list:
        """
        Elimina stopwords, .... 
        """
        return [self.lexemizer.lemmatize(token.lower()) for token in re.split(r'\W+', text) if token not in self.stopwords]


    def get_frequency(elements: list) -> dict:
        """
        Calcula la frecuencia de los términos
        """
        count = dict()

        for element in elements:
            if not count.get(element):
                count[element] = 1
            else:
                count[element] += 1

        return count


    def get_max_frequency(count: dict) -> int:
        """
        Halla la frequencia máxima entre los términos
        """
        max = 0

        for term in count:
            if max < count[term]:
                max = count[term]

        return max


    def similiraty(self):
        """
        Calcula la similitud entre la consulta y el contenido de los documentos
        y entre la consulta y el nombre de los archivos
        """

        sim_data = dict()
        aux_1 = dict()

        # Similitud con el contenido del documento
        for term in self.doc_cont_terms:
            if term in self.query_terms:
                aux_1[term] = self.query_terms[term]
            else:
                aux_1[term] = 0

        for term in aux_1:
            for doc in self.doc_cont_terms[term]:
                if not sim_data.get(doc):
                    sim_data[doc] = {'wiq2': pow(aux_1[term], 2), 'wij2': pow(
                        self.doc_cont_terms[term][doc]['w'], 2), 'wijxwiq': aux_1[term] * self.doc_cont_terms[term][doc]['w']}
                else:
                    sim_data[doc]['wiq2'] += pow(aux_1[term], 2)
                    sim_data[doc]['wij2'] += pow(self.doc_cont_terms[term]
                                            [doc]['w'], 2)
                    sim_data[doc]['wijxwiq'] += aux_1[term] * \
                        self.doc_cont_terms[term][doc]['w']

        for doc in sim_data:
            if pow(sim_data[doc]['wiq2'], 1/2) * pow(sim_data[doc]['wij2'], 1/2) != 0:
                self.query_cont_sim[doc] = round(
                    sim_data[doc]['wijxwiq'] / (pow(sim_data[doc]['wiq2'], 1/2) * pow(sim_data[doc]['wij2'], 1/2)), 3)
            else:
                self.query_cont_sim[doc] = 0

        sim_name = dict()
        aux_2 = dict()

        # Similitud con el nombre del documento
        for ter in self.doc_name_terms: 
            if term in self.query_terms:
                aux_2[term] = self.query_terms[term]
            else:
                aux_2[term] = 0

        for term in aux_2:
            for doc in self.doc_name_terms[term]:
                if not sim_name.get(doc):
                    sim_name[doc] = {'wiq2': pow(aux_2[term], 2), 'wij2': pow(
                        self.doc_name_terms[term][doc]['w'], 2), 'wijxwiq': aux_2[term] * self.doc_name_terms[term][doc]['w']}
                else:
                    sim_name[doc]['wiq2'] += pow(aux_2[term], 2)
                    sim_name[doc]['wij2'] += pow(self.doc_name_terms[term]
                                            [doc]['w'], 2)
                    sim_name[doc]['wijxwiq'] += aux_2[term] * \
                        self.doc_name_terms[term][doc]['w']

        for doc in sim_name:
            if pow(sim_name[doc]['wiq2'], 1/2) * pow(sim_name[doc]['wij2'], 1/2) != 0:
                self.query_name_sim[doc] = round(
                    sim_name[doc]['wijxwiq'] / (pow(sim_name[doc]['wiq2'], 1/2) * pow(sim_name[doc]['wij2'], 1/2)), 3)
            else:
                self.query_name_sim[doc] = 0


    def ranking(self): 
        query_cont_sim_1 = dict()
        query_name_sim_1 = dict()

        for doc in self.query_cont_sim:
            if self.query_cont_sim[doc] > 0:
                query_cont_sim_1[doc] = self.query_cont_sim[doc]

        rank_data = sorted(query_cont_sim_1.items(), key=lambda x: x[1], reverse=True)
        
        for doc in self.query_name_sim:
            if self.query_name_sim[doc] > 0:
                query_name_sim_1[doc] = self.query_name_sim[doc]

        rank_name = sorted(query_name_sim_1.items(), key=lambda x: x[1], reverse=True) 
        
        
        return rank_name, rank_data

    