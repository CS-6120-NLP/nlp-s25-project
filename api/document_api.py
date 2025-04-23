import os
from typing import List, Literal

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredPDFLoader, TextLoader, UnstructuredWordDocumentLoader
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

from models.entities import Document as DBDocument
from utils.db_utils import get_db_session

router = APIRouter()


@router.post("", response_model=dict)
async def upload_document(
        personas: List[Literal["student", "staff"]] = Form(...),
        file: UploadFile = File(...)
):
    if not personas:
        raise HTTPException(status_code=400, detail="At least one persona tag is required.")
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in {".pdf", ".txt", ".docx"}:
        raise HTTPException(status_code=415, detail="Unsupported file type.")

    # Save file
    save_dir = "docs"
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, file.filename)
    with open(save_path, "wb") as out:
        out.write(await file.read())

    # Load & split
    if ext == ".pdf":
        loader = UnstructuredPDFLoader(save_path)
    elif ext == ".docx":
        loader = UnstructuredWordDocumentLoader(save_path)
    else:
        loader = TextLoader(save_path, encoding="utf-8")
    raw_docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(raw_docs)

    # Embed incrementally
    embeddings = OpenAIEmbeddings()
    persist_dir = "chroma_db"
    if os.path.isdir(persist_dir) and os.listdir(persist_dir):
        store = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
        store.add_documents(chunks, metadatas=[{"persona_tags": personas} for _ in chunks])
    else:
        store = Chroma.from_documents(
            chunks, embeddings, persist_directory=persist_dir,
            metadatas=[{"persona_tags": personas} for _ in chunks]
        )
    store.persist()

    # Persist metadata to SQL
    # after `store.persist()`
    db = get_db_session()
    for chunk in chunks:
        db.add(
            DBDocument(
                source=chunk.metadata.get("source"),
                filename=file.filename,
                extension=ext,
                persona_tags=personas
            )
        )
    db.commit()

    return {"status": "uploaded", "personas": personas, "filename": file.filename}
