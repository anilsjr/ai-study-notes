from app.services.gemini import get_gemini_model

class NotesGenerationAgent:
    def __init__(self):
        self.model = get_gemini_model(model_name="gemini-2.5-flash")

    async def generate_summary(self, context: str) -> str:
        prompt = f"""
        Provide a comprehensive and highly structured summary of the following study material. 
        Format with clear headings, bullet points, and highlight key formulas or concepts in bold.
        
        Material:
        {context}
        """
        response = await self.model.generate_content_async(prompt)
        return response.text

    async def extract_key_points(self, context: str) -> str:
        prompt = f"""
        Extract the absolute most critical key points and formulas from this study material.
        Make it easy to revise.

        Material:
        {context}
        """
        response = await self.model.generate_content_async(prompt)
        return response.text
