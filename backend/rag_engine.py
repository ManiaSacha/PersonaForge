import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

DB_DIR = "rag_db"
os.makedirs(DB_DIR, exist_ok=True)

embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def load_and_embed(file_path: str, persona_name: str):
    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith(".txt") or file_path.endswith(".md"):
        loader = TextLoader(file_path)
    else:
        raise ValueError("Unsupported file type")

    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_documents(docs)

    vectordb = Chroma(persist_directory=os.path.join(DB_DIR, persona_name), embedding_function=embedding_model)
    vectordb.add_documents(chunks)
    vectordb.persist()

def search_docs(persona_name: str, query: str, top_k=3) -> str:
    vectordb = Chroma(persist_directory=os.path.join(DB_DIR, persona_name), embedding_function=embedding_model)
    docs = vectordb.similarity_search(query, k=top_k)
    return "\n\n".join([doc.page_content for doc in docs])
