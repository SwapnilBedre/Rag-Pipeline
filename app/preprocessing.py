from typing import List, Dict, Any
import os

from langchain.document_loaders import TextLoader, PDFMinerLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter, TokenTextSplitter
from langchain.schema import Document

def load_raw_documents(data_dir: str, extensions: List[str] = [".txt", ".md", ".pdf"]) -> List[Document]:
    """
    Load raw documents from a directory (or a single file) into Document objects.
    Supports .txt, .md, .pdf by default.
    """
    docs: List[Document] = []
    # Option A: use DirectoryLoader (if many files)
    loader = DirectoryLoader(data_dir, glob="**/*", loader_cls=TextLoader, silent_errors=True)
    docs += loader.load()
    # For PDF files, you may add loader for PDF
    pdf_loader = DirectoryLoader(data_dir, glob="**/*.pdf", loader_cls=PDFMinerLoader, silent_errors=True)
    docs += pdf_loader.load()
    return docs

def preprocess_and_chunk(
    docs: List[Document],
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    separators: List[str] = None
) -> List[Document]:
    """
    Preprocess docs: split into smaller chunks with overlap.
    Returns new list of Documents (chunked pieces) preserving metadata.
    """
    if separators is None:
        separators = ["\n\n", "\n", " ", ""]
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=separators
    )
    chunked_docs: List[Document] = []
    for doc in docs:
        # if the document is already small enough, you may skip splitting
        splits = text_splitter.split_text(doc.page_content)
        for chunk in splits:
            chunked_docs.append(
                Document(page_content=chunk, metadata=doc.metadata)
            )
    return chunked_docs

def filter_documents(docs: List[Document], min_length: int = 50) -> List[Document]:
    """
    Optional: remove chunks that are too small or not meaningful.
    """
    filtered: List[Document] = []
    for d in docs:
        if len(d.page_content.strip()) < min_length:
            continue
        filtered.append(d)
    return filtered

def load_and_preprocess_pipeline(
    data_dir: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    min_length: int = 50
) -> List[Document]:
    raw = load_raw_documents(data_dir)
    chunked = preprocess_and_chunk(raw, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    filtered = filter_documents(chunked, min_length=min_length)
    return filtered

if __name__ == "__main__":
    # Example usage
    data_directory = "data/"  # path to your files
    docs = load_and_preprocess_pipeline(data_directory, chunk_size=800, chunk_overlap=100)
    print(f"Loaded {len(docs)} chunks.")
    # inspect first few
    for d in docs[:5]:
        print("---- chunk ----")
        print(d.page_content[:200], "…")
        print("metadata:", d.metadata)
