import json
from tqdm import tqdm
from cosmic-python-rag_rag.config import PROCESSED_DIR
from cosmic-python-rag_rag.data.embeddings import get_embedding
from cosmic-python-rag_rag.data.generate_summaries import generate_chapter_summary
from cosmic-python-rag_rag.data.keywords_extraction import extract_keywords
from cosmic-python-rag_rag.data.data_cleaning import parse_html_content_with_sections, read_all_chapter_html_files
from dotenv import load_dotenv  

load_dotenv()

# Ensure the processed directory exists
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

def process_and_index_chapters():
    print("Starting indexing...")
    # Step 1: Data Loading
    chapters = read_all_chapter_html_files()
    print(f"Read {len(chapters)} chapters")

    # Step 2: Process Chapters
    processed_data = {}
    for chapter_num, chapter_soup in tqdm(chapters.items(), desc="Processing chapters"):
        chapter_content = parse_html_content_with_sections(chapter_soup)
        
        # Generate summary
        full_chapter_text = ' '.join([section['text_content'] for section in chapter_content['sections']])
        with tqdm(total=1, desc=f"Generating summary for chapter {chapter_num}", leave=False) as pbar:
            chapter_summary = generate_chapter_summary(full_chapter_text)
            pbar.update(1)
        
        # Calculate summary embedding
        with tqdm(total=1, desc=f"Calculating summary embedding for chapter {chapter_num}", leave=False) as pbar:
            summary_embedding = get_embedding(chapter_summary)
            pbar.update(1)
        
        # Extract keywords
        with tqdm(total=1, desc=f"Extracting keywords for chapter {chapter_num}", leave=False) as pbar:
            chapter_keywords = extract_keywords({chapter_num: {'sections': chapter_content['sections']}})
            pbar.update(1)
        
        # Calculate embeddings for each section
        for section in tqdm(chapter_content['sections'], desc=f"Calculating embeddings for chapter {chapter_num}", leave=False):
            section['embedding'] = get_embedding(section['text_content'])
        
        processed_data[chapter_num] = {
            'chapter_title': chapter_content['title'],
            'chapter_summary': chapter_summary,
            'chapter_summary_embedding': summary_embedding,
            'chapter_keywords': chapter_keywords[chapter_num],
            'sections': chapter_content['sections']
        }

    # Step 3: Save Processed Data
    with tqdm(total=1, desc="Saving processed data", leave=False) as pbar:
        with open(PROCESSED_DIR / 'processed_data.json', 'w') as output_file:
            json.dump(processed_data, output_file, indent=4)
        pbar.update(1)
    print("Saved processed data to JSON file")

    print("Indexing completed.")

if __name__ == "__main__":
    process_and_index_chapters()
