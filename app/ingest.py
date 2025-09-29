from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("data/synthetic_healthcare_0001.pdf")
docs = loader.load()

for d in docs[:5]:
    print(d.page_content[:300])
