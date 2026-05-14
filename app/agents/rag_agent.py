from app.vectorstore.chroma import vector_store
from app.services.gemini import get_gemini_model

class RAGQueryAgent:
    def __init__(self):
        self.model = get_gemini_model("gemini-2.5-flash")

    def retrieve_context(self, collection_name: str, query: str, top_k: int = 4):
        results = vector_store.query(collection_name, query, n_results=top_k)
        if not results['documents']:
            return ""
        return "\n\n".join([doc for sublist in results['documents'] for doc in sublist])

    async def answer_query(self, collection_name: str, query: str) -> str:
        context = self.retrieve_context(collection_name, query)
        
        prompt = f"""
        You are a helpful AI Study assistant answering questions strictly based on the provided document excerpts.
        If the answer is not in the context, do not make up an answer. State that you don't have that information.
        
        Context:
        {context}

        Question: {query}
        """
        response = await self.model.generate_content_async(prompt)
        return response.text
