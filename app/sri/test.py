from dataset import Dataset
from vector_model_copy import VectorModel


dataset = Dataset()

dataset.build_dataset('cranfield')


# vm = VectorModel(dataset.docslen)

# vm.doc_terms_data(dataset.documents_cont)

vm = VectorModel()

vm.doc_terms_data(dataset.documents_cont)

query = dataset.print_query_data('cranfield')

print(query[0])


# for id, rank in vm.ranking(query[0])[:4]:
#     print(dataset.documents_cont[int(id)])

print(vm.ranking(query[0])[:6])

