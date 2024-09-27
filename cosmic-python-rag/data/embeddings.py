import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
from cosmic-python-rag_rag.config import OPENAI_MODEL_EMB
from sklearn.metrics.pairwise import cosine_similarity
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_embedding(text: str) -> list:
    """
    Generate an embedding for the given text using OpenAI's API.

    Args:
        text (str): The input text to generate an embedding for.

    Returns:
        list: The embedding vector for the input text.
    """
    try:
        response = client.embeddings.create(
            input=[text],
            model=OPENAI_MODEL_EMB
        )
        embedding = response.data[0].embedding
        return embedding
    except Exception as e:
        raise e

def calculate_similarity(embedding1, embedding2):
    # Reshape embeddings to 2D arrays
    embedding1 = np.array(embedding1).reshape(1, -1)
    embedding2 = np.array(embedding2).reshape(1, -1)
    
    # Calculate cosine similarity
    similarity = cosine_similarity(embedding1, embedding2)[0][0]
    return similarity

if __name__ == "__main__":
    sample_text = "Your text here"
    print(get_embedding(sample_text))
