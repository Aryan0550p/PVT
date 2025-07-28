#!/usr/bin/env python3

import sys
sys.path.append('.')

from extract_outline_backup import extract_outline, get_font_size, clean_text
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar
import re

def find_missing_german_vocab():
    pdf_path = "input/file07.pdf"
    
    print("=== COMPREHENSIVE GERMAN VOCABULARY SEARCH ===")
    
    # Get current detected headings
    result = extract_outline(pdf_path)
    current_german_headings = set()
    for item in result["outline"]:
        if any(word in item["text"].lower() for word in ["ausziehen", "anprobieren", "anziehen", "nähen", "stricken", "färben", "flicken", "zusammenpassen", "abstimmen", "waschen"]) or "(v)" in item["text"] or "(n)" in item["text"] or "(adj)" in item["text"]:
            current_german_headings.add(item["text"])
    
    print(f"Currently detected German headings ({len(current_german_headings)}):")
    for heading in sorted(current_german_headings):
        print(f"  ✓ {heading}")
    
    print(f"\nScanning for potential missing German vocabulary...")
    
    # Scan all text in the PDF for potential German vocabulary
    all_potential_vocab = []
    
    for page_num, page_layout in enumerate(extract_pages(pdf_path), start=0):
        if page_num > 5:  # Check first 6 pages
            break
            
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                for text_line in element:
                    text = clean_text(text_line.get_text())
                    if not text or len(text) < 3 or len(text) > 40:
                        continue
                    
                    font_size = get_font_size(text_line)
                    
                    # Look for potential German vocabulary patterns
                    is_potential_german = (
                        # Part of speech indicators
                        ('(v)' in text or '(n)' in text or '(adj)' in text or '(fem)' in text) or
                        # German characters
                        any(char in text.lower() for char in 'äöüß') or
                        # Common German words
                        any(word in text.lower() for word in ['ausziehen', 'anprobieren', 'anziehen', 'nähen', 'stricken', 'färben', 'flicken', 'zusammenpassen', 'abstimmen', 'waschen', 'kleidung', 'anzug', 'mantel', 'mütze', 'haar', 'socken']) or
                        # German articles + word
                        re.search(r'^(einen?|eine|ein|sich|das|die|der) [a-zäöüß]', text.lower()) or
                        # Short German-like words
                        (len(text.split()) <= 3 and re.search(r'[a-zäöüß]{4,}', text.lower()))
                    )
                    
                    if is_potential_german and font_size >= 11.0:
                        # Check if it's already detected
                        is_detected = text in current_german_headings
                        all_potential_vocab.append({
                            'text': text,
                            'page': page_num,
                            'size': font_size,
                            'detected': is_detected
                        })
    
    # Show potential missing vocabulary
    missing_vocab = [item for item in all_potential_vocab if not item['detected']]
    
    print(f"\nPotential missing German vocabulary ({len(missing_vocab)}):")
    for item in sorted(missing_vocab, key=lambda x: x['size'], reverse=True)[:20]:  # Top 20 by size
        print(f"  ❌ Page {item['page']}: '{item['text']}' (size: {item['size']:.1f})")
    
    print(f"\nSummary:")
    print(f"  Current detected: {len(current_german_headings)}")
    print(f"  Potential missing: {len(missing_vocab)}")
    print(f"  Total potential: {len(all_potential_vocab)}")

if __name__ == "__main__":
    find_missing_german_vocab()
