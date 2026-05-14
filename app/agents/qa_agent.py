from google.adk.agents import LlmAgent

# MCQ Agent
mcq_agent = LlmAgent(
    name="mcq_generation_agent",
    model="gemini-2.5-flash",
    instruction="""Generate 5 Multiple Choice Questions at Medium difficulty from the provided text.
Return ONLY a valid JSON array:
[{"question": "...", "options": ["A","B","C","D"], "correct_answer": "...", "explanation": "..."}]""",
    description="Generates MCQs from study material.",
    output_key="mcqs",
)

# Flashcard Agent
flashcard_agent = LlmAgent(
    name="flashcard_generation_agent",
    model="gemini-2.5-flash",
    instruction="""Create 10 flashcards from the provided text.
Return ONLY a valid JSON array:
[{"front": "Concept or Question", "back": "Definition or Answer"}]""",
    description="Generates flashcards from study material.",
    output_key="flashcards",
)
