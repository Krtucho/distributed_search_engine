from vector_model import VectorModel

docs = [(1, "leon leon leon"), (2, "leon leon leon zorro"), (3, "leon zorro nutria"), (4, "leon leon leon zorro zorro zorro"), (5, "nutria")]

# docs = ["leon leon leon", "leon leon leon zorro", "leon zorro nutria", "leon leon leon zorro zorro zorro", "nutria"]

vm = VectorModel()

vm.doc_terms_data(docs)

# for term in vm.doc_terms:
#     for doc in vm.doc_terms[term]:
#         # print(term)
#         # print(doc)
#         print(term, " ", doc, " freq: ", vm.doc_terms[term][doc].freq," tf: ", vm.doc_terms[term][doc].tf, " w: ", vm.doc_terms[term][doc].w, " idf: ", vm.term_idf[term])
#         print()

query = "nutria"

print(vm.ranking(query))

# term = "leon"
# for doc in vm.doc_terms[term]:
#     # print(term)
#     # print(doc)
#     print(term, " ", doc, " freq: ", vm.doc_terms[term][doc].freq," tf: ", vm.doc_terms[term][doc].tf, " idf: ", vm.doc_terms[term][doc].idf, " w: ", vm.doc_terms[term][doc].w)
#     print()

doc_1 = [(6, "leon nutria")]

# doc_1 = ["leon nutria"]

vm.doc_terms_data(doc_1)

for term in vm.doc_terms:
    for doc in vm.doc_terms[term]:
        # print(term)
        # print(doc)
        print(term, " ", doc, " freq: ", vm.doc_terms[term][doc]['freq']," tf: ", vm.doc_terms[term][doc]['tf'], " w: ", vm.doc_terms[term][doc]['w'], " idf: ", vm.doc_terms[term][doc]['idf'])
        print()


query_1 = "leon nutria"

print(vm.ranking(query_1))