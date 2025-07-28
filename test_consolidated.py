#!/usr/bin/env python3

import sys
sys.path.append('.')

from extract_outline_backup import extract_outline

if __name__ == "__main__":
    pdf_path = "input/file07.pdf"
    result = extract_outline(pdf_path)
    
    print("=== CONSOLIDATED SOLUTION TEST - file07.pdf ===")
    print(f"Title: {result['title']}")
    print(f"Total headings: {len(result['outline'])}")
    print(f"Multilingual: {result['languages']['is_multilingual']}")
    print(f"Primary language: {result['languages']['primary_language']}")
    
    print(f"\nGerman vocabulary headings found:")
    german_headings = []
    for item in result["outline"]:
        if any(word in item["text"].lower() for word in ["ausziehen", "anprobieren", "anziehen", "nähen", "stricken", "färben", "flicken", "zusammenpassen", "abstimmen", "waschen"]) or "(v)" in item["text"]:
            german_headings.append(item)
            print(f"  {item['level']}: {item['text']} (page {item['page']})")
    
    print(f"\nSummary:")
    print(f"  Total headings: {len(result['outline'])}")
    print(f"  German vocabulary headings: {len(german_headings)}")
    print(f"  Is multilingual: {result['languages']['is_multilingual']}")
    print(f"  Languages detected: {[lang['language'] for lang in result['languages']['detected_languages']]}")
