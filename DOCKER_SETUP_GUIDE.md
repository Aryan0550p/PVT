# Docker Installation and Testing Guide

## Step 1: Install Docker
1. Download Docker Desktop from: https://www.docker.com/products/docker-desktop/
2. Install and restart your computer
3. Open PowerShell or Command Prompt

## Step 2: Verify Docker Installation
```bash
docker --version
docker run hello-world
```

## Step 3: Test Our Adobe Hackathon Solution

### Build the Container
```bash
cd "e:\adobe_n1"
docker build --platform linux/amd64 -t pdfoutlineextractor:dev .
```

### Run the Container (Production Mode)
```bash
docker run --rm -v $(pwd)/input:/app/input:ro -v $(pwd)/output:/app/output --network none pdfoutlineextractor:dev
```

### Alternative: Test with PowerShell Syntax
```powershell
docker run --rm -v ${PWD}/input:/app/input:ro -v ${PWD}/output:/app/output --network none pdfoutlineextractor:dev
```

## Step 4: Verify Results
Check that JSON files are generated in the output directory:
- file01.json
- file02.json  
- file03.json
- file04.json
- file05.json
- file06.json
- file07.json

## Expected Output
Each JSON should contain:
- title: Document title
- outline: Array of headings with levels (H1-H4) and page numbers
- languages: Language detection information with multilingual support

## Performance Validation
- Processing time should be <10 seconds for all files
- Memory usage should be <500MB
- All 7 PDFs should be processed successfully

## Troubleshooting
If you encounter issues:
1. Ensure Docker Desktop is running
2. Check that input directory contains PDF files
3. Verify output directory is writable
4. Check Docker logs for errors

---
**Adobe India Hackathon 2025 - Challenge 1a Solution**
**Ready for submission once Docker testing is complete!**
