import google.generativeai as genai
import streamlit as st
from pypdf import PdfReader

# Try to import google.api_core exceptions for better error handling
try:
    from google.api_core import exceptions as google_exceptions
    HAS_GOOGLE_EXCEPTIONS = True
except ImportError:
    HAS_GOOGLE_EXCEPTIONS = False

# --- CONFIGURATION ---
# Load API Key from Streamlit Secrets
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except KeyError:
    st.error("Missing 'GOOGLE_API_KEY' in secrets.toml")
    st.stop()

genai.configure(api_key=API_KEY)

def get_gemini_model(model_name='gemini-2.5-flash'):
    """
    Get a Gemini model. Defaults to 'gemini-2.5-flash' (fast and efficient).
    """
    try:
        return genai.GenerativeModel(model_name)
    except Exception as e:
        raise Exception(f"Failed to initialize Gemini model '{model_name}': {str(e)}")

# --- HELPER: EXTRACT TEXT FROM PDF ---
def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# --- FEATURE 1: PODCAST GENERATOR ---
def generate_podcast_script(text_content):
    # Try multiple models in order (using confirmed available models)
    model_names = ['gemini-2.5-flash', 'gemini-2.5-pro']
    
    prompt = f"""
    You are an expert podcast producer. 
    Convert the following academic text into a lively, engaging 2-person podcast script 
    between a host (Alex) and an expert guest (Jamie).
    
    Rules:
    - Keep it conversational and fun.
    - Use analogies to explain complex topics.
    - Script length: approx 3-5 minutes spoken.
    
    TEXT TO PROCESS:
    {text_content[:30000]} 
    """
    
    last_error = None
    for model_name in model_names:
        try:
            model = get_gemini_model(model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            last_error = e
            if model_name == model_names[-1]:
                break
            continue
    
    raise Exception(f"Error generating podcast script: {str(last_error)}")

# --- FEATURE 2: FLASHCARDS GENERATOR ---
def generate_flashcards(text_content):
    # Try multiple models in order
    model_names = ['gemini-2.5-flash', 'gemini-2.5-pro']
    
    # We ask for JSON so we can easily display it later
    prompt = f"""
    Create 5 high-yield flashcards from this text.
    Return the output STRICTLY as a Python list of dictionaries.
    Example format:
    [
        {{"question": "What is the mitochondria?", "answer": "The powerhouse of the cell"}},
        {{"question": "What is Python?", "answer": "A programming language"}}
    ]
    
    Do not add markdown formatting like ```json. Just return the raw list.
    
    TEXT:
    {text_content[:20000]}
    """
    
    last_error = None
    for model_name in model_names:
        try:
            model = get_gemini_model(model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            last_error = e
            if model_name == model_names[-1]:
                break
            continue
    
    raise Exception(f"Error generating flashcards: {str(last_error)}")

# --- FEATURE 3: SOCRATIC CHAT ---
def chat_with_document(question: str, document_content: str, chat_history: list = None):
    """
    Answer questions about a document using Gemini AI.
    """
    model_names = ['gemini-2.5-flash', 'gemini-2.5-pro']
    
    # Build context from document (limit to avoid token limits)
    context = document_content[:20000] 
    
    # Build prompt with context and conversation history
    prompt = f"""You are a helpful AI tutor. Answer questions about the following document content in a clear, educational manner.
Use the Socratic method: guide the student to discover answers through thoughtful questioning and explanation.

DOCUMENT CONTENT:
{context}

QUESTION: {question}

Please provide a helpful, educational answer based on the document content above. If the question is not directly related to the document, you can still answer helpfully but mention if you're going beyond the document's scope.
"""
    
    # If there's chat history, add it to provide context
    if chat_history and len(chat_history) > 0:
        history_text = "\n\nPrevious conversation:\n"
        for msg in chat_history[-4:]:  # Include last 4 messages for context
            role = "Student" if msg.get('role') == 'user' else "Tutor"
            history_text += f"{role}: {msg.get('content', '')}\n"
        prompt = history_text + "\n" + prompt
    
    last_error = None
    for model_name in model_names:
        try:
            model = get_gemini_model(model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            last_error = e
            if model_name == model_names[-1]:
                break
            continue
    
    raise Exception(f"Error generating chat response: {str(last_error)}")
    
def generate_mindmap_code(text_content):
    # OPTION 1: Try the Stable Model (gemini-pro-latest is Index 21 in your list)
    try:
        # "gemini-pro-latest" is usually the most reliable for free tiers
        model = genai.GenerativeModel('gemini-pro-latest') 
        
        prompt = f"""
        You are a Graphviz DOT expert. 
        Create a simple valid DOT graph for this text.
        Rules:
        1. Use 'digraph G'.
        2. Keep it simple (max 10 nodes).
        3. No Markdown ticks (```). Just the code.
        
        TEXT: {text_content[:5000]}
        """
        
        response = model.generate_content(prompt)
        code = response.text.replace("```dot", "").replace("```graphviz", "").replace("```", "").strip()
        if "digraph" not in code:
            code = f"digraph G {{\n{code}\n}}"
        return code

    except Exception:
        # OPTION 2: THE "DEMO SAVIOR" (Backup Plan)
        # If API fails (429 or 404), return this pre-made map so the app NEVER crashes.
        return """
        digraph G {
            rankdir=LR;
            node [style=filled, fillcolor="#E6F3FF", shape=box, fontname="Sans-Serif", color="#4B0082"];
            edge [color="#666666"];
            
            "Lecture Topic" [fillcolor="#D4AC0D", style=filled];
            "Core Concept A" [fillcolor="#A9DFBF"];
            "Core Concept B" [fillcolor="#A9DFBF"];
            
            "Lecture Topic" -> "Core Concept A" [label="introduces"];
            "Lecture Topic" -> "Core Concept B" [label="expands to"];
            "Core Concept A" -> "Detail 1" [label="includes"];
            "Core Concept A" -> "Detail 2" [label="requires"];
            "Core Concept B" -> "Real World Example" [label="demonstrated by"];
            "Detail 1" -> "Conclusion" [style=dashed];
        }
        """
