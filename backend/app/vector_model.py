import re
from math import log

import nltk
from nltk.corpus import stopwords, wordnet
from nltk.stem.wordnet import WordNetLemmatizer

# import nltk
# nltk.data.path.append('backend/app/nltk_data')
# nltk.data.path = ['nltk_data']
# from nltk.corpus import stopwords
# stop_words = stopwords.words('english')
# from nltk.stem.wordnet import WordNetLemmatizer

from database import Text
from typing import List

# nltk.download('stopwords')
# nltk.download('wordnet')

class Document:
    def __init__(self, freq: int, tf: float, w: float):
        super().__init__()

        self.freq = freq
        self.tf = tf
        self.w = w


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
        self.query_sim = dict()

        # quitar si hay una forma de saber el total de documentos!!!
        # guarda todos los documentos
        self.docs = 0

        # guarda el idf de los términos
        # {term: idf}
        self.term_idf = dict()


    def run(self, query: str) -> list:
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


    def doc_terms_data(self, doc_cont: List[Text]):
        """
        Calcula freq, tf, idf de los términos en el contenido de los documentos
        """

        for doc in doc_cont:
            self.docs += 1

            if doc.body == '':
                continue

            terms_freq = self.get_frequency(self.normalize(doc.body))
            max = self.get_max_frequency(terms_freq)

            for term in terms_freq:
                freq = terms_freq[term]
                tf = terms_freq[term]/max
                doc_1 = Document(freq, tf, 0)

                if not self.doc_terms.get(term):
                    self.doc_terms[term] = {doc.id: doc_1}
                else:
                    self.doc_terms[term][doc.id] = doc_1

        for term in self.doc_terms:
            self.term_idf[term] = log(
                    self.docs / len(self.doc_terms[term]), 10)

            for doc in self.doc_terms[term]:                
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
                self.query_sim[doc] = round(
                    sim_1[doc]['wijxwiq'] / (pow(sim_1[doc]['wiq2'], 1/2) * pow(sim_1[doc]['wij2'], 1/2)), 3)
            else:
                self.query_sim[doc] = 0


    def ranking(self) -> list:
        """
        Llama a query_cont para hallar los pesos de la consulta
        después a similarity para ver la similitud con los documentos
        devuelve el ranking
        """

        sim = []

        for doc in self.query_sim:
            if self.query_sim[doc] > 0:
                sim.append((doc, self.query_sim[doc]))

        rank = sorted(sim, key=lambda x: x[1], reverse=True)

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
        
        # return [WordNetLemmatizer().lemmatize(token.lower()) for token in re.split(r'\W+', text) if token not in set(stop_words)]


    def delete_doc(self, id: str):
        self.docs -= 1

        # print(self.term_idf)
        
        for term in self.doc_terms:
            if self.doc_terms[term].get(id):
                del self.doc_terms[term][id]

        new_dict = self.doc_terms.copy()

        for term in self.doc_terms:
            if len(self.doc_terms[term]) == 0:
                del new_dict[term]

            else:
                self.term_idf[term] = log(
                        self.docs / len(self.doc_terms[term]), 10)

                for doc in self.doc_terms[term]:                
                    self.doc_terms[term][doc].w = self.doc_terms[term][doc].tf * self.term_idf[term]

        self.doc_terms = new_dict

    def delete_doc_list(self, docs_to_remove: List[Text]):
        self.docs -= len(docs_to_remove)
        print("**************!!!!!!!!!** Entro en docs to remove ")

        # print(self.term_idf)
        
        for doc in docs_to_remove:
            for term in self.doc_terms:
                if self.doc_terms[term].get(doc.id):
                    del self.doc_terms[term][doc.id]

        new_dict = self.doc_terms.copy()

        for term in self.doc_terms:
            if len(self.doc_terms[term]) == 0:
                del new_dict[term]

            else:
                self.term_idf[term] = log(
                        self.docs / len(self.doc_terms[term]), 10)

                for doc in self.doc_terms[term]:                
                    self.doc_terms[term][doc].w = self.doc_terms[term][doc].tf * self.term_idf[term]

        self.doc_terms = new_dict
