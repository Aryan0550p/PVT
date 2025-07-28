#!/usr/bin/env python3

import re
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar

def get_font_size(text_line):
    """Same function as in extract_outline.py"""
    sizes = [char.size for char in text_line if isinstance(char, LTChar)]
    return max(sizes) if sizes else 0

def debug_font_size_calculation():
    pdf_path = "input/file07.pdf"
    
    print("=== FONT SIZE CALCULATION DEBUG ===")
    
    # German vocabulary words we expect to find
    target_words = [
        'ausziehen (v)', 'anprobieren (v)', 'anziehen (v)', 
        'nähen (v)', 'stricken (v)', 'färben (v)', 'nicht zusammenpassen (v)',
        'zusammenpassen mit (v)', 'abstimmen (v)', 'ﬂicken (v)'
    ]
    
    for page_num, page_layout in enumerate(extract_pages(pdf_path), start=0):
        if page_num > 4:  # Check first 5 pages
            break
            
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                for text_line in element:
                    text = text_line.get_text().strip()
                    if not text or len(text) < 3:
                        continue
                    
                    # Check if this is one of our target German vocabulary words
                    if any(target in text for target in target_words):
                        font_size = get_font_size(text_line)  # Using same method as extract_outline.py
                        
                        # Debug individual character sizes
                        char_sizes = [char.size for char in text_line if isinstance(char, LTChar)]
                        avg_size = sum(char_sizes) / len(char_sizes) if char_sizes else 0
                        
                        print(f"Page {page_num}: '{text}'")
                        print(f"  Max size (extract_outline method): {font_size:.1f}")
                        print(f"  Avg size (debug method): {avg_size:.1f}")
                        print(f"  Individual char sizes: {char_sizes}")
                        
                        # Test German vocab detection
                        is_german_vocab = (
                            len(text) < 30 and  
                            font_size >= 11.0 and font_size <= 11.6 and
                            ('(v)' in text or '(n)' in text or '(adj)' in text or
                             any(word in text.lower() for word in ['ausziehen', 'anprobieren', 'anziehen', 'nähen', 'stricken', 'färben', 'flicken', 'zusammenpassen', 'abstimmen', 'waschen']))
                        )
                        print(f"  Would be detected as German vocab: {is_german_vocab}")
                        print()

if __name__ == "__main__":
    debug_font_size_calculation()
