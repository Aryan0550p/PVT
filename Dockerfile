# Adobe India Hackathon 2025 - Challenge 1a
# PDF Outline Extractor Solution
FROM --platform=linux/amd64 python:3.12-slim

# Set working directory
WORKDIR /app

# Install only pdfminer.six - minimal dependencies to avoid mirror sync issues
RUN pip install --no-cache-dir pdfminer.six==20231228

# Copy application code
COPY process_pdfs.py .
COPY extract_outline.py .

# Create input and output directories with proper permissions
RUN mkdir -p /app/input /app/output && \
    chmod 755 /app/input /app/output

# Run the main processing script
CMD ["python", "process_pdfs.py"]
