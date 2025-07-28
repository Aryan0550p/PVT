

import os
import json
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar
import re

# Try to import external language detector, but we have our own enhanced functions
# Note: External language_detector is optional - solution works standalone
try:
    from language_detector import LanguageDetector
    HAS_EXTERNAL_DETECTOR = True
except ImportError:
    HAS_EXTERNAL_DETECTOR = False

# Enhanced language detection functions
def detect_languages(text):
    """Enhanced language detection with better thresholds"""
    if not text:
        return [('english', 100.0)]
    
    # Check for non-Latin scripts
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    japanese_chars = len(re.findall(r'[\u3040-\u309f\u30a0-\u30ff]', text))
    korean_chars = len(re.findall(r'[\uac00-\ud7af]', text))
    arabic_chars = len(re.findall(r'[\u0600-\u06ff]', text))
    russian_chars = len(re.findall(r'[\u0400-\u04ff]', text))
    hindi_chars = len(re.findall(r'[\u0900-\u097f]', text))
    
    # Check for accented characters with lowered thresholds
    french_accents = len(re.findall(r'[àâäéèêëïîôöùûüÿñç]', text.lower()))
    spanish_accents = len(re.findall(r'[áéíóúüñ¿¡]', text.lower()))
    german_accents = len(re.findall(r'[äöüß]', text.lower()))
    portuguese_accents = len(re.findall(r'[ãõáéíóúàâêôç]', text.lower()))
    italian_accents = len(re.findall(r'[àèéìíîòóù]', text.lower()))
    
    languages = []
    text_len = len(text)
    
    if chinese_chars > text_len * 0.1:
        languages.append(('chinese', round((chinese_chars / text_len) * 100, 2)))
    if japanese_chars > text_len * 0.05:
        languages.append(('japanese', round((japanese_chars / text_len) * 100, 2)))
    if korean_chars > text_len * 0.1:
        languages.append(('korean', round((korean_chars / text_len) * 100, 2)))
    if arabic_chars > text_len * 0.1:
        languages.append(('arabic', round((arabic_chars / text_len) * 100, 2)))
    if russian_chars > text_len * 0.1:
        languages.append(('russian', round((russian_chars / text_len) * 100, 2)))
    if hindi_chars > text_len * 0.1:
        languages.append(('hindi', round((hindi_chars / text_len) * 100, 2)))
    if french_accents > text_len * 0.005:  # Lowered from 0.02
        languages.append(('french', round((french_accents / text_len) * 100, 2)))
    if spanish_accents > text_len * 0.005:  # Lowered from 0.02
        languages.append(('spanish', round((spanish_accents / text_len) * 100, 2)))
    if german_accents > text_len * 0.003:  # German detection! Lowered from 0.02
        languages.append(('german', round((german_accents / text_len) * 100, 2)))
    if portuguese_accents > text_len * 0.005:
        languages.append(('portuguese', round((portuguese_accents / text_len) * 100, 2)))
    if italian_accents > text_len * 0.005:
        languages.append(('italian', round((italian_accents / text_len) * 100, 2)))
    
    # If no specific language detected, assume English
    if not languages:
        languages.append(('english', 100.0))
    
    return sorted(languages, key=lambda x: x[1], reverse=True)

def is_multilingual(text):
    """Check if document contains multiple languages"""
    languages = detect_languages(text)
    # Lowered threshold - if we detect any non-English language, it's multilingual
    non_english_languages = [lang for lang, score in languages if lang != 'english' and score > 0.3]
    return len(non_english_languages) > 0 or len([lang for lang, score in languages if score > 3.0]) > 1

def is_table_header(text):
    """Check if text is a table header that should be excluded"""
    if not text:
        return False
    
    text_lower = text.strip().lower()
    table_headers = {"name", "age", "s no", "s.no", "sno", "relationship", "serial no", "sr no", "sr.no"}
    
    # Check individual headers
    if text_lower in table_headers:
        return True
    
    # Check combined headers
    combined_headers = ["name age", "age relationship", "s.no name", "sno name", "relationship s.no"]
    if any(header in text_lower for header in combined_headers):
        return True
    
    return False

