from app.agents.notes_agent import NotesGenerationAgent
from app.agents.qa_agent import QAGenerationAgent
from app.agents.rag_agent import RAGQueryAgent
from app.agents.export_agent import PDFExportAgent

class OrchestratorAgent:
    """
    Acts as the central conductor for the Google ADK inspired architecture.
    Handles decision making, tool distribution, and state workflows.
    """
    def __init__(self):
        self.notes_agent = NotesGenerationAgent()
        self.qa_agent = QAGenerationAgent()
        self.rag_agent = RAGQueryAgent()
        self.export_agent = PDFExportAgent()

    async def workflow_generate_study_pack(self, context: str):
        """
        Executes a full study pack pipeline.
        """
        # 1. Generate Notes
        summary = await self.notes_agent.generate_summary(context)
        
        # 2. Generate Flashcards
        flashcards = await self.qa_agent.generate_flashcards(context)
        
        # 3. Generate MCQs
        mcqs = await self.qa_agent.generate_mcqs(context)

        return {
            "summary": summary,
            "flashcards": flashcards,
            "mcqs": mcqs
        }
        
    async def workflow_rag_chat(self, collection_name: str, query: str):
        return await self.rag_agent.answer_query(collection_name, query)

orchestrator = OrchestratorAgent()
