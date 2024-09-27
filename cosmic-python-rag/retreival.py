from cosmic-python-rag_rag.config import TOP_N_CHAPTERS, TOP_N_SECTIONS, SCORE_BOOST_FOR_MATCH
from cosmic-python-rag_rag.data.embeddings import get_embedding, calculate_similarity
import string

def get_initial_retrieval(query, processed_data):
    """
    Retrieve the initial set of chapters based on the query.

    Parameters:
    query (str): The input query.
    processed_data (dict): The processed data containing chapter information.

    Returns:
    tuple: A tuple containing the retrieved chapters, query embedding, and filtered matched keywords.
    """
    # Get query embedding
    query_embedding = get_embedding(query)

    # Load processed data

    # The loops could be combined into one loop, but I'm keeping them separate for now for clarity
    # Calculate similarity scores for each chapter based on summary embeddings
    chapter_scores = {}
    for chapter_num, chapter_data in processed_data.items():
        summary_embedding = chapter_data['chapter_summary_embedding']
        similarity_score = calculate_similarity(query_embedding, summary_embedding)
        chapter_scores[chapter_num] = similarity_score

    # Adjust scores based on keyword matches


    matched_keywords = {}
    query_words = set(query.lower().translate(str.maketrans('', '', string.punctuation)).split())
    for chapter_num, chapter_data in processed_data.items():
        matched_keywords[chapter_num] = []
        for keyword in chapter_data['chapter_keywords']:
            cleaned_keyword = keyword.lower().translate(str.maketrans('', '', string.punctuation))
            if cleaned_keyword in query_words:
                chapter_scores[chapter_num] += SCORE_BOOST_FOR_MATCH
                matched_keywords[chapter_num].append(keyword)

    # Sort chapters after adjusting scores
    retrieved_chapters = sorted(chapter_scores.items(), key=lambda x: x[1], reverse=True)[:TOP_N_CHAPTERS]

    # Filter matched_keywords to include only the retrieved chapters
    filtered_matched_keywords = {
        chapter_num: keywords
        for chapter_num, keywords in matched_keywords.items()
        if chapter_num in dict(retrieved_chapters)
    }

    # Return filtered_matched_keywords instead of matched_keywords
    return retrieved_chapters, query_embedding, filtered_matched_keywords, chapter_scores

    
def get_final_retrieval(query_embedding, retrieved_chapters, processed_data, initial_chapter_scores):
    """
    Retrieve the final set of sections based on the query embedding and retrieved chapters.

    Parameters:
    query_embedding (list): The embedding of the query.
    retrieved_chapters (list): The list of retrieved chapters.
    processed_data (dict): The processed data containing chapter information.
    initial_chapter_scores (dict): The initial scores of the retrieved chapters.

    Returns:
    list: A list of top sections that match the query.
    """
    # Find top 5 sections that match the query
    matching_sections = []
    for chapter_num, _ in retrieved_chapters:
        chapter_data = processed_data[chapter_num]
        for section in chapter_data['sections']:
            section_embedding = section['embedding']  # Assuming the key is 'embedding' based on the indexing.py file
            similarity_score = calculate_similarity(query_embedding, section_embedding)

            # Add initial chapter score to the section similarity score
            total_similarity_score = similarity_score + initial_chapter_scores[chapter_num]

            matching_sections.append({
                'chapter_num': chapter_num,
                'chapter_title': chapter_data['chapter_title'],
                'section_title': section['section_title'],
                'text_content': section['text_content'],
                'similarity_score': total_similarity_score,
                'code_snippets': section['code_blocks']
            })
    
    # Sort sections by similarity score and get top n
    top_sections = sorted(matching_sections, key=lambda x: x['similarity_score'], reverse=True)[:TOP_N_SECTIONS]
    
    return top_sections
    
def get_rag_response(query, processed_data):
    """
    Get the RAG (Retrieval-Augmented Generation) response based on the query and processed data.

    Parameters:
    query (str): The input query.
    processed_data (dict): The processed data containing chapter information.

    Returns:
    tuple: A tuple containing the top sections and matched keywords.
    """
    retrieved_chapters, query_embedding, matched_keywords, initial_chapter_scores = get_initial_retrieval(query, processed_data)
    
    top_sections = get_final_retrieval(query_embedding, retrieved_chapters, processed_data, initial_chapter_scores)
    
    return top_sections, matched_keywords
