import os
import chromadb
from chromadb.config import Settings

CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "./chroma_data")

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=CHROMA_DB_DIR)

    def get_or_create_collection(self, collection_name: str):
        return self.client.get_or_create_collection(name=collection_name)

    def add_documents(self, collection_name: str, texts: list[str], metadatas: list[dict], ids: list[str]):
        collection = self.get_or_create_collection(collection_name)
        collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )

    def query(self, collection_name: str, query_text: str, n_results: int = 5):
        collection = self.get_or_create_collection(collection_name)
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results

vector_store = VectorStore()
