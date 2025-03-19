import pandas as pd
from fuzzywuzzy import fuzz
from typing import Tuple, Optional
import requests
import json
from PIL import Image
import pytesseract
import os
from transformers import pipeline
import PyPDF2
import io

class FAQChatbot:
    def __init__(self, data_path: str):
        self.faq_data = pd.read_csv(data_path)
        required_cols = ['qtype', 'Question', 'Answer']
        if not all(col in self.faq_data.columns for col in required_cols):
            raise ValueError("Dataset must contain 'qtype', 'Question', and 'Answer' columns")
        
        print("Using Ollama with Llama 3.2 3B model...")

        try:
            self._generate_ollama_response("test")
            print("Ollama connection successful!")
        except Exception as e:
            print(f"Error connecting to Ollama: {e}")
            raise

    def _generate_ollama_response(self, prompt: str) -> str:

        try:
            response = requests.post('http://localhost:11434/api/generate',
                                  json={
                                      'model': 'llama3.2:3b',
                                      'prompt': prompt,
                                      'stream': False
                                  })
            response.raise_for_status()
            return response.json()['response']
        except Exception as e:
            print(f"Error generating Ollama response: {e}")
            return "I apologize, but I'm having trouble generating a response at the moment."

    def process_attachment(self, file_path: str) -> str:

        try:
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                image = Image.open(file_path)
                text = pytesseract.image_to_string(image)
                return text.strip()
            elif file_path.lower().endswith('.pdf'):
                text = ""
                with open(file_path, 'rb') as file:
                    # Create PDF reader object
                    pdf_reader = PyPDF2.PdfReader(file)
                    
                    # Extract text from each page
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                return text.strip()
            elif file_path.lower().endswith(('.txt', '.csv')):
                with open(file_path, 'r', encoding='utf-8') as file:
                    return file.read().strip()
            return ""
        except Exception as e:
            print(f"Error processing attachment: {e}")
            return ""

    def generate_llm_response(self, query: str, context: str = "") -> str:
        try:
            max_context_length = 2000
            if len(context) > max_context_length:
                context = context[:max_context_length] + "..."
            prompt = f"""Context: {context}

Question: {query}

Please provide a helpful and accurate response based on the given context and question. If the context is from a document, use specific information from it."""

            return self._generate_ollama_response(prompt)
        except Exception as e:
            print(f"Error generating response: {e}")
            return "I apologize, but I'm having trouble generating a response at the moment."

    def find_best_match(self, user_input: str, threshold: int = 60) -> Tuple[Optional[str], Optional[str], float]:
        """
        Find the best matching question and its answer from the dataset.
        Returns: (answer, category, match_score)
        """
        best_score = 0
        best_match = None
        best_category = None

        for _, row in self.faq_data.iterrows():
            score = fuzz.token_sort_ratio(user_input.lower(), row['Question'].lower())
            
            if score > best_score:
                best_score = score
                best_match = row['Answer']
                best_category = row['qtype']

        if best_score >= threshold:
            return best_match, best_category, best_score
        return None, None, best_score

    def get_response(self, user_input: str, attachment_path: str = None) -> str:
        context = ""
        if attachment_path:
            context = self.process_attachment(attachment_path)
        answer, category, score = self.find_best_match(user_input)
        if answer and score >= 60:
            return f"Category: {category}\nAnswer: {answer}"
        print("Using LLM for response generation...")
        llm_response = self.generate_llm_response(user_input, context)
        return f"AI Generated Response:\n{llm_response}"

def main():
    chatbot = FAQChatbot('train.csv')
    
    print("FAQ YourMediAI initialized. Type 'quit' to exit.")
    print("You can also provide attachments by typing 'file:' followed by the file path")
    
    while True:
        user_input = input("\nYour question: ").strip()
        
        if user_input.lower() == 'quit':
            print("Goodbye!")
            break

        attachment_path = None
        if user_input.startswith('file:'):
            attachment_path = user_input[5:].strip()
            user_input = input("Please enter your question about the file: ").strip()
            
        response = chatbot.get_response(user_input, attachment_path)
        print("\n" + response)

if __name__ == "__main__":
    main() 
