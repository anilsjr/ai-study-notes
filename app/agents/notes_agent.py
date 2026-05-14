from google.adk.agents import LlmAgent

notes_agent = LlmAgent(
    name="notes_generation_agent",
    model="gemini-2.5-flash",
    instruction="""You are an expert academic summarizer.
When given study material text, produce a comprehensive, structured summary.
Use clear markdown headings (##), bullet points, and bold key terms/formulas.
Return ONLY the formatted markdown summary.""",
    description="Generates structured summaries and key points from study material.",
    output_key="summary",
)
