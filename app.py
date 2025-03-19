import streamlit as st
from faq_chatbot import FAQChatbot
import tempfile
import os
from PIL import Image

def initialize_chatbot():
    """Initialize the chatbot and store it in session state."""
    if 'chatbot' not in st.session_state:
        try:
            st.session_state.chatbot = FAQChatbot('train.csv')
            st.session_state.chat_history = []
        except Exception as e:
            st.error(f"Error initializing chatbot: {str(e)}")

def save_uploaded_file(uploaded_file):
    """Save uploaded file temporarily and return the file path."""
    try:
        if uploaded_file is not None:
            # Create a temporary file
            temp_dir = tempfile.mkdtemp()
            file_path = os.path.join(temp_dir, uploaded_file.name)
            
            # Write the file
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # If it's an image, display it
            if uploaded_file.type.startswith('image/'):
                try:
                    image = Image.open(file_path)
                    st.sidebar.image(image, caption='Uploaded Image', use_column_width=True)
                except Exception as e:
                    st.sidebar.error(f"Error displaying image: {str(e)}")
            
            return file_path
    except Exception as e:
        st.error(f"Error saving file: {str(e)}")
        return None
    return None

def main():
    st.title("FAQ Chatbot Assistant")
    
    # Initialize chatbot
    initialize_chatbot()
    
    # Sidebar for file upload
    with st.sidebar:
        st.header("Upload Files")
        uploaded_file = st.file_uploader(
            "Upload a file (PDF, Image, or Text)",
            type=['pdf', 'png', 'jpg', 'jpeg', 'txt']
        )
        
        # Display file details if uploaded
        if uploaded_file:
            st.write("File Details:")
            st.write(f"- Name: {uploaded_file.name}")
            st.write(f"- Type: {uploaded_file.type}")
            st.write(f"- Size: {uploaded_file.size} bytes")
        
        file_path = None
        if uploaded_file:
            file_path = save_uploaded_file(uploaded_file)
            if file_path:
                st.success("File uploaded successfully!")
            else:
                st.error("Failed to process the uploaded file")

    # Add system status indicators
    with st.sidebar:
        st.write("System Status:")
        try:
            # Test Tesseract
            import pytesseract
            pytesseract.get_tesseract_version()
            st.success("✓ Tesseract OCR: Connected")
        except:
            st.error("✗ Tesseract OCR: Not Found")
        
        # Test Ollama
        try:
            import requests
            requests.get('http://localhost:11434/api/tags')
            st.success("✓ Ollama: Connected")
        except:
            st.error("✗ Ollama: Not Connected")

    # Chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask your question..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get chatbot response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.chatbot.get_response(prompt, file_path)
                st.markdown(response)
                
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

    # Clear chat button
    if st.sidebar.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.rerun()

if __name__ == "__main__":
    main() 
