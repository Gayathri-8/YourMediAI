import streamlit as st
from faq_chatbot import FAQChatbot
import tempfile
import os
from PIL import Image
st.set_page_config(
    page_title="YourMediAI Assistant",
    page_icon="🏥",
    layout="wide"
)
def local_css():
    st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stApp {
        background-color: #f8f9fa;
    }
    .css-1d391kg {
        padding: 2rem 1rem;
    }
    .st-bw {
        background-color: #ffffff;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 5px solid #2196f3;
    }
    .bot-message {
        background-color: #f1f8e9;
        border-left: 5px solid #4caf50;
    }
    .chat-header {
        color: #1976d2;
        font-size: 2.5rem;
        font-weight: 600;
        margin-bottom: 2rem;
        text-align: center;
    }
    .sidebar-header {
        color: #1976d2;
        font-size: 1.2rem;
        font-weight: 500;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

def initialize_chatbot():
    if 'chatbot' not in st.session_state:
        try:
            st.session_state.chatbot = FAQChatbot('train.csv')
            st.session_state.chat_history = []
        except Exception as e:
            st.error(f"Error initializing chatbot: {str(e)}")

def save_uploaded_file(uploaded_file):
    try:
        if uploaded_file is not None:
            temp_dir = tempfile.mkdtemp()
            file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
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
    local_css()
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    with st.sidebar:
        st.markdown("<div class='sidebar-header'></div>", unsafe_allow_html=True)
        st.markdown("### 📎 Upload Documents")
        uploaded_file = st.file_uploader(
            "Upload medical documents or images",
            type=['pdf', 'png', 'jpg', 'jpeg', 'txt'],
            help="Supported formats: PDF, PNG, JPG, JPEG, TXT"
        )
        if uploaded_file:
            st.success("✅ File uploaded successfully!")
            st.info("📝 File Details:")
            st.write(f"- Name: {uploaded_file.name}")
            st.write(f"- Type: {uploaded_file.type}")
            st.write(f"- Size: {uploaded_file.size / 1024:.2f} KB")
        st.markdown("### 🔧 System Status")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Ollama**")
            try:
                import requests
                requests.get('http://localhost:11434/api/tags')
                st.success("Connected")
            except:
                st.error("Offline")
        with col2:
            st.markdown("**OCR**")
            try:
                import pytesseract
                pytesseract.get_tesseract_version()
                st.success("Ready")
            except:
                st.error("Not Found")
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    st.markdown("<div class='chat-header'> YourMediAI </div>", unsafe_allow_html=True)
    initialize_chatbot()
    for message in st.session_state.messages:
        with st.container():
            st.markdown(
                f"<div class='chat-message {'user-message' if message['role'] == 'user' else 'bot-message'}'>"
                f"<b>{'You' if message['role'] == 'user' else 'YourMediAI'}:</b><br>{message['content']}"
                "</div>",
                unsafe_allow_html=True
            )
    file_path = save_uploaded_file(uploaded_file) if uploaded_file else None
    user_input = st.chat_input("Ask your medical question here...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("🤔 Thinking..."):
            response = st.session_state.chatbot.get_response(user_input, file_path)
            st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

if __name__ == "__main__":
    main()
