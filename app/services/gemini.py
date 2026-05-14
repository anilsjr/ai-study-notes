import os
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("WARNING: GEMINI_API_KEY not set!")

def get_gemini_model(model_name="gemini-2.5-flash", generation_config=None):
    """
    Returns a configured Gemini model instance.
    """
    return genai.GenerativeModel(
        model_name=model_name,
        generation_config=generation_config
    )

async def generate_content_async(prompt: str, model_name="gemini-2.5-flash"):
    model = get_gemini_model(model_name=model_name)
    response = await model.generate_content_async(prompt)
    return response.text
