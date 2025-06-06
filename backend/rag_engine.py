import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

DB_DIR = "rag_db"
os.makedirs(DB_DIR, exist_ok=True)

embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def load_and_embed(file_path: str, persona_name: str, user_id: str = None):
    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith(".txt") or file_path.endswith(".md"):
        loader = TextLoader(file_path)
    else:
        raise ValueError("Unsupported file type")

    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_documents(docs)
    
    # Add user_id metadata to each document chunk if provided
    if user_id:
        for chunk in chunks:
            chunk.metadata["user_id"] = user_id

    # Use user-specific directory if user_id is provided
    persist_dir = os.path.join(DB_DIR, f"{user_id}_{persona_name}" if user_id else persona_name)
    vectordb = Chroma(persist_directory=persist_dir, embedding_function=embedding_model)
    vectordb.add_documents(chunks)
    vectordb.persist()

def search_docs(persona_name: str, query: str, top_k=3, user_id: str = None) -> str:
    # Use user-specific directory if user_id is provided
    persist_dir = os.path.join(DB_DIR, f"{user_id}_{persona_name}" if user_id else persona_name)
    
    # Check if the directory exists
    if not os.path.exists(persist_dir):
        return "No relevant documents found."
        
    vectordb = Chroma(persist_directory=persist_dir, embedding_function=embedding_model)
    
    # Add filter for user_id if provided
    filter_dict = {"user_id": user_id} if user_id else None
    
    try:
        docs = vectordb.similarity_search(query, k=top_k, filter=filter_dict)
        return "\n\n".join([doc.page_content for doc in docs])
    except Exception as e:
        print(f"Error searching documents: {str(e)}")
        return "Error retrieving relevant documents."
