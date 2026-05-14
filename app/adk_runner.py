from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
from app.agents.orchestrator import study_pack_agent, rag_orchestrator

APP_NAME = "ai_study_notes"

session_service = InMemorySessionService()

study_pack_runner = Runner(
    agent=study_pack_agent,
    app_name=APP_NAME,
    session_service=session_service,
    auto_create_session=True,
)

rag_runner = Runner(
    agent=rag_orchestrator,
    app_name=APP_NAME,
    session_service=session_service,
    auto_create_session=True,
)


async def run_study_pack(context: str, session_id: str) -> dict:
    """Runs the study pack pipeline via ADK Runner and returns structured output."""
    content = Content(parts=[Part(text=context)])
    result = {"summary": "", "mcqs": [], "flashcards": []}
    
    # Run the study pack pipeline
    async for event in study_pack_runner.run_async(
        user_id="system",
        session_id=session_id,
        new_message=content,
    ):
        if event.is_final_response():
            # Get the session to extract the merged state from parallel sub-agents
            session = await session_service.get_session(
                app_name=APP_NAME, user_id="system", session_id=session_id
            )
            state = session.state
            # Parallel sub-agents with output_key write directly into session state.
            # Keep fallbacks for older/alternate state structures.
            result["summary"] = (
                state.get("summary")
                or state.get("notes_generation_agent", {}).get("response", "")
                or result["summary"]
            )
            result["mcqs"] = (
                state.get("mcqs")
                or state.get("mcq_generation_agent", {}).get("mcqs", [])
                or result["mcqs"]
            )
            result["flashcards"] = (
                state.get("flashcards")
                or state.get("flashcard_generation_agent", {}).get("flashcards", [])
                or result["flashcards"]
            )
    return result


async def run_rag_chat(collection_name: str, query: str, session_id: str) -> str:
    """Runs a RAG query via ADK Runner and returns the answer string."""
    # Pass collection_name as context in the message so the tool can use it
    message_text = f"[collection:{collection_name}]\n\n{query}"
    content = Content(parts=[Part(text=message_text)])
    answer = ""
    async for event in rag_runner.run_async(
        user_id="system",
        session_id=session_id,
        new_message=content,
    ):
        if event.is_final_response() and event.content:
            answer = event.content.parts[0].text
    return answer
