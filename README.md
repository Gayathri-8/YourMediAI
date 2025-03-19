# FAQ Chatbot with LLM Integration

A smart chatbot that combines FAQ database matching with LLM capabilities. Features a Streamlit web interface and supports document analysis through file uploads.

## Features

- Hybrid response system combining FAQ database and LLM
- Support for multiple file formats (PDF, Images, Text)
- Interactive Streamlit chat interface
- Fuzzy matching for FAQ queries
- Integration with Ollama (Llama 3.2 3B)
- Automatic category detection

## Prerequisites

1. **Python Dependencies**
```bash
pip install streamlit pandas fuzzywuzzy python-Levenshtein requests pillow pytesseract PyPDF2
```

2. **Ollama Setup**
- Install Ollama from [ollama.ai](https://ollama.ai)
- Pull the Llama model:
```bash
ollama pull llama3.2:3b
```

3. **Tesseract OCR**
- Required for image processing
- Installation:
  - Windows: Download from [Tesseract GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
  - Linux: `sudo apt-get install tesseract-ocr`
  - Mac: `brew install tesseract`

## Project Structure

```
.
├── app.py           # Streamlit interface
├── faq_chatbot.py   # Core chatbot logic
├── train.csv        # FAQ dataset
└── README.md        # Documentation
```

## Dataset Format (train.csv)

The FAQ dataset should contain three columns:
- `qtype`: Category of the question
- `Question`: The actual question
- `Answer`: The corresponding answer

## Running the Application

1. Start Ollama service:
```bash
ollama serve
```

2. Launch the Streamlit interface:
```bash
streamlit run app.py
```

3. Access the web interface at `http://localhost:8501`

## Usage Guide

1. **Basic Questions**
   - Type your question in the chat input
   - The system will first try to match it with the FAQ database
   - If no good match is found, it will use the LLM

2. **File Analysis**
   - Upload files using the sidebar
   - Supported formats: PDF, PNG, JPG, JPEG, TXT
   - Ask questions about the uploaded document

3. **Interface Controls**
   - Clear Chat: Use the button in the sidebar
   - File Upload: Available in the sidebar
   - Chat Input: Located at the bottom of the interface

## How It Works

1. **FAQ Matching**
   - Uses fuzzy string matching
   - Configurable matching threshold (default 60%)
   - Returns category and answer if match found

2. **LLM Integration**
   - Uses Ollama's API
   - Processes context from uploaded files
   - Generates contextual responses

3. **Document Processing**
   - PDFs: Extracts text using PyPDF2
   - Images: Uses Tesseract OCR
   - Text files: Direct reading

## Troubleshooting

1. **Ollama Connection Issues**
   - Ensure Ollama service is running
   - Check if model is properly installed
   - Verify port 11434 is available

2. **File Upload Issues**
   - Check file format compatibility
   - Ensure file size is reasonable
   - Verify file permissions

3. **OCR Issues**
   - Confirm Tesseract is properly installed
   - Check image quality and format
   - Verify system PATH includes Tesseract