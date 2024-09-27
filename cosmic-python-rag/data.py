import os
from cosmic-python-rag_rag.config import PROCESSED_DIR

from bs4 import BeautifulSoup

def read_all_chapter_html_files():
    """
    Read all chapter files in HTML format from the processed directory.
    """
    chapters = {}
    html_dir = PROCESSED_DIR / 'html'
    
    for filename in sorted(os.listdir(html_dir)):
        if filename.startswith('chapter_') and filename.endswith('.html'):
            chapter_number = filename.split('_')[1].split('.')[0].zfill(2) #zfill(2) to ensure the chapter number is two digits
            html_path = html_dir / filename
            with html_path.open('r') as html_file:
                soup = BeautifulSoup(html_file, 'html.parser')
                chapters[chapter_number] = soup
    
    return chapters