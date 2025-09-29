from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def load_and_preprocess(data_dir: str):
    docs = []
    import os

    for file in os.listdir(data_dir):
        if file.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(data_dir, file))
            docs.extend(loader.load())

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800, chunk_overlap=100
    )
    chunks = splitter.split_documents(docs)
    return chunks

if __name__ == "__main__":
    docs = load_and_preprocess("data")
    print(f"✅ Loaded {len(docs)} chunks")
    print("Sample text:", docs[0].page_content[:300])
