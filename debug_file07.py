import os
import re
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar

def debug_file07():
    pdf_path = 'input/file07.pdf'
    
    print("=== FONT ANALYSIS FOR file07.pdf ===")
    all_text_info = []
    
    for page_num, page_layout in enumerate(extract_pages(pdf_path), start=0):
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                for text_line in element:
                    text = text_line.get_text().strip()
                    if not text or len(text) < 3:
                        continue
                        
                    chars = [char for char in text_line if isinstance(char, LTChar)]
                    if not chars:
                        continue
                    
                    # Get font info
                    font_names = [char.fontname for char in chars]
                    font_sizes = [char.size for char in chars]
                    
                    # Determine if bold
                    bold_count = sum(1 for font in font_names if 'Bold' in font or 'BLACK' in font or 'Heavy' in font)
                    bold_ratio = bold_count / len(chars) if chars else 0
                    
                    avg_size = sum(font_sizes) / len(font_sizes) if font_sizes else 0
                    dominant_font = max(set(font_names), key=font_names.count) if font_names else 'Unknown'
                    
                    all_text_info.append({
                        'text': text[:60] + ('...' if len(text) > 60 else ''),
                        'page': page_num,
                        'size': round(avg_size, 1),
                        'font': dominant_font,
                        'bold_ratio': round(bold_ratio, 2),
                        'is_bold': bold_ratio > 0.3
                    })
    
    # Sort by font size (largest first) and show top 30
    all_text_info.sort(key=lambda x: x['size'], reverse=True)
    
    print("\nTOP 30 LARGEST TEXT ELEMENTS:")
    print("Size | Bold | Page | Text")
    print("-" * 80)
    for i, info in enumerate(all_text_info[:30]):
        bold_indicator = "✓" if info['is_bold'] else "✗"
        print(f"{info['size']:4.1f} | {bold_indicator:4} | {info['page']:4} | {info['text']}")
    
    print(f"\nFONT NAMES FOUND:")
    all_fonts = [info['font'] for info in all_text_info]
    unique_fonts = list(set(all_fonts))
    for font in sorted(unique_fonts):
        count = all_fonts.count(font)
        has_bold = 'Bold' in font or 'BLACK' in font or 'Heavy' in font
        print(f"  {font} ({count} times) {'[BOLD]' if has_bold else ''}")
    
    print(f"\nACTUAL BOLD TEXT (Helvetica-Bold):")
    bold_items = [info for info in all_text_info if 'Bold' in info['font']]
    for item in bold_items:
        print(f"  Page {item['page']}: {item['text']} (size: {item['size']})")
        
    print(f"\nMUSEOSANS-500 TEXT (might be bold-equivalent):")
    museo_items = [info for info in all_text_info if 'MuseoSans-500' in info['font']]
    for item in museo_items:
        print(f"  Page {item['page']}: {item['text']} (size: {item['size']})")
        
    print(f"\nPOTENTIAL GERMAN HEADINGS (vocabulary words):")
    # Look for German vocabulary patterns that should be headings
    german_vocab_pattern = [info for info in all_text_info if 
                          len(info['text']) < 30 and  # Short terms (likely vocab)
                          (info['size'] >= 11.0 and info['size'] <= 11.6) and  # Size range from debug analysis
                          ('(v)' in info['text'] or  # Verb indicators
                           '(n)' in info['text'] or  # Noun indicators
                           '(adj)' in info['text'] or  # Adjective indicators
                           re.search(r'^[a-zäöüß]+ \(', info['text'].lower()) or  # Word with parentheses
                           # Expanded vocabulary detection
                           any(word in info['text'].lower() for word in ['ausziehen', 'anprobieren', 'anziehen', 'nähen', 'stricken', 'färben', 'flicken', 'zusammenpassen', 'abstimmen', 'waschen']) or
                           re.search(r'^(einen?|eine|ein|sich|das|die|der) [a-zäöüß]+', info['text'].lower()))]
    
    print(f"Found {len(german_vocab_pattern)} potential German vocabulary headings:")
    for item in german_vocab_pattern:  # Show ALL matches
        print(f"  Page {item['page']}: {item['text']} (size: {item['size']}, font: {item['font']})")

if __name__ == '__main__':
    debug_file07()
