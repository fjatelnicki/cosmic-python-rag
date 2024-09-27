import os
import openai
from dotenv import load_dotenv
from cosmic-python-rag_rag.config import OPENAI_MODEL_GPT, RAG_PROMPT, TEMPERATURE

load_dotenv()

def generate_answer(query, top_sections):
    """
    Generate an answer based on the query and top sections using OpenAI's GPT model.

    Parameters:
    query (str): The input query.
    top_sections (list): A list of top sections that match the query.

    Returns:
    str: The generated answer from the GPT model.
    """
    sections_context = "\n\n".join([
        f"Section: {section['section_title']}\n{section['text_content']}"
        for section in top_sections
    ])

    full_prompt = RAG_PROMPT.format(
        sections=sections_context,
    )

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    client = openai.OpenAI(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL_GPT,
            messages=[
                {"role": "system", "content": full_prompt},
                {"role": "user", "content": query}
            ],
            max_tokens=500,
            temperature=TEMPERATURE,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating answer: {str(e)}")
        return "I'm sorry, but I encountered an error while trying to generate an answer. Please try again later."
