#!/usr/bin/env python3

import re
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar

def get_font_size(textline):
    sizes = []
    for char in textline:
        if isinstance(char, LTChar):
            sizes.append(char.height)
    return max(sizes) if sizes else 0

def test_german_vocab_detection():
    pdf_path = "input/file07.pdf"
    
    print("=== TESTING GERMAN VOCABULARY DETECTION ===")
    
    for page_num, page_layout in enumerate(extract_pages(pdf_path), start=0):
        if page_num > 3:  # Only check first few pages
            break
            
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                for text_line in element:
                    text = text_line.get_text().strip()
                    if not text or len(text) < 3:
                        continue
                        
                    font_size = get_font_size(text_line)
                    
                    # Test conditions
                    is_short = len(text) < 30
                    in_size_range = font_size >= 11.0 and font_size < 12.0
                    has_verb_marker = '(v)' in text
                    has_german_pattern = re.search(r'^[a-zäöüß]+ \(', text.lower())
                    has_keywords = any(word in text.lower() for word in ['ausziehen', 'anprobieren', 'anziehen', 'nähen', 'stricken', 'färben', 'flicken', 'zusammenpassen', 'abstimmen', 'waschen'])
                    
                    # Check if this matches our German vocab pattern (updated to match main code)
                    is_german_vocab = (
                        is_short and 
                        (has_verb_marker or has_german_pattern or has_keywords)
                    )
                    
                    if font_size >= 10.0 and font_size <= 13.0:  # Show all text in broader size range
                        print(f"Page {page_num} | Size: {font_size:.1f} | Text: '{text}' | German vocab: {is_german_vocab}")
                        if is_german_vocab:
                            print(f"  ✓ MATCHES: short={is_short}, size_range={in_size_range}, verb={has_verb_marker}, pattern={has_german_pattern}, keywords={has_keywords}")

if __name__ == "__main__":
    test_german_vocab_detection()
