#!/usr/bin/env python3

import os
import sys
sys.path.append('.')

from extract_outline import extract_outline

if __name__ == "__main__":
    pdf_path = "input/file07.pdf"
    result = extract_outline(pdf_path)
    
    print("All headings found:")
    for item in result["outline"]:
        print(f"  {item['level']}: {item['text']} (page {item['page']})")
    
    print(f"\nGerman vocabulary headings found:")
    german_headings = []
    for item in result["outline"]:
        if any(word in item["text"].lower() for word in ["ausziehen", "anprobieren", "anziehen", "nähen", "stricken", "färben", "flicken", "zusammenpassen", "abstimmen"]) or "(v)" in item["text"]:
            german_headings.append(item)
            print(f"  {item['level']}: {item['text']} (page {item['page']})")
    
    print(f"\nTotal headings: {len(result['outline'])}")  
    print(f"German vocab headings: {len(german_headings)}")
    print(f"Multilingual: {result['languages']['is_multilingual']}")
