import re
from math import log

import nltk
import numpy as np
from nltk.corpus import stopwords, wordnet
from nltk.stem.wordnet import WordNetLemmatizer


class VectorModel:
    def __init__(self):
        super().__init__()

        # Términos del contenido de los documentos
        # {terms: {docs: {freq, tf, idf, w}}}
        self.doc_terms = dict()

        # Términos de la consulta
        # {terms: {w}}
        self.query_terms = dict()

        # similitud entre los términos de la consulta y los términos dentro del contenido de los documentos
        self.query_sim= dict()

        # quitar si hay una forma de saber el total de documentos!!!
        # guarda todos los documentos
        self.docs_count = 0
        # self.docs_count = docs_count
        
        # guarda el idf de los términos
        # {term: idf}
        self.term_idf = dict()


    def run(self, query: str):
        """
        Llama a query_cont para hallar los pesos de la consulta
        después a similarity para ver la similitud con los documentos
        y después llama a ranking
        """
        self.clean_query_data()

        self.query_cont(query)

        self.similarity()

        return self.ranking()


    def query_cont(self, query: str):
        """
        Calcula el idf de los términos de la consulta
        """
        terms_freq = self.get_frequency([term for term in self.normalize(query) if self.doc_terms.get(term)])

        max = self.get_max_frequency(terms_freq)

        
        for term in terms_freq:
            idf= 0

            if term in self.term_idf:
                idf = self.term_idf[term]
                
            if max != 0:
                self.query_terms[term] = (0.5 + (0.5) * ((terms_freq[term])/(max))) * idf
            else:
                self.query_terms[term] = 0
 

    def doc_terms_data(self, doc_cont: list):
        """
        Calcula freq, tf, idf de los términos en el contenido de los documentos
        """

        for id, doc in doc_cont:
            self.docs_count += 1
            
            if doc == '':
                continue

            terms_freq = self.get_frequency(self.normalize(doc))

            max = self.get_max_frequency(terms_freq)

            for term in terms_freq:
                if not self.doc_terms.get(term):
                    self.doc_terms[term] = {id : {'freq': terms_freq[term], 'tf': terms_freq[term]/max, 'w': 0}}
                else:
                    self.doc_terms[term][id] = {'freq': terms_freq[term], 'tf': terms_freq[term]/max, 'w': 0}

        for term in self.doc_terms:
            self.term_idf[term] = log(self.docs_count / len(self.doc_terms[term]), 10)
            
            for doc in self.doc_terms[term]:              
                self.doc_terms[term][doc]['w'] = self.doc_terms[term][doc]['tf'] * self.term_idf[term]


    def similarity(self):
        """
        Calcula la similitud entre la consulta y e documento
        """

        sim = dict()
        aux = dict()

        for term in self.doc_terms:
            if term in self.query_terms:
                aux[term] = self.query_terms[term]
            else:
                aux[term] = 0

        for term in aux:
            for doc in self.doc_terms[term]:
                if not sim.get(doc):
                    sim[doc] = {'wiq2': pow(aux[term], 2), 'wij2': pow(
                        self.doc_terms[term][doc]['w'], 2), 'wijxwiq': aux[term] * self.doc_terms[term][doc]['w']}
                else:
                    sim[doc]['wiq2'] += pow(aux[term], 2)
                    sim[doc]['wij2'] += pow(self.doc_terms[term][doc]['w'], 2)
                    sim[doc]['wijxwiq'] += aux[term] * self.doc_terms[term][doc]['w']

        for doc in sim:
            if pow(sim[doc]['wiq2'], 1/2) * pow(sim[doc]['wij2'], 1/2) != 0:
                self.query_sim[doc] = round(
                    sim[doc]['wijxwiq'] / (pow(sim[doc]['wiq2'], 1/2) * pow(sim[doc]['wij2'], 1/2)), 3)
            else:
                self.query_sim[doc] = 0


    def ranking(self) -> list:
        """
        devuelve el ranking
        """

        sim = dict()

        for doc in self.query_sim:
            if self.query_sim[doc] > 0:
                sim[doc] = self.query_sim[doc]

        rank = sorted(sim.items(), key=lambda x: x[1], reverse=True)

        return rank


    def clean_query_data(self):
        self.query_terms.clear()
        self.query_sim.clear()
    

    def get_frequency(self, elements: list) -> dict:
        count = dict()
        for element in elements:
            if not count.get(element):
                count[element] = 1
            else:
                count[element] += 1
        return count


    def get_max_frequency(self, count: dict) -> int:
        max = 0
        for term in count:
            if max < count[term]:
                max = count[term]
        return max


    def normalize(self, text: str) -> list:
        return [WordNetLemmatizer().lemmatize(token.lower()) for token in re.split(r'\W+', text) if token not in set(stopwords.words('english'))]