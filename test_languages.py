#!/usr/bin/env python3

import re

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

# Test with sample text from different languages
test_texts = {
    "English": "This is a sample English text with no special characters.",
    "French": "Bonjour! Comment allez-vous? C'est très intéressant. Merci beaucoup pour votre coopération.",
    "Spanish": "¡Hola! ¿Cómo estás? Me gustaría hablar contigo. ¿Qué tal tu día?",
    "German": "Guten Tag! Wie geht es Ihnen? Das ist sehr schön. Vielen Dank für Ihre Hilfe.",
    "Portuguese": "Olá! Como você está? Muito obrigado pela sua cooperação. É uma grande oportunidade.",
    "Italian": "Ciao! Come stai? È molto interessante. Grazie per la tua collaborazione.",
    "Russian": "Привет! Как дела? Это очень интересно. Спасибо за вашу помощь.",
    "Arabic": "مرحبا! كيف حالك؟ هذا مثير جداً للاهتمام. شكراً لك على مساعدتك.",
    "Chinese": "你好！你好吗？这非常有趣。谢谢你的帮助。",
    "Japanese": "こんにちは！元気ですか？とても面白いです。ご協力ありがとうございます。",
    "Korean": "안녕하세요! 어떻게 지내세요? 매우 흥미롭습니다. 도움을 주셔서 감사합니다.",
    "Hindi": "नमस्ते! आप कैसे हैं? यह बहुत दिलचस्प है। आपकी सहायता के लिए धन्यवाद।",
    "Mixed": "Hello! Bonjour! Hola! Guten Tag! 你好！こんにちは！مرحبا！"
}

print("=== LANGUAGE DETECTION TEST ===\n")

for lang_name, text in test_texts.items():
    detected = detect_languages(text)
    multilingual = is_multilingual(text)
    
    print(f"**{lang_name} Text:**")
    print(f"Text: {text}")
    print(f"Detected languages: {detected}")
    print(f"Is multilingual: {multilingual}")
    print("-" * 60)

print("\n=== SUPPORTED LANGUAGES SUMMARY ===")
print("The code supports detection of these 12 languages:")
print("1. Chinese (中文)")
print("2. Japanese (日本語)")
print("3. Korean (한국어)")
print("4. Arabic (العربية)")
print("5. Russian (Русский)")
print("6. Hindi (हिन्दी)")
print("7. French (Français)")
print("8. Spanish (Español)")
print("9. German (Deutsch)")
print("10. Portuguese (Português)")
print("11. Italian (Italiano)")
print("12. English (default)")
