import re
from math import log

import dataset
import document
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
        self.sim = dict()

        # quitar si hay una forma de saber el total de documentos!!!
        # guarda todos los documentos
        self.docs = []

        # guarda el idf de los términos
        # {term: idf}
        self.term_idf = dict()


    def query_cont(self, query: str):
        """
        Calcula el idf de los términos de la consulta
        """
        terms_freq = self.get_frequency(self.normalize(query))

        max = self.get_max_frequency(terms_freq)

        for term in terms_freq:
            idf = 0

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
            self.docs.append((id, doc))

            terms_freq = self.get_frequency(self.normalize(doc))
            max = self.get_max_frequency(terms_freq)

            for term in terms_freq:
                freq = terms_freq[term]
                tf = terms_freq[term]/max
                doc_1 = document.Document(freq, tf, 0)

                if not self.doc_terms.get(term):
                    self.doc_terms[term] = {id: doc_1}
                else:
                    self.doc_terms[term][id] = doc_1

        for term in self.doc_terms:
            for doc in self.doc_terms[term]:
                self.term_idf[term] = log(
                    len(self.docs) / len(self.doc_terms[term]), 10)
                self.doc_terms[term][doc].w = self.doc_terms[term][doc].tf * self.term_idf[term]


    def similarity(self):
        """
        Calcula la similitud entre la consulta y el documento
        """

        sim_1 = dict()
        aux_1 = dict()

        for term in self.doc_terms:
            if term in self.query_terms:
                aux_1[term] = self.query_terms[term]
            else:
                aux_1[term] = 0

        for term in aux_1:
            for doc in self.doc_terms[term]:
                if not sim_1.get(doc):
                    sim_1[doc] = {'wiq2': pow(aux_1[term], 2), 'wij2': pow(
                        self.doc_terms[term][doc].w, 2), 'wijxwiq': aux_1[term] * self.doc_terms[term][doc].w}
                else:
                    sim_1[doc]['wiq2'] += pow(aux_1[term], 2)
                    sim_1[doc]['wij2'] += pow(self.doc_terms[term]
                                              [doc].w, 2)
                    sim_1[doc]['wijxwiq'] += aux_1[term] * self.doc_terms[term][doc].w

        for doc in sim_1:
            if pow(sim_1[doc]['wiq2'], 1/2) * pow(sim_1[doc]['wij2'], 1/2) != 0:
                self.sim[doc] = round(
                    sim_1[doc]['wijxwiq'] / (pow(sim_1[doc]['wiq2'], 1/2) * pow(sim_1[doc]['wij2'], 1/2)), 3)
            else:
                self.sim[doc] = 0


    def ranking(self, query: str) -> list:
        """
        Llama a query_cont para hallar los pesos de la consulta
        después a similarity para ver la similitud con los documentos
        devuelve el ranking
        """

        self.clean_query_data()

        self.query_cont(query)

        self.similarity()

        sim_1 = dict()

        for doc in self.sim:
            if self.sim[doc] > 0:
                sim_1[doc] = self.sim[doc]

        rank = sorted(sim_1.items(), key=lambda x: x[1], reverse=True)

        return rank


    def clean_query_data(self):
        self.query_terms.clear()
        self.sim.clear()



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