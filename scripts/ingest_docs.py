import os
from langchain_community.document_loaders import UnstructuredPDFLoader, TextLoader, UnstructuredWordDocumentLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from api.db_utils import get_db_session
from api.db_models import Document as DocumentModel

def ingest(input_dir="docs", persist_dir="chroma_db"):
    docs = []
    for root, _, files in os.walk(input_dir):
        for fname in files:
            path = os.path.join(root, fname)
            if fname.lower().endswith(".pdf"):
                loader = UnstructuredPDFLoader(path)
            elif fname.lower().endswith(".docx"):
                loader = UnstructuredWordDocumentLoader(path)
            elif fname.lower().endswith(".txt"):
                loader = TextLoader(path, encoding="utf-8")
            else:
                continue
            docs.extend(loader.load())
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)
    embeddings = OpenAIEmbeddings()
    if os.path.isdir(persist_dir) and os.listdir(persist_dir):
        store = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
        store.add_documents(chunks)
    else:
        store = Chroma.from_documents(chunks, embeddings, persist_directory=persist_dir)
    store.persist()
    db = get_db_session()
    for chunk in chunks:
        db.add(DocumentModel(source=chunk.metadata.get("source"), persona_tags=[]))
    db.commit()

if __name__ == "__main__":
    ingest()
