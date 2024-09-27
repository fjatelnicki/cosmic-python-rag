import json
import os
import re
from ..config import PROCESSED_DIR, RAW_DIR
from bs4 import BeautifulSoup

def clean_whitespace(text):
    """
    Remove repeated whitespaces from the text.
    
    Parameters:
    text (str): The input text.
    
    Returns:
    str: The cleaned text with repeated whitespaces removed.
    """
    return re.sub(r'\s+', ' ', text).strip()

def remove_non_ascii(text):
    """
    Remove non-ASCII characters from the text.
    
    Parameters:
    text (str): The input text.
    
    Returns:
    str: The cleaned text with non-ASCII characters removed.
    """
    return re.sub(r'[^\x00-\x7F]+', '', text)

def read_all_chapter_html_files():
    """
    Read all chapter files in HTML format from the RAW_DIR directory.

    Returns:
    dict: A dictionary where keys are chapter numbers (as strings) and values are BeautifulSoup objects of the chapter HTML content.
    """
    chapters = {}
    
    for filename in sorted(os.listdir(RAW_DIR)):
        if filename.startswith('chapter_') and filename.endswith('.html'):
            chapter_number = filename.split('_')[1].split('.')[0].zfill(2)
            with open(RAW_DIR / filename, 'r') as html_file:
                chapters[chapter_number] = BeautifulSoup(html_file, 'html.parser')
    
    return chapters

def remove_styling(html_content):
    """
    Remove styling text from HTML code.
    
    Parameters:
    html_content (str): The HTML content as a string.
    
    Returns:
    str: The HTML content with styling text removed.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove <style> tags and style attributes
    for tag in soup.find_all(['style', True]):
        if tag.name == 'style':
            tag.decompose()
        elif 'style' in tag.attrs:
            del tag.attrs['style']
    
    return str(soup)

def extract_title(soup):
    """
    Extract the title from the HTML content.

    Parameters:
    soup (BeautifulSoup): The BeautifulSoup object of the HTML content.

    Returns:
    str: The title of the HTML content, or 'Untitled Chapter' if no title is found.
    """
    title_tag = soup.find('title')
    return clean_whitespace(remove_non_ascii(title_tag.get_text(strip=True))) if title_tag else 'Untitled Chapter'

def extract_text_content(soup):
    """
    Extract the text content from the HTML content.

    Parameters:
    soup (BeautifulSoup): The BeautifulSoup object of the HTML content.

    Returns:
    str: The text content of the HTML content, with paragraphs joined by spaces.
    """
    paragraphs = [p.get_text() for p in soup.find_all('p')]
    text_content = ' '.join(paragraphs).replace('\n', ' ').strip()
    # Remove repeated whitespaces
    return clean_whitespace(remove_non_ascii(text_content))

def extract_code_blocks(soup):
    """
    Extract code blocks and their titles from the HTML content.

    Parameters:
    soup (BeautifulSoup): The BeautifulSoup object of the HTML content.

    Returns:
    list: A list of dictionaries containing 'title' and 'code' for each code block.
    """
    code_blocks = []
    for pre in soup.find_all('pre', class_='highlight'):
        code = pre.find('code')
        if code:
            title = pre.find_previous('div', class_='title')
            title_text = clean_whitespace(remove_non_ascii(title.get_text(strip=True))) if title else 'Untitled Code Block'
            code_blocks.append({
                'title': title_text,
                'code': f"{title_text}\n{code.get_text()}"
            })
    return code_blocks


def extract_images(soup):
    """
    Extract images from the HTML content.

    Parameters:
    soup (BeautifulSoup): The BeautifulSoup object of the HTML content.

    Returns:
    list: A list of dictionaries containing image 'src' and 'description'.
    """
    images = []
    for img in soup.find_all('img'):
        img_info = {
            'src': img.get('src'),
            'description': clean_whitespace(remove_non_ascii(img.find_next('div', class_='title').get_text(strip=True))) if img.find_next('div', class_='title') else ''
        }
        images.append(img_info)
    return images

def extract_references(soup):
    """
    Extract references from the HTML content.

    Parameters:
    soup (BeautifulSoup): The BeautifulSoup object of the HTML content.

    Returns:
    list: A list of dictionaries containing 'chapter_ref' and 'text' for each reference.
    """
    references = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.startswith('#chapter'):
            references.append({
                'chapter_ref': href.replace('#', ''),
                'text': clean_whitespace(remove_non_ascii(a.get_text(strip=True)))
            })
    return references

def extract_sections(soup):
    """
    Extract sections from the HTML content.

    Parameters:
    soup (BeautifulSoup): The BeautifulSoup object of the HTML content.

    Returns:
    list: A list of dictionaries containing 'title', 'text_content', 'code_blocks', 'images', 'references', and 'section_title' for each section.
    """
    sections = []
    for section in soup.find_all('div', class_='sect2'):
        section_title = section.find('h3').get_text(strip=True) if section.find('h3') else 'Untitled Section'
        section_content = {
            'title': clean_whitespace(remove_non_ascii(section_title)),
            'text_content': f"{clean_whitespace(remove_non_ascii(section_title))}\n\n{extract_text_content(section).strip()}",
            'code_blocks': extract_code_blocks(section),
            'images': extract_images(section),
            'references': extract_references(section),
            'section_title': clean_whitespace(remove_non_ascii(section_title))
        }
        sections.append(section_content)
    return sections

def parse_html_content_with_sections(soup):
    """
    Parse the HTML content and extract sections.

    Parameters:
    html_content (str): The HTML content as a string.

    Returns:
    dict: A dictionary containing 'title' and 'sections' extracted from the HTML content.
    """
    title = extract_title(soup)
    sections = extract_sections(soup)
    
    return {
        'title': title,
        'sections': sections
    }

def get_processed_data():
    """
    Get the processed data from the PROCESSED_DIR directory.

    Returns:
    dict: A dictionary containing the processed data.
    """
    try:
        with open(PROCESSED_DIR / 'processed_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError("The processed_data.json file was not found in the PROCESSED_DIR directory.")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Error decoding the JSON file: {str(e)}", e.doc, e.pos)

if __name__ == "__main__":
    chapters = read_all_chapter_html_files()
    print(f"Read {len(chapters)} chapters")
    print(chapters)