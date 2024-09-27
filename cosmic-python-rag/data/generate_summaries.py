import openai
from dotenv import load_dotenv
from cosmic-python-rag_rag.config import OPENAI_MODEL_GPT, SUMMARY_PROMPT, TEMPERATURE
import os

load_dotenv()

def generate_chapter_summary(chapter_text: str) -> str:
    """
    Generate a summary for a given chapter using OpenAI's API.

    Parameters:
    chapter_text (str): The text content of the chapter to be summarized.

    Returns:
    str: The generated summary of the chapter.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    client = openai.OpenAI(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL_GPT,
            messages=[
                {"role": "system", "content": SUMMARY_PROMPT},
                {"role": "user", "content": chapter_text}
            ],
            max_tokens=150,
            temperature=TEMPERATURE,
        )

        summary = response.choices[0].message.content.strip()
        return summary
    except Exception as e:
        raise e

# Example usage
if __name__ == "__main__":
    chapter_text = "Your chapter text here"
    print(generate_chapter_summary(chapter_text))
