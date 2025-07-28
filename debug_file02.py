from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar
import re

def get_font_name(text_line):
    names = [char.fontname for char in text_line if isinstance(char, LTChar)]
    return names[0] if names else ''

def get_font_size(text_line):
    sizes = [char.size for char in text_line if isinstance(char, LTChar)]
    return max(sizes) if sizes else 0

def is_bold(font_name):
    if not font_name:
        return False
    font_lower = font_name.lower()
    return ('bold' in font_lower or 'heavy' in font_lower or 'black' in font_lower or 
            'semibold' in font_lower or 'demi' in font_lower or 'medium' in font_lower)

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

# Look for headings that should be in the output
target_headings = [
    "2.1 Intended Audience",
    "2.2 Career Paths for Testers", 
    "2.3 Learning Objectives",
    "Acknowledgements",
    "Introduction to the Foundation Level Extensions"
]

print("Looking for missing headings in file02.pdf:")
print("=" * 50)

count = 0
for page_num, page_layout in enumerate(extract_pages('input/file02.pdf')):
    if count > 100:
        break
    for element in page_layout:
        if isinstance(element, LTTextContainer):
            for text_line in element:
                text = clean_text(text_line.get_text())
                if text and any(target in text for target in target_headings):
                    font_name = get_font_name(text_line)
                    font_size = get_font_size(text_line)
                    is_text_bold = is_bold(font_name)
                    print(f'Page {page_num}: "{text}"')
                    print(f'  Font: {font_name}, Size: {font_size:.1f}, Bold: {is_text_bold}')
                    print()
                    count += 1
                elif text and len(text) > 10 and len(text) < 60 and count < 20:
                    # Show some other headings for context
                    font_name = get_font_name(text_line)
                    font_size = get_font_size(text_line)
                    is_text_bold = is_bold(font_name)
                    if is_text_bold or font_size > 11:
                        print(f'Page {page_num}: "{text}" | Font: {font_name} | Size: {font_size:.1f} | Bold: {is_text_bold}')
                        count += 1
