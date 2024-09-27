from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from scipy.sparse import csr_matrix
from nltk.corpus import stopwords
import nltk

nltk.download('stopwords', quiet=True)

def ct_idf_keyword_extraction(chapters):
    """
    Extract keywords using c-TF-IDF scores from chapters of a single document.

    Parameters:
    chapters (dict): A dictionary where keys are chapter identifiers and values are dictionaries
                     containing chapter content. Each chapter content dictionary should have a 
                     'sections' key with a list of text sections.

    Returns:
    dict: A dictionary where keys are chapter identifiers and values are lists of top 10 keywords 
          for each chapter based on c-TF-IDF scores.
    """
    chapter_texts = []
    chapter_keys = []

    for chapter_key, chapter_content in chapters.items():
        chapter_keys.append(chapter_key)
        combined_text = ' '.join([section['text_content'] for section in chapter_content['sections']])
        chapter_texts.append(combined_text)

    # Calculate TF-IDF scores with stopwords removed
    stop_words = stopwords.words('english')
    vectorizer = TfidfVectorizer(stop_words=stop_words)
    tfidf_matrix = vectorizer.fit_transform(chapter_texts)
    feature_names = vectorizer.get_feature_names_out()

    # Calculate c-TF-IDF scores
    num_docs = len(chapter_texts)
    tfidf_matrix_sum = tfidf_matrix.sum(axis=0)
    c_tfidf_matrix = tfidf_matrix.multiply(num_docs).multiply(1 / tfidf_matrix_sum)

    # Convert to CSR matrix for efficient row slicing
    c_tfidf_matrix = csr_matrix(c_tfidf_matrix)

    keywords = {}
    for i, chapter_key in enumerate(chapter_keys):
        c_tfidf_scores = c_tfidf_matrix[i].toarray().flatten()
        sorted_indices = np.argsort(c_tfidf_scores)[::-1]
        top_keywords = [feature_names[idx] for idx in sorted_indices[:10]]
        keywords[chapter_key] = top_keywords

    return keywords

def keywords_from_description(chapters):
    """
    Extract keywords from the description of images and code blocks.

    Parameters:
    chapters (dict): A dictionary where keys are chapter identifiers and values are dictionaries
                     containing chapter content. Each chapter content dictionary should have a 
                     'sections' key with a list of dictionaries containing 'images' and 'code_blocks'.

    Returns:
    dict: A dictionary where keys are chapter identifiers and values are lists of keywords 
          extracted from image descriptions and code block titles.
    """
    import re
    
    def extract_words(text):
        return [word.lower() for word in re.findall(r'\b(?:figure \d+|\w+(?:\.py)?)\b', text, re.IGNORECASE)]
    
    keywords = {
        chapter_key: [
            word
            for section in chapter_content['sections']
            for source in ('images', 'code_blocks')
            for item in section.get(source, [])
            for word in extract_words(item.get('description') or item.get('title', ''))
        ]
        for chapter_key, chapter_content in chapters.items()
    }
    
    return keywords

def extract_keywords(chapters):
    """
    Create a pipeline for keywords extraction.

    Parameters:
    chapters (dict): A dictionary where keys are chapter identifiers and values are dictionaries
                     containing chapter content.

    Returns:
    dict: A dictionary where keys are chapter identifiers and values are lists of top 10 keywords 
          for each chapter, combining results from c-TF-IDF and description-based extraction.
    """
    stop_words = set(stopwords.words('english'))

    ct_idf_keywords = ct_idf_keyword_extraction(chapters)
    description_keywords = keywords_from_description(chapters)

    combined_keywords = {}
    for chapter_key in chapters.keys():
        all_keywords = ct_idf_keywords.get(chapter_key, []) + description_keywords.get(chapter_key, [])
        filtered_keywords = [word for word in all_keywords if word.lower() not in stop_words]
        combined_keywords[chapter_key] = list(set(filtered_keywords))

    return combined_keywords
