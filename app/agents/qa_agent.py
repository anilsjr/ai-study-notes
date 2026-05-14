from app.services.gemini import get_gemini_model
import json

class QAGenerationAgent:
    def __init__(self):
        # We enforce JSON output to structure QAs cleanly
        self.model = get_gemini_model(
            model_name="gemini-2.5-flash",
            generation_config={"response_mime_type": "application/json"}
        )

    async def generate_mcqs(self, context: str, count: int = 5, difficulty="Medium"):
        prompt = f"""
        Based on the following text context, generate {count} Multiple Choice Questions (MCQs) 
        with a {difficulty} difficulty level.
        Return ONLY a JSON array of objects with the keys:
        [
            {{
                "question": "The question text",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "The correct option",
                "explanation": "Why this is correct"
            }}
        ]
        
        Context:
        {context}
        """
        response = await self.model.generate_content_async(prompt)
        return json.loads(response.text)

    async def generate_flashcards(self, context: str, count: int = 10):
        prompt = f"""
        Create {count} flashcards based on the following text.
        Return ONLY a JSON array of objects with the keys:
        [
            {{
                "front": "Concept or Question",
                "back": "Definition or Answer"
            }}
        ]

        Context:
        {context}
        """
        response = await self.model.generate_content_async(prompt)
        return json.loads(response.text)
