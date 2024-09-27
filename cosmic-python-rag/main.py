import argparse
import os
from cosmic-python-rag_rag.data.data_cleaning import get_processed_data
from cosmic-python-rag_rag.generation import generate_answer
from cosmic-python-rag_rag.indexing import process_and_index_chapters
from cosmic-python-rag_rag.config import ENTER_QUESTION_PHRASE, GOODBYE_PHRASE, PROCESSED_DIR, WELCOME_PHRASE, loading_animation
import threading
import sys

def run_chatbot():
    from cosmic-python-rag_rag.retreival import get_rag_response
    
    print(WELCOME_PHRASE)
    processed_data = get_processed_data()
    
    while True:
        query = input(ENTER_QUESTION_PHRASE).strip()
            
        if query.lower() == 'exit':
            print(GOODBYE_PHRASE)
            break
        
        if query:
            try:
                top_sections, matched_keywords = get_rag_response(query, processed_data)
                    
                loading = [True]
                thread = threading.Thread(target=loading_animation, args=(loading,))
                thread.start()

                answer = generate_answer(query, top_sections)

                loading[0] = False
                thread.join()
                # Clear the animation line
                sys.stdout.write('\r' + ' ' * 30 + '\r')  
                sys.stdout.flush()

                print("\nAnswer:")
                print(answer)
                
                print("\n")
                print("Relevant sections found:")
                for i, section in enumerate(top_sections, 1):
                    chapter_num = section['chapter_num']
                    chapter_title = section['chapter_title']
                    section_title = section['section_title']
                    similarity_score = section['similarity_score']
                    print(f"{i}. Chapter {chapter_num}: {chapter_title}")
                    print(f"   Section: {section_title}")
                    print(f"   Similarity Score: {similarity_score:.4f}")
                
                if matched_keywords:
                    print("\nMatched keywords:")
                    for chapter_num, keywords in matched_keywords.items():
                        if keywords:
                            chapter_title = processed_data[chapter_num]['chapter_title']
                            print(f"Chapter {chapter_num} - {chapter_title}: {', '.join(keywords)}")
            except Exception as e:
                print(f"An error occurred while processing the response: {str(e)}")
                print("Please try again or rephrase your question.")
        else:
            print("Please enter a valid question.")
    pass


def main():
    parser = argparse.ArgumentParser(description="Run indexing or chatbot on the data.")
    parser.add_argument("mode", choices=["indexing", "chatbot"], 
                        help="Mode to run the script in: 'indexing' or 'chatbot'")
    args = parser.parse_args()

    if args.mode == "chatbot" and not os.listdir(PROCESSED_DIR):
        print("No data in processed directory. Cannot run chatbot.")
        return

    run_function = process_and_index_chapters if args.mode == "indexing" else run_chatbot
    run_function()

if __name__ == "__main__":
    main()
