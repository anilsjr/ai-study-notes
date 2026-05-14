from google.adk.agents import ParallelAgent
from app.agents.notes_agent import notes_agent
from app.agents.qa_agent import mcq_agent, flashcard_agent
from app.agents.rag_agent import rag_agent

# For study pack generation: run notes, MCQs, and flashcards in PARALLEL
study_pack_agent = ParallelAgent(
    name="study_pack_orchestrator",
    sub_agents=[notes_agent, mcq_agent, flashcard_agent],
    description="Generates a complete study pack (summary + MCQs + flashcards) in parallel.",
)

# RAG agent is standalone — expose it directly
rag_orchestrator = rag_agent
