from dataset import Dataset
from vector_model import VectorModel


dataset = Dataset()

dataset.build_dataset('cranfield')

vm = VectorModel()

vm.doc_terms_data(dataset.documents_cont[:10])

query = dataset.print_query_data('cranfield')

print(vm.run(query[1])[:6])

vm.doc_terms_data(dataset.documents_cont[10:])

print(vm.run(query[1])[:6])