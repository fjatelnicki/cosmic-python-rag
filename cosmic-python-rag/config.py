from pathlib import Path
import sys
import time

# Data Config
DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

# RAG Config
TOP_N_SECTIONS = 5
TOP_N_CHAPTERS = 3
SCORE_BOOST_FOR_MATCH = 0.1

# OpenAI Config
OPENAI_MODEL_EMB = "text-embedding-3-small"
OPENAI_MODEL_GPT = "gpt-3.5-turbo"
TEMPERATURE = 0.7
SUMMARY_PROMPT = """
You are a helpful assistant that summarizes text about Clean Architecture in Python.

Summarize the following chapter in two sentences:

{chapter_text}
"""

RAG_PROMPT = """
You are a helpful assistant that answers questions about Clean Architecture in Python.

Use the following sections to answer the question:

{sections}

Answer the question in plain text. Cite code snippets if relevant and needed.
"""

# Chatbot Config
GOODBYE_PHRASE = "Thank you for using the chatbot. Goodbye!"
WELCOME_PHRASE = "Welcome to the Clean Architecture in Python chatbot! (Type 'exit' to quit the chatbot)"
ENTER_QUESTION_PHRASE = "\nEnter your question:\n"


def loading_animation(loading):
    animation = ['.', '..', '...']
    i = 0
    while loading[0]:
        sys.stdout.write('\rGenerating answer' + animation[i % len(animation)])
        sys.stdout.flush()
        time.sleep(0.5)
        i += 1