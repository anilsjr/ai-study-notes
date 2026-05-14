from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from app.vectorstore.chroma import vector_store


def retrieve_context(collection_name: str, query: str, top_k: int = 4) -> str:
    """Retrieves relevant document chunks from ChromaDB for a given query.

    Args:
        collection_name: The ChromaDB collection name to search in.
        query: The search query string.
        top_k: Number of top results to retrieve.

    Returns:
        A string containing the concatenated relevant document chunks.
    """
    results = vector_store.query(collection_name, query, n_results=top_k)
    if not results.get("documents"):
        return "No relevant context found in the knowledge base."
    return "\n\n".join([doc for sublist in results["documents"] for doc in sublist])


retrieve_context_tool = FunctionTool(func=retrieve_context)

rag_agent = LlmAgent(
    name="rag_query_agent",
    model="gemini-2.5-flash",
    instruction="""You are a helpful AI Study Assistant.
Use the `retrieve_context` tool to find relevant information from the student's document collection.
Answer questions ONLY based on the retrieved context.
If the context does not contain the answer, say: "I don't have that information in your notes."
Always cite which part of the notes you're drawing from.""",
    description="Answers student questions using RAG over their uploaded notes.",
    tools=[retrieve_context_tool],
)