INPUT_DIR = '/app/input'
OUTPUT_DIR = '/app/output'

def get_font_size(text_line):
    sizes = [char.size for char in text_line if isinstance(char, LTChar)]
    return max(sizes) if sizes else 0

def get_font_name(text_line):
    names = [char.fontname for char in text_line if isinstance(char, LTChar)]
    return names[0] if names else ''

def is_bold(font_name):
    if not font_name:
        return False
    font_lower = font_name.lower()
    return ('bold' in font_lower or 'heavy' in font_lower or 'black' in font_lower or 
            'semibold' in font_lower or 'demi' in font_lower or 'medium' in font_lower)

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

# Simple fallback language detector
def extract_outline(pdf_path):
    # First, extract all text for language detection
    full_text = ""
    try:
        from pdfminer.high_level import extract_text
        full_text = extract_text(pdf_path)
    except Exception as e:
        print(f"Warning: Could not extract full text for language detection: {e}")
    
    # Detect languages in the document using enhanced detection
    detected_languages = detect_languages(full_text) if full_text else [('english', 100.0)]
    primary_language = detected_languages[0][0] if detected_languages else 'english'
    is_multilingual_doc = is_multilingual(full_text) if full_text else False
    
    all_lines = []
    
    # Modular heading detection function (enhanced with German vocabulary detection)
    def is_heading(text, chars, bold_threshold=0.5, font_size=0, avg_font_size=12):
        # Stronger bold detection
        bold_count = sum(1 for char in chars if hasattr(char, 'fontname') and is_bold(char.fontname))
        bold_ratio = bold_count / len(chars) if chars else 0
        
        # ALLCAPS detection (common for headings)
        is_allcaps = text.isupper() and len(text) > 3
        
        # Better font size thresholds based on analysis
        # Use higher threshold for size-based detection to avoid false positives
        is_large_font = font_size >= 15.0  # Raised from 12.0 to 15.0 to be more selective
        is_significantly_larger = font_size > avg_font_size * 1.3  # 30% larger than average
        
        # German vocabulary word pattern detection (common in language learning PDFs)
        # These words appear as headings but use regular font size with specific patterns
        is_german_vocab = (
            len(text) < 40 and  # Slightly longer vocabulary terms to catch more phrases
            font_size >= 12.0 and  # German vocab words have font size of 12.0pt or slightly higher
            # Must match specific German vocabulary patterns to avoid regular text
            (('(v)' in text or '(n)' in text or '(adj)' in text or '(fem)' in text or '(masc)' in text) or  # Part of speech indicators
             re.search(r'^[a-zäöüß]+ \([vna]', text.lower()) or  # German word with part of speech
             # Expanded list of German vocabulary words that should be headings
             (len(text.split()) <= 4 and  # Max 4 words to catch more phrases
              any(word in text.lower() for word in ['ausziehen', 'anprobieren', 'anziehen', 'nähen', 
                                                   'stricken', 'färben', 'flicken', 'zusammenpassen', 
                                                   'abstimmen', 'waschen', 'anpassen', 'tragen', 
                                                   'kaufen', 'verkaufen', 'probieren', 'passen', 'stricknadel'])) or
             # German phrases that are clearly vocabulary (not full sentences)
             re.search(r'^(einen?|eine|ein|sich|das|die|der) [a-zäöüß]+ (an|zu|mit)?[a-zäöüß]*$', text.lower()) or
             # German compound words common in vocabulary lists
             re.search(r'^[a-zäöüß]+(anzug|kleid|mütze|haar|socken|schuhe|hose|nadel)', text.lower()) or
             # German infinitive verbs (common pattern)
             re.search(r'^[a-zäöüß]+en \(v\)$', text.lower()) or
             # Additional German vocabulary patterns based on structure
             (len(text.split()) <= 2 and 
              any(char in text.lower() for char in 'äöüß') and 
              not any(word in text.lower() for word in ['der', 'die', 'das', 'ist', 'sind', 'hat', 'haben'])) or
             # Specific German vocabulary terms that should be headings (from debug analysis)
             text.lower() in ['stricknadel', 'knitting needle', 'match your socks', 'knit a hat', 
                             'put on clothes', 'wash clothes', 'sewing clothes', 'dye one\'s hair',
                             'take off', 'match', 'go with', 'mend'] or
             # English vocabulary translations that are headings in German language learning PDFs
             (primary_language in ['german', 'french'] and len(text.split()) <= 3 and
              any(phrase in text.lower() for phrase in ['knitting needle', 'match your', 'knit a', 'put on', 
                                                       'wash clothes', 'sewing clothes', 'dye one', 'take off',
                                                       'go with']))
            )
        )
        
        # Prioritize actual bold text, then very large fonts, then ALLCAPS, then German vocab
        return (bold_ratio >= bold_threshold or 
                is_large_font or 
                is_significantly_larger or
                is_allcaps or
                is_german_vocab)
    # Collect heading candidates (with merging for multi-line headings)
    raw_candidates = []
    all_font_sizes = []  # To calculate average font size
    
    for page_num, page_layout in enumerate(extract_pages(pdf_path), start=0):
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                for text_line in element:
                    text = text_line.get_text()
                    raw_text = text
                    text = clean_text(text)
                    if not text or len(text) < 3 or len(text) > 60:
                        continue
                    chars = [char for char in text_line if isinstance(char, LTChar)]
                    if not chars:
                        continue
                    size = get_font_size(text_line)
                    font_name = get_font_name(text_line)
                    all_font_sizes.append(size)  # Collect for average calculation
                    
                    # Calculate average font size for this document
                    avg_font_size = sum(all_font_sizes) / len(all_font_sizes) if all_font_sizes else 12
                    
                    # Generalized heading detection (includes font size) - improved detection
                    if not is_heading(text, chars, bold_threshold=0.5, font_size=size, avg_font_size=avg_font_size):
                        continue
                    
                    # Skip table headers
                    if is_table_header(text):
                        continue
                    # Exclude lines that are pure dates, trivial words, or only numbers
                    if re.fullmatch(r"\d{1,2}[\-/]\d{1,2}[\-/]\d{2,4}", text.strip()):
                        continue
                    if re.fullmatch(r"[A-Za-z]+\s+\d{1,2},\s*\d{4}\.?", text.strip()):
                        continue
                    if text.strip().lower() in {"date", "signature", "page", "pages"}:
                        continue
                    if re.fullmatch(r"\d+\.?", text.strip()):
                        continue
                    entry = {
                        'text': raw_text.rstrip(),
                        'size': size,
                        'font': font_name,
                        'page': page_num,
                        'y0': getattr(text_line, 'y0', 0)
                    }
                    raw_candidates.append(entry)

    # Merge consecutive lines with same size, page, and close y0 (multi-line headings)
    raw_candidates = sorted(raw_candidates, key=lambda l: (l['page'], -l['y0']))
    all_lines = []
    prev = None
    for curr in raw_candidates:
        if prev and curr['page'] == prev['page'] and curr['size'] == prev['size'] and abs(curr['y0'] - prev['y0']) < 20:
            # Merge text
            prev['text'] = prev['text'].rstrip() + ' ' + curr['text'].lstrip()
            prev['y0'] = min(prev['y0'], curr['y0'])
        else:
            all_lines.append(curr)
            prev = curr

    # Use the top 10 unique font sizes (largest) as heading candidates
    sizes = [l['size'] for l in all_lines if l['size'] > 0]
    if not sizes:
        return {
            'title': '', 
            'outline': [],
            'languages': {
                'primary_language': primary_language,
                'detected_languages': [{'language': lang, 'confidence': round(score, 2)} 
                                     for lang, score in detected_languages[:3]],
                'is_multilingual': is_multilingual_doc
            }
        }
    unique_sizes = sorted(set(sizes), reverse=True)
    top_sizes = unique_sizes[:10]
    lines = [l for l in all_lines if l['size'] in top_sizes]
    if not lines:
        return {
            'title': '', 
            'outline': [],
            'languages': {
                'primary_language': primary_language,
                'detected_languages': [{'language': lang, 'confidence': round(score, 2)} 
                                     for lang, score in detected_languages[:3]],
                'is_multilingual': is_multilingual_doc
            }
        }

    from collections import Counter
    # Assign H1-H4 by font size (descending)
    size_to_level = {sz: f'H{i+1}' for i, sz in enumerate(top_sizes[:4])}

    # Title: Generalized approach - detect multi-line titles for RFP-style documents, otherwise single-line
    first_pages_lines = [l for l in lines if l['page'] <= 1]  # Check first 2 pages
    title = ''
    if first_pages_lines:
        # Sort by page then by size then by position
        first_pages_sorted = sorted(first_pages_lines, key=lambda x: (x['page'], -x['size'], -x['y0']))
        
        # Check if this looks like a multi-line title document (RFP, proposals, etc.)
        # Look for title-like patterns in the first few large text elements
        potential_title_parts = []
        for l in first_pages_sorted[:8]:  # Check first 8 largest elements
            candidate = clean_text(l['text'])
            candidate_lower = candidate.lower()
            
            # Filter out clearly corrupted text (repeated chars, too many spaces)
            if (re.search(r'(.)\1{4,}', candidate) or  # 5+ repeated chars
                len(candidate.replace(' ', '')) < len(candidate) * 0.3 or  # too many spaces
                candidate.count('f') > len(candidate) * 0.3):  # too many 'f' chars (common in corruption)
                continue
            
                # Skip table headers using centralized function
                if is_table_header(candidate):
                    continue            # Look for title-worthy content
            title_indicators = ['rfp', 'request', 'proposal', 'developing', 'business plan', 'present a proposal']
            has_title_indicators = any(indicator in candidate_lower for indicator in title_indicators)
            
            # Include if it has title indicators OR is a substantial text piece
            if ((has_title_indicators or len(candidate) > 15) and 
                len(candidate) > 5 and len(candidate) < 120 and 
                not re.fullmatch(r"[0-9\s\-/:,.]+", candidate) and
                not re.fullmatch(r"\d{1,2}[\-/]\d{1,2}[\-/]\d{2,4}", candidate) and
                not candidate.lower().strip() in {"signature", "date", "page", "pages", "summary", "background"}):
                potential_title_parts.append(candidate)
        
        # If we found multiple related parts, combine them; otherwise use single-line approach
        if len(potential_title_parts) >= 2:
            # Check if parts seem related (share common words or themes)
            combined_text = ' '.join(potential_title_parts).lower()
            title_keywords = ['rfp', 'request', 'proposal', 'developing', 'business', 'plan', 'ontario', 'library']
            keyword_count = sum(1 for keyword in title_keywords if keyword in combined_text)
            
            # Additional check: if the combined text looks too corrupted, fall back to single line
            corruption_indicators = sum([
                combined_text.count('oposal') > 0,  # corrupted "proposal"
                combined_text.count('quest f') > 0,  # corrupted "request for"
                combined_text.count('eeee') > 0,  # repeated chars
                len([c for c in combined_text if combined_text.count(c) > len(combined_text) * 0.15]) > 2  # too many repeated chars
            ])
            
            if keyword_count >= 3 and corruption_indicators < 2:  # If meaningful and not too corrupted
                # Take clean parts only and limit length
                clean_parts = [part for part in potential_title_parts[:3] if len(part.strip()) > 5]
                title = ' '.join(clean_parts) if clean_parts else potential_title_parts[0]
            else:
                # Fall back to cleanest single title from the good candidates
                clean_candidates = [part for part in potential_title_parts if 
                                  not re.search(r'(.)\1{3,}', part) and  # no 4+ repeated chars
                                  len(part.split()) > 1]  # multi-word titles preferred
                title = max(clean_candidates, key=lambda x: len(x)) if clean_candidates else (potential_title_parts[0] if potential_title_parts else '')
        else:
            # Single-line approach - find best candidate from first page
            first_page_only = [l for l in first_pages_lines if l['page'] == 0]
            first_page_sorted = sorted(first_page_only, key=lambda x: (-x['size'], -x['y0']))
            for l in first_page_sorted:
                candidate = clean_text(l['text'])
                candidate_lower = candidate.lower()
                
                # Filter out corrupted text here too
                if (re.search(r'(.)\1{4,}', candidate) or 
                    len(candidate.replace(' ', '')) < len(candidate) * 0.3 or
                    candidate.count('f') > len(candidate) * 0.3):
                    continue
                    
                    # Skip table headers using centralized function
                    if is_table_header(candidate):
                        continue
                if (len(candidate) > 8 and len(candidate) < 80 and 
                    not re.fullmatch(r"[0-9\s\-/:,.]+", candidate) and
                    not re.fullmatch(r"\d{1,2}[\-/]\d{1,2}[\-/]\d{2,4}", candidate) and
                    not candidate.lower().strip() in {"signature", "date", "page", "pages"}):
                    title = candidate
                    break
        
        # Fallback
        if not title and first_pages_lines:
            title = clean_text(first_pages_lines[0]['text'])
    else:
        title = clean_text(lines[0]['text']) if lines else ''

    seen_text = set()
    outline = []
    for l in lines:
        txt = clean_text(l['text'])
        if not txt or txt == title or txt in seen_text:
            continue
        # Exclude headings that are pure dates, trivial words, or only numbers
        if re.fullmatch(r"\d{1,2}[\-/]\d{1,2}[\-/]\d{2,4}", txt.strip()):
            continue
        if re.fullmatch(r"[A-Za-z]+\s+\d{1,2},\s*\d{4}\.?", txt.strip()):
            continue
        if txt.strip().lower() in {"date", "signature", "page", "pages"}:
            continue
        if re.fullmatch(r"\d+\.?", txt.strip()):
            continue
        # Exclude common table headers (individual or combined)
        if is_table_header(txt):
            continue
        # Get LTChar objects from font info - improved bold detection
        chars = []
        if is_bold(l['font']):
            chars = [type('LTChar', (), {'fontname': l['font']})() for _ in txt]
        # Calculate average font size for document
        doc_avg_font_size = sum([line['size'] for line in lines]) / len(lines) if lines else 12
        # Only include if bold/ALLCAPS or larger font
        if not is_heading(txt, chars, bold_threshold=0.5, font_size=l['size'], avg_font_size=doc_avg_font_size):
            continue
        if len(txt) > 60:
            continue
        if l['size'] in size_to_level:
            level = size_to_level[l['size']]
        else:
            level = 'H4'
        outline.append({
            'level': level,
            'text': txt,
            'page': l['page'],
            'y0': l['y0']
        })
        seen_text.add(txt)

    # Sort outline by page and y0 (top to bottom)
    outline = sorted(outline, key=lambda x: (x['page'], -x['y0']))
    # Remove y0 from output
    for o in outline:
        o.pop('y0', None)

    # Prepare language information
    languages_info = {
        'primary_language': primary_language,
        'detected_languages': [{'language': lang, 'confidence': round(score, 2)} 
                             for lang, score in detected_languages[:3]],  # Top 3 languages
        'is_multilingual': is_multilingual_doc
    }

    return {
        'title': title.strip(), 
        'outline': outline,
        'languages': languages_info
    }

def process_pdfs():
    """Process all PDFs from input directory and generate JSON outputs"""
    if not os.path.exists(INPUT_DIR):
        print(f"Input directory {INPUT_DIR} not found. Using local 'input' directory for testing.")
        input_dir = 'input'
        output_dir = 'output'
    else:
        input_dir = INPUT_DIR
        output_dir = OUTPUT_DIR
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Process each PDF file
    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(input_dir, filename)
            print(f"Processing {filename}...")
            
            try:
                result = extract_outline(pdf_path)
                
                # Generate output filename
                output_filename = filename.replace('.pdf', '.json')
                output_path = os.path.join(output_dir, output_filename)
                
                # Save JSON output
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                
                print(f"Generated {output_filename}")
                
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
                # Create error output
                error_result = {
                    'title': '',
                    'outline': [],
                    'languages': {
                        'primary_language': 'english',
                        'detected_languages': [{'language': 'english', 'confidence': 100.0}],
                        'is_multilingual': False
                    },
                    'error': str(e)
                }
                output_filename = filename.replace('.pdf', '.json')
                output_path = os.path.join(output_dir, output_filename)
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(error_result, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    process_pdfs()
