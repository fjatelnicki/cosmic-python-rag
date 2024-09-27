# Clean Architecture in Python Chatbot

This repository contains a Python-based Retrieval-Augmented Generation (RAG).The system can retrieve relevant information from a book on Clean Architecture in Python and generate answers to user queries by referencing specific sections of the source material. It combines advanced natural language processing techniques with efficient information retrieval to provide accurate and context-aware responses about Clean Architecture concepts and related topics.

## Setup
This project uses Poetry for dependency management. Follow these steps to set up the project:
w
1.	Install Poetry (if you haven't already):
```sh
curl -sSL https://install.python-poetry.org | python3 -
```
2.	Clone the repository in `data/raw/` directory
```
mkdir -p data/raw
cd data/raw
git clone https://github.com/your-username/clean-architecture-python-chatbot.git raw
```

3.	Install dependencies:

```sh
poetry install
```
4.	Activate the virtual environment:
```sh
poetry shell
```
5.	Set up environment variables:
Create a `.env` file in the project root and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Module Documentation

### Retrieval - `retrieval.py`

This module handles the retrieval of relevant chapters and sections based on the user's query.

- **`get_initial_retrieval(query, processed_data)`**: 
  - Calculates similarity scores between the query and chapter summaries using embeddings.
  - Adjusts scores based on keyword matches in the query.
  - Returns the top `TOP_N_CHAPTERS` (defined in config) with highest scores, query embedding, and matched keywords.
  - Implementation details:
    - Uses `get_embedding()` to create query embedding.
    - Calculates similarity between query and chapter summary embeddings.
    - Boosts scores by `SCORE_BOOST_FOR_MATCH` (from config) for each keyword match.
    - Filters matched keywords to include only retrieved chapters.

- **`get_final_retrieval(query_embedding, retrieved_chapters, processed_data)`**: 
  - Finds the most relevant sections within the retrieved chapters.
  - Calculates similarity scores between the query embedding and section embeddings.
  - Returns the top `TOP_N_SECTIONS` (defined in config) with highest similarity scores.
  - Implementation details:
    - Iterates through sections in retrieved chapters.
    - Calculates similarity between query embedding and section embeddings.
    - Sorts sections by similarity score and returns top N.

- **`get_rag_response(query, processed_data)`**: 
  - Combines the initial and final retrieval steps for a comprehensive response.
  - Returns the top sections and matched keywords.
  - Implementation details:
    - Calls `get_initial_retrieval()` to get top chapters and query embedding.
    - Calls `get_final_retrieval()` with results from initial retrieval.
    - Returns combined results for use in generating the final response.

This module utilizes embeddings and similarity calculations to provide context-aware retrieval of relevant information from the processed data.

### `generate_summaries.py`

This module generates summaries for chapters using the OpenAI GPT model.

- **`generate_chapter_summary(chapter_text: str) -> str`**: 
  - Generates a summary for a given chapter using OpenAI's API.
  - Parameters:
    - `chapter_text (str)`: The text content of the chapter to be summarized.
  - Returns:
    - `str`: The generated summary of the chapter.
  - Implementation details:
    - Retrieves the OpenAI API key from environment variables.
    - Creates an OpenAI client and sends a chat completion request with the following parameters:
      - Model: Specified by OPENAI_MODEL_GPT in the config
      - Messages: System message with the SUMMARY_PROMPT and user message with the chapter text
      - Max tokens: 150
      - Temperature: Specified by TEMPERATURE in the config
    - Returns the generated summary from the model's response.
    - Handles potential errors and raises exceptions if summary generation fails.

This module provides a way to generate concise summaries of chapter content, which can be useful for creating chapter overviews or for use in other parts of the RAG (Retrieval-Augmented Generation) pipeline. The summaries are generated using the same OpenAI GPT model as the main answer generation, ensuring consistency in the AI's understanding and output style across the application.


### Keyword extraction - `keywords_extraction.py`

This module extracts keywords from chapters using different methods, combining c-TF-IDF scores and description-based extraction.

- **`ct_idf_keyword_extraction(chapters)`**: 
  - Extracts keywords using c-TF-IDF (class-based Term Frequency-Inverse Document Frequency) scores from chapters.
  - Returns a dictionary of top 10 keywords for each chapter.
  - Implementation details:
    - Combines all section texts for each chapter.
    - Uses sklearn's TfidfVectorizer with English stopwords removed.
    - Calculates c-TF-IDF scores by multiplying TF-IDF scores with document frequency.
    - Selects top 10 keywords based on c-TF-IDF scores for each chapter.

- **`keywords_from_description(chapters)`**: 
  - Extracts keywords from the descriptions of images and titles of code blocks in each chapter.
  - Returns a dictionary of keywords extracted from image descriptions and code block titles.
  - Implementation details:
    - Uses regex to find words, "figure X" mentions, and potential file names (e.g., "word.py").
    - Extracts words from 'description' field of images and 'title' field of code blocks.
    - Converts all extracted words to lowercase.

- **`extract_keywords(chapters)`**: 
  - Combines c-TF-IDF and description-based extraction methods for comprehensive keyword extraction.
  - Returns a dictionary of unique keywords for each chapter, with stopwords removed.
  - Implementation details:
    - Calls both `ct_idf_keyword_extraction()` and `keywords_from_description()`.
    - Combines results from both methods for each chapter.
    - Removes stopwords and duplicates from the combined keyword list.

This module provides a robust approach to keyword extraction, leveraging both statistical (c-TF-IDF) and rule-based (description extraction) methods to capture important terms from the chapters.

### Generation - `generation.py`

This module generates answers using the OpenAI GPT model based on the user's query and retrieved relevant sections.

- **`generate_answer(query, top_sections)`**: 
  - Generates an answer based on the query and top sections.
  - Returns the generated answer as a string.
  - Implementation details:
    - Constructs a context string from the top sections, including section titles and content.
    - Uses a predefined RAG_PROMPT (Retrieval-Augmented Generation prompt) from the config.
    - Retrieves the OpenAI API key from environment variables.
    - Creates an OpenAI client and sends a chat completion request with the following parameters:
      - Model: Specified by OPENAI_MODEL_GPT in the config
      - Messages: System message with the RAG prompt and user message with the query
      - Max tokens: 500
      - Temperature: Specified by TEMPERATURE in the config
    - Returns the generated content from the model's response.
    - Handles potential errors and returns an error message if generation fails.

This module leverages the OpenAI GPT model to generate context-aware answers based on the retrieved relevant sections, providing a seamless integration of retrieval and generation in the RAG (Retrieval-Augmented Generation) pipeline.


# Example Usage

## Asciidoc to HTML Conversion

To convert the Asciidoc book to HTML, you'll need to install some dependencies and run specific commands. Here's how to set it up:

### Dependencies

Make sure you have the following dependencies installed and commands run

- asciidoctor
- Pygments (for syntax highlighting)
- asciidoctor-diagram (to render images from the text sources in ./images)

You can install these dependencies using the following commands:

```sh
gem install asciidoctor
python3 -m pip install --user pygments
gem install pygments.rb
gem install asciidoctor-diagram
```

```sh
make html  # builds local .html versions of each chapter
make test  # does a sanity-check of the code listings
```


## Indexing the Book

Before running the chatbot, it's essential to index the book file. This process prepares the data for efficient retrieval and analysis. To index the book, follow these steps:

1. Ensure you have the raw book file in the `data/raw` directory.

2. Run the indexing process using the following command:

   ```sh
   python cosmic-python-rag_rag/main.py indexing
   ```

3. This command will:
   - Process the raw book file
   - Extract chapters and sections
   - Generate embeddings for each section
   - Create summaries for each chapter
   - Extract keywords from the content
   - Store the processed data in the `data/processed` directory

4. Wait for the indexing process to complete. This may take a few minutes depending on the size of the book and your system's performance.

5. Once indexing is finished, you'll see a confirmation message indicating that the data has been successfully processed and stored.

After completing these steps, your book will be indexed and ready for use with the chatbot. You can now proceed to run the chatbot as shown in the Example Usage section below.


## Chatbot
### Example 1: Basic Q&A

This example demonstrates the usage of the Clean Architecture in Python chatbot. Let's break down each part:

1. Welcome Message:
   The chatbot starts with a welcome message and instructions on how to exit.

2. User Input:
   The user is prompted to enter a question. In this case, the question is "What is the domain model?"

3. Answer:
   The chatbot provides a comprehensive answer about the domain model, explaining its role in software development and business processes.

4. Relevant Sections:
   The chatbot lists the top 5 most relevant sections from the source material, including:
   - Chapter and section titles
   - Similarity scores (indicating how closely the section matches the query)

5. Matched Keywords:
   The chatbot shows which chapters contained keywords matching the user's query. In this case, the word "domain" was found as a keyword in Chapters 1, 2, and 12.

This example showcases the chatbot's ability to:
- Understand and respond to user queries
- Provide detailed, context-aware answers
- Reference specific sections of the source material
- Highlight keyword matches across different chapters

The chatbot combines natural language processing, information retrieval, and domain-specific knowledge to offer a comprehensive and informative interaction about Clean Architecture in Python.


```sh
python cosmic-python-rag_rag/main.py chatbot
```

```
Welcome to the Clean Architecture in Python chatbot! (Type 'exit' to quit the chatbot)

Enter your question:
What is the domain model?

Answer:
A domain model is a representation of the core business domain in software development. It captures the essential rules, constraints, and behaviors of the problem being solved. The domain model is a mental map that business owners have of their businesses, reflecting how complex processes are distilled into a single word or phrase. In the context of software architecture, the domain model focuses on building a useful model of a problem, which, when done correctly, adds value and enables new possibilities. The domain model is essential for designing software that aligns with the business domain and supports its processes effectively.


Relevant sections found:
1. Chapter 01: Domain Modeling
   Section: What Is a Domain Model?
   Similarity Score: 0.6323
2. Chapter 12: Command-Query Responsibility Segregation (CQRS)
   Section: Domain Models Are for Writing
   Similarity Score: 0.6044
3. Chapter 02: Repository Pattern
   Section: Persisting Our Domain Model
   Similarity Score: 0.5486
4. Chapter 12: Command-Query Responsibility Segregation (CQRS)
   Section: Your Domain Model Is Not Optimized for Read Operations
   Similarity Score: 0.5302
5. Chapter 01: Domain Modeling
   Section: Exploring the Domain Language
   Similarity Score: 0.4812

Matched keywords:
Chapter 01 - Domain Modeling: domain
Chapter 02 - Repository Pattern: domain
Chapter 12 - Command-Query Responsibility Segregation (CQRS): domain
```

### Example 2: Code-snippets Q&A
This example demonstrates the chatbot's ability to provide code snippets in response to user queries. The chatbot can understand the user's request for specific code examples and retrieve relevant code snippets from the source material. This feature is particularly useful for developers looking for practical examples and implementations.

In this example, the user asks for the "First cut of a domain model for batches (model.py)" and the chatbot responds with a detailed code snippet that defines the domain model for batches in Python. The provided code includes data classes, methods for allocation and deallocation, and properties for managing order lines and quantities.

This example showcases the chatbot's capability to:
- Interpret and respond to code-related queries
- Retrieve and present relevant code snippets
- Provide context and explanations for the code

The chatbot leverages natural language processing and information retrieval techniques to deliver accurate and useful code examples to the user.

```
Enter your question:
What is code First cut of a domain model for batches (model.py)

Answer:
Here is the first cut of a domain model for batches in Python:

```python
from dataclasses import dataclass
from typing import Optional
from datetime import date

@dataclass
class OrderLine:
    orderid: str
    sku: str
    qty: int

@dataclass
class Batch:
    reference: str
    sku: str
    qty: int
    eta: Optional[date] = None

    def allocate(self, line: OrderLine):
        if self.can_allocate(line):
            self.qty -= line.qty

    def deallocate(self, line: OrderLine):
        if line in self._allocations:
            self.qty += line.qty
            self._allocations.remove(line)

    def can_allocate(self, line: OrderLine) -> bool:
        return self.sku == line.sku and self.available_quantity >= line.qty

    @property
    def available_quantity(self) -> int:
        return self.qty - sum(line.qty for line in self._allocations)

    def __gt__(self, other: 'Batch') -> bool:
        return self.qty > other.qty

    def __eq__(self, other) -> bool:
        if not isinstance(other, Batch):
            return False
        return self.reference == other.reference

    def __hash__(self) -> int:
        return hash(self.reference)

    def __init__(self, reference: str, sku: str, qty: int):
        self.reference = reference
        self.sku = sku
        self.qty = qty
        self._allocations = set()
```

This code defines two data classes, `OrderLine` and `Batch`, representing an order line and a batch respectively. The `Batch` class includes methods for allocating and deallocating order lines, checking if an order line can be allocated to the batch, calculating the available quantity, and comparing batches based on quantity. The `__eq__` and `__hash__` methods are implemented for equality and hashing based on the `reference` attribute.

This is a simple domain model for batches that allows for allocation and deallocation of order lines.


Relevant sections found:
1. Chapter 01: Domain Modeling
   Section: Not Everything Has to Be an Object: A Domain Service Function
   Similarity Score: 1.3517
2. Chapter 01: Domain Modeling
   Section: Unit Testing Domain Models
   Similarity Score: 1.3331
3. Chapter 01: Domain Modeling
   Section: Exploring the Domain Language
   Similarity Score: 1.3217
4. Chapter 01: Domain Modeling
   Section: What Is a Domain Model?
   Similarity Score: 1.2820
5. Chapter 07: Aggregates and Consistency Boundaries
   Section: What About Performance?
   Similarity Score: 1.0561
```

