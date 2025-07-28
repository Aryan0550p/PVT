#!/usr/bin/env python3
"""
Adobe India Hackathon 2025 - Challenge 1a
PDF Outline Extractor - Main Processing Script

This script processes all PDF files from /app/input directory and 
generates corresponding JSON files in /app/output directory.

Required format compliance:
- Input: /app/input/*.pdf (read-only)
- Output: /app/output/*.json  
- Processing: <10 seconds for 50-page PDFs
- Architecture: AMD64, offline, no internet access
"""

import sys
import os
from pathlib import Path

# Import the main extraction function from our comprehensive solution
from extract_outline import process_pdfs

def main():
    """Main entry point for Adobe Hackathon solution"""
    print("Adobe India Hackathon 2025 - Challenge 1a")
    print("PDF Outline Extractor - Processing started...")
    
    try:
        # Process all PDFs from input to output
        process_pdfs()
        print("✅ Processing completed successfully!")
        return 0
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
