import streamlit as st
from streamlit_option_menu import option_menu
import auth
import os
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="LectureLoop AI",
    page_icon="logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. FIREBASE DB INIT (Backend)
if not firebase_admin._apps:
    try:
        # Load from Streamlit Secrets (TOML)
        if "firebase_credentials" in st.secrets:
            # Create a dictionary from the secrets object
            key_dict = dict(st.secrets["firebase_credentials"])
            
            # Handle private key newlines if they are escaped
            if "\\n" in key_dict["private_key"]:
                key_dict["private_key"] = key_dict["private_key"].replace("\\n", "\n")
                
            cred = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(cred)
        else:
            st.error("Firebase credentials not found in st.secrets!")
            st.stop()
            
    except Exception as e:
        st.error(f"Failed to initialize database: {e}")
        st.stop()

# 3. SESSION STATE MANAGEMENT
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'Home'

# 4. MAIN APP LOGIC
def main():
    # --- BEAUTIFUL CSS STYLING WITH VIBRANT COLORS ---
    st.markdown("""
        <style>
            /* Hide Streamlit Branding */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
           /* header {visibility: hidden;} */
            
            /* Main App Background - Light vibrant gradient */
            .stApp {
               background: linear-gradient(135deg, #E0C3FC 0%, #8EC5FC 100%);
                background-attachment: fixed;
            }
            
            /* Main Content Area */
            .main .block-container {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                padding: 2rem;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                backdrop-filter: blur(10px);
                margin-top: 2rem;
            }
            
            /* Sidebar - Beautiful gradient */
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #ffffff 0%, #f8f9ff 50%, #e8eaff 100%);
                border-right: 2px solid rgba(102, 126, 234, 0.2);
            }
            
            /* Profile Card in Sidebar */
            .profile-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 15px;
                margin-bottom: 20px;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
            }
            
            .profile-name {
                font-size: 20px;
                font-weight: bold;
                margin-bottom: 5px;
            }
            
            .profile-email {
                font-size: 14px;
                opacity: 0.9;
                margin-bottom: 10px;
            }
            
            /* Cards - Vibrant with shadows */
            .css-card, div[data-testid="stMetricValue"] {
                background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 4px 20px rgba(102, 126, 234, 0.15);
                margin-bottom: 20px;
                border: 1px solid rgba(102, 126, 234, 0.1);
            }
            
            /* Titles */
            h1 {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                font-weight: 700;
            }
            
            h2, h3 {
                color: #667eea;
                font-weight: 600;
            }
            
            /* Buttons - Vibrant gradient */
            .stButton > button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 0.5rem 1.5rem;
                font-weight: 600;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
            }
            
            .stButton > button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
            }
            
            /* Metrics - Beautiful cards */
            div[data-testid="stMetricContainer"] {
                background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(248,249,255,0.9) 100%);
                padding: 20px;
                border-radius: 15px;
                border: 1px solid rgba(102, 126, 234, 0.2);
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.1);
            }
            
            /* Info boxes - Light vibrant */
            .stInfo {
                background: linear-gradient(135deg, #e0f2fe 0%, #dbeafe 100%);
                border-left: 4px solid #667eea;
                border-radius: 10px;
            }
            
            .stSuccess {
                background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
                border-left: 4px solid #10b981;
                border-radius: 10px;
            }
            
            .stWarning {
                background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
                border-left: 4px solid #f59e0b;
                border-radius: 10px;
            }
            
            /* Input fields */
            .stTextInput > div > div > input {
                border-radius: 10px;
                border: 2px solid rgba(102, 126, 234, 0.2);
                background: rgba(255, 255, 255, 0.9);
            }
            
            .stTextInput > div > div > input:focus {
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            
            /* File uploader */
            .uploadedFile {
                background: linear-gradient(135deg, #f8f9ff 0%, #ffffff 100%);
                border-radius: 10px;
                padding: 15px;
                border: 2px dashed #667eea;
            }
        </style>
    """, unsafe_allow_html=True)

    # --- VIEW CONTROLLER ---
    if not st.session_state.logged_in:
        auth.handle_auth()
    else:
        dashboard_interface()

def load_user_data_from_firebase(user_email):
    """Load user data from Firebase including profile and processed documents"""
    try:
        db = firestore.client()
        user_id = user_email.split('@')[0]
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if user_doc.exists:
            return user_doc.to_dict()
        return None
    except:
        return None

def save_user_data_to_firebase(user_email, data):
    """Save user data to Firebase"""
    try:
        db = firestore.client()
        user_id = user_email.split('@')[0]
        user_ref = db.collection('users').document(user_id)
        user_ref.set(data, merge=True)
        return True
    except:
        return False

def dashboard_interface():
    # Load user data from Firebase on login
    user_email = st.session_state.user.get('email', '')
    if 'user_profile_loaded' not in st.session_state:
        user_data = load_user_data_from_firebase(user_email)
        if user_data:
            # Load saved data into session state
            if 'document_text' in user_data:
                st.session_state['document_text'] = user_data.get('document_text')
            if 'podcast_script' in user_data:
                st.session_state['podcast_script'] = user_data.get('podcast_script')
            if 'flashcards' in user_data:
                st.session_state['flashcards'] = user_data.get('flashcards')
            # 🟢 ADD THIS NEW BLOCK:
            if 'mindmap_code' in user_data:
                st.session_state['mindmap_code'] = user_data.get('mindmap_code')
            # ----------------------
            if 'processed_files' in user_data:
                st.session_state.processed_files = user_data.get('processed_files', [])
        st.session_state.user_profile_loaded = True
    
    # Get user profile info
    user_profile = st.session_state.user.get('profile', {})
    user_name = user_profile.get('name') if user_profile else None
    if not user_name:
        # Try to get from Firebase
        user_data = load_user_data_from_firebase(user_email)
        if user_data and 'name' in user_data:
            user_name = user_data.get('name')
        else:
            # Extract name from email as fallback
            user_name = user_email.split('@')[0].replace('.', ' ').title()
    
    # --- SIDEBAR ---
    with st.sidebar:
        # Check if logo exists before displaying
        if os.path.exists("logo.png"):
            st.image("logo.png", width=250) 
        else:
            st.markdown("## LectureLoop AI")
            
        st.markdown("---") 
        # Profile Card with beautiful design
        st.markdown(f"""
        <div class="profile-card">
            <div style='text-align: center;'>
                <div style='font-size: 48px; margin-bottom: 10px;'>👤</div>
                <div class="profile-name">{user_name}</div>
                <div class="profile-email">{user_email}</div>
                <div style='font-size: 12px; opacity: 0.8; margin-top: 10px;'>
                    📚 Learning Platform
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Profile editing
        with st.expander("✏️ Edit Profile"):
            new_name = st.text_input("Name", value=user_name, key="profile_name_input")
            if st.button("💾 Save Profile", use_container_width=True):
                try:
                    db = firestore.client()
                    user_id = user_email.split('@')[0]
                    user_ref = db.collection('users').document(user_id)
                    user_ref.set({'name': new_name}, merge=True)
                    st.success("Profile updated!")
                    st.rerun()
                except:
                    st.session_state.user['profile'] = {'name': new_name}
                    st.success("Profile updated (local)!")
        
        st.markdown("---")
        
        selected = option_menu(
            menu_title="LectureLoop",
           # Added "Mind Map"
            options=["Home", "Upload & Process", "Podcast", "Flashcards", "Mind Map", "Socratic Chat"],
            # Added "diagram-3"
            icons=["house", "cloud-upload", "mic", "card-text", "diagram-3", "chat-dots"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "5px", "background-color": "transparent"},
                "nav-link": {
                    "font-size": "16px", 
                    "text-align": "left", 
                    "margin": "5px", 
                    "padding": "10px",
                    "border-radius": "10px",
                    "--hover-color": "rgba(102, 126, 234, 0.1)"
                },
                "nav-link-selected": {
                    "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                    "color": "white",
                    "border-radius": "10px",
                },
            }
        )
        
        st.markdown("---")
        if st.button("🚪 Sign Out", use_container_width=True):
            # Save current session data to Firebase before logging out
            try:
                user_data_to_save = {
                    'email': user_email,
                    'name': user_name,
                    'document_text': st.session_state.get('document_text'),
                    'podcast_script': st.session_state.get('podcast_script'),
                    'flashcards': st.session_state.get('flashcards'),
                    'processed_files': st.session_state.get('processed_files', []),
                    'last_updated': firestore.SERVER_TIMESTAMP
                }
                save_user_data_to_firebase(user_email, user_data_to_save)
            except:
                pass
            
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.user_profile_loaded = False
            # Clear session state
            for key in list(st.session_state.keys()):
                if key not in ['logged_in', 'current_view']:
                    del st.session_state[key]
            st.rerun()

    # --- MAIN CONTENT AREA ---
    
    if selected == "Home":
        st.title("Student Dashboard")
        
        # Initialize session state for tracking
        if 'processed_files' not in st.session_state:
            st.session_state.processed_files = []
        if 'total_flashcards' not in st.session_state:
            st.session_state.total_flashcards = 0
        
        # Calculate metrics from session state
        lectures_count = len(st.session_state.processed_files) if 'processed_files' in st.session_state else 0
        
        # Count flashcards from session state
        flashcards_count = 0
        if 'flashcards' in st.session_state and st.session_state['flashcards']:
            try:
                import json
                import ast
                flashcards_data = st.session_state['flashcards']
                if isinstance(flashcards_data, str):
                    try:
                        flashcards_list = json.loads(flashcards_data)
                    except:
                        try:
                            flashcards_list = ast.literal_eval(flashcards_data)
                        except:
                            flashcards_list = []
                else:
                    flashcards_list = flashcards_data
                if isinstance(flashcards_list, list):
                    flashcards_count = len(flashcards_list)
            except:
                flashcards_count = 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Lectures Processed", value=str(lectures_count))
        with col2:
            st.metric(label="Flashcards Created", value=str(flashcards_count))
        with col3:
            # Estimate study hours saved (rough calculation: 1 lecture = 2 hours saved)
            hours_saved = lectures_count * 2
            st.metric(label="Study Hours Saved", value=f"{hours_saved} hrs")
            
        st.markdown("### 📚 Recent Lectures")
        if 'processed_files' in st.session_state and len(st.session_state.processed_files) > 0:
            for idx, file_info in enumerate(reversed(st.session_state.processed_files[-5:]), 1):
                st.markdown(f"**{idx}.** {file_info.get('filename', 'Unknown file')} - {file_info.get('date', 'Recently processed')}")
        else:
            st.info("No lectures uploaded yet. Go to 'Upload & Process' to start.")

    elif selected == "Upload & Process":
        st.title("Upload Materials")
        st.markdown("Upload your lecture recording (MP3) or textbook chapter (PDF).")
        
        uploaded_file = st.file_uploader("Drag and drop file here", type=['pdf'])
        
        if uploaded_file:
            st.success(f"File '{uploaded_file.name}' ready.")
            
            if st.button("Generate Study Guide"):
                try:
                    with st.spinner("Processing with Gemini AI..."):
                        import gemini_brain
                        
                        # 1. Extract Text
                        if uploaded_file.name.endswith('.pdf'):
                            raw_text = gemini_brain.extract_text_from_pdf(uploaded_file)
                            if not raw_text or len(raw_text.strip()) == 0:
                                st.error("Failed to extract text from PDF. The file might be corrupted or image-based.")
                                st.stop()
                        else:
                            raw_text = "Audio processing coming soon." # Placeholder for audio
                            st.warning("Audio processing is not yet implemented. Please upload a PDF file.")

                        # 2. Generate Content
                        try:
                            podcast_script = gemini_brain.generate_podcast_script(raw_text)
                        except Exception as e:
                            st.error(f"Error generating podcast script: {str(e)}")
                            podcast_script = None
                        
                        try:
                            flashcards = gemini_brain.generate_flashcards(raw_text)
                        except Exception as e:
                            st.error(f"Error generating flashcards: {str(e)}")
                            flashcards = None
                        
                        # 3. Save to Session State (so we can see it in other tabs)
                        if podcast_script:
                            st.session_state['podcast_script'] = podcast_script
                        if flashcards:
                            st.session_state['flashcards'] = flashcards
                        # Save raw text for chat functionality
                        st.session_state['document_text'] = raw_text
                        
                        # 4. Track processed file in session state
                        if 'processed_files' not in st.session_state:
                            st.session_state.processed_files = []
                        
                        file_info = {
                            'filename': uploaded_file.name,
                            'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                            'has_podcast': bool(podcast_script),
                            'has_flashcards': bool(flashcards)
                        }
                        st.session_state.processed_files.append(file_info)
                        
                        # 5. Save all data to Firebase for persistence
                        user_email = st.session_state.user.get('email', 'anonymous')
                        try:
                            # Save everything to user's document
                            user_data_to_save = {
                                'email': user_email,
                                'document_text': raw_text,
                                'podcast_script': podcast_script if podcast_script else None,
                                'flashcards': flashcards if flashcards else None,
                                'processed_files': st.session_state.get('processed_files', []),
                                'last_updated': firestore.SERVER_TIMESTAMP
                            }
                            
                            if save_user_data_to_firebase(user_email, user_data_to_save):
                                pass  # Successfully saved
                        except Exception as e:
                            # Silently fail - data is still in session state
                            pass
                        
                        # 6. Success!
                        if podcast_script or flashcards:
                            st.success("✅ Processing Complete! Go to the 'Podcast' or 'Flashcards' tab to view results.")
                        else:
                            st.error("Processing failed. Please check your API key and try again.")
                except Exception as e:
                    st.error(f"An error occurred during processing: {str(e)}")
                    st.info("💡 Troubleshooting tips:\n"
                           "1. Check if your Google API key is valid\n"
                           "2. Ensure Gemini API is enabled in Google Cloud Console\n"
                           "3. Verify billing is enabled (free tier available)\n"
                           "4. Check your internet connection")
    elif selected == "Podcast":
        st.title("🎧 Audio Summaries")
        st.markdown("Listen to your lectures converted into conversational podcasts.")
        
        # Check if podcast script exists in session state
        if 'podcast_script' in st.session_state and st.session_state['podcast_script']:
            st.success("✅ Podcast script available!")
            
            # Display the podcast script
            st.markdown("### 📝 Podcast Transcript")
            st.markdown("---")
            
            # Display the script in a nice format
            script_text = st.session_state['podcast_script']
            st.markdown(f"""
            <div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 4px solid #6A0DAD;'>
                <pre style='white-space: pre-wrap; font-family: Arial, sans-serif; font-size: 14px; line-height: 1.6;'>{script_text}</pre>
            </div>
            """, unsafe_allow_html=True)
            
            # Audio playback using text-to-speech
            st.markdown("---")
            st.markdown("### 🔊 Audio Player")
            
            try:
                from gtts import gTTS
                import io
                
                # Generate audio from text
                if st.button("🎵 Generate & Play Audio", use_container_width=True):
                    with st.spinner("Generating audio... This may take a moment."):
                        try:
                            # Create a temporary file for the audio
                            tts = gTTS(text=script_text, lang='en', slow=False)
                            
                            # Save to bytes buffer
                            audio_buffer = io.BytesIO()
                            tts.write_to_fp(audio_buffer)
                            audio_buffer.seek(0)
                            
                            # Save audio to session state so it persists
                            audio_bytes = audio_buffer.read()
                            st.session_state['podcast_audio'] = audio_bytes
                            
                            st.success("✅ Audio generated successfully!")
                        except Exception as e:
                            st.error(f"Error generating audio: {str(e)}")
                            st.info("💡 Tip: Make sure you have an internet connection for text-to-speech.")
                
                # Play audio if it exists in session state
                if 'podcast_audio' in st.session_state and st.session_state['podcast_audio']:
                    st.audio(st.session_state['podcast_audio'], format='audio/mp3', autoplay=False)
                    
                    # Download audio button
                    st.download_button(
                        label="📥 Download Audio (MP3)",
                        data=st.session_state['podcast_audio'],
                        file_name="podcast_audio.mp3",
                        mime="audio/mp3"
                    )
                else:
                    st.info("💡 Click 'Generate & Play Audio' above to create audio from the transcript.")
                    
            except ImportError:
                st.warning("⚠️ Text-to-speech library not installed. Install it with: pip install gtts")
                st.info("💡 For now, you can read the transcript above.")
            
            # Option to download as text
            st.markdown("---")
            st.download_button(
                label="📥 Download Transcript (TXT)",
                data=script_text,
                file_name="podcast_transcript.txt",
                mime="text/plain"
            )
        else:
            st.warning("⚠️ No podcast script available yet. Go to 'Upload & Process' to generate one!")

    elif selected == "Flashcards":
        st.title("⚡ Active Recall")
        
        # Check if flashcards exist in session state
        if 'flashcards' in st.session_state and st.session_state['flashcards']:
            try:
                import json
                import ast
                
                # Parse the flashcards (they should be a JSON string or list)
                flashcards_data = st.session_state['flashcards']
                
                # Try to parse as JSON string first, then as Python literal
                try:
                    if isinstance(flashcards_data, str):
                        # Try JSON first
                        try:
                            flashcards = json.loads(flashcards_data)
                        except json.JSONDecodeError:
                            # Try Python literal eval
                            flashcards = ast.literal_eval(flashcards_data)
                    else:
                        flashcards = flashcards_data
                    
                    if isinstance(flashcards, list) and len(flashcards) > 0:
                        st.success(f"✅ {len(flashcards)} flashcards available!")
                        
                        # Initialize session state for flashcard navigation
                        if 'current_flashcard_index' not in st.session_state:
                            st.session_state.current_flashcard_index = 0
                        if 'flashcard_flipped' not in st.session_state:
                            st.session_state.flashcard_flipped = False
                        
                        current_idx = st.session_state.current_flashcard_index % len(flashcards)
                        card = flashcards[current_idx]
                        
                        # Display flashcard
                        col1, col2, col3 = st.columns([1, 3, 1])
                        with col2:
                            if st.session_state.flashcard_flipped:
                                card_content = f"""
                                <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                            color: white; padding: 40px; border-radius: 16px; 
                                            min-height: 300px; display: flex; align-items: center; 
                                            justify-content: center; box-shadow: 0 8px 16px rgba(0,0,0,0.2);'>
                                    <div style='text-align: center; width: 100%;'>
                                        <h3 style='color: white; margin-bottom: 20px;'>Answer:</h3>
                                        <p style='font-size: 18px;'>{card.get('answer', 'N/A')}</p>
                                    </div>
                                </div>
                                """
                            else:
                                card_content = f"""
                                <div style='background: white; border: 2px solid #667eea; 
                                            padding: 40px; border-radius: 16px; 
                                            min-height: 300px; display: flex; align-items: center; 
                                            justify-content: center; box-shadow: 0 8px 16px rgba(0,0,0,0.1);'>
                                    <div style='text-align: center; width: 100%;'>
                                        <h3 style='color: #667eea; margin-bottom: 20px;'>Question:</h3>
                                        <p style='font-size: 20px; color: #333; font-weight: 500;'>{card.get('question', 'N/A')}</p>
                                    </div>
                                </div>
                                """
                            st.markdown(card_content, unsafe_allow_html=True)
                            
                            # Flip button
                            if st.button("🔄 Flip Card", use_container_width=True, key="flip_card"):
                                st.session_state.flashcard_flipped = not st.session_state.flashcard_flipped
                                st.rerun()
                        
                        # Navigation buttons
                        col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
                        with col2:
                            if st.button("⏮️ Previous"):
                                st.session_state.current_flashcard_index = (current_idx - 1) % len(flashcards)
                                st.session_state.flashcard_flipped = False
                                st.rerun()
                        with col3:
                            if st.button("Next ⏭️"):
                                st.session_state.current_flashcard_index = (current_idx + 1) % len(flashcards)
                                st.session_state.flashcard_flipped = False
                                st.rerun()
                        
                        # Card counter
                        st.markdown(f"<div style='text-align: center; margin-top: 20px; color: #666; font-size: 14px;'>Card {current_idx + 1} of {len(flashcards)}</div>", unsafe_allow_html=True)
                        
                        # Show all flashcards in expander
                        with st.expander("📚 View All Flashcards"):
                            for i, fc in enumerate(flashcards):
                                st.markdown(f"**Card {i+1}**")
                                st.markdown(f"**Q:** {fc.get('question', 'N/A')}")
                                st.markdown(f"**A:** {fc.get('answer', 'N/A')}")
                                st.markdown("---")
                    else:
                        st.error("Flashcards data is not in the correct format.")
                except Exception as e:
                    st.error(f"Error parsing flashcards: {str(e)}")
                    st.code(st.session_state['flashcards'], language='text')
            except Exception as e:
                st.error(f"Error displaying flashcards: {str(e)}")
        else:
            st.info("ℹ️ Process a document to generate flashcards. Go to 'Upload & Process' to get started!")
    elif selected == "Mind Map":
        st.title("🧠 Concept Map")
        st.markdown("Visualize the connections between ideas in your lecture.")
      
        # Check if we have a document
        if 'document_text' in st.session_state and st.session_state['document_text']:
            
            # Button to generate
            if st.button("Generate Mind Map", type="primary"):
                with st.spinner("Analyzing connections and drawing map..."):
                    try:
                        import gemini_brain
                        # Generate the code
                        dot_code = gemini_brain.generate_mindmap_code(st.session_state['document_text'])
                        st.session_state['mindmap_code'] = dot_code
                        
                        # 🟢 ADD THIS DATABASE SAVE BLOCK:
                        user_email = st.session_state.user.get('email')
                        if user_email:
                            save_user_data_to_firebase(user_email, {'mindmap_code': dot_code})
                        # --------------------------------

                        st.success("Map generated !")
                    except Exception as e:
                        st.error(f"Failed to generate map: {e}")

            # Display the map if it exists in memory
            if 'mindmap_code' in st.session_state:
                st.markdown("---")
                # 1. ATTEMPT TO DRAW
                try:
                    st.graphviz_chart(st.session_state['mindmap_code'])
                except Exception as e:
                    st.error(f"Graph error: {e}")
                
                # Option to regenerate
                if st.button("🔄 Regenerate Map"):
                    del st.session_state['mindmap_code']
                    st.rerun()
        else:
            st.info("👆 Please go to 'Upload & Process' and process a document first!")
    elif selected == "Socratic Chat":
        st.title("🤖 AI Tutor")
        st.markdown("Ask questions about your uploaded document. The AI will help you understand the content.")
        
        # Initialize chat messages
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Check if document is available
        has_document = 'document_text' in st.session_state and st.session_state.get('document_text')
        
        if not has_document:
            st.info("ℹ️ Please upload and process a document in 'Upload & Process' to start chatting about it.")

        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input
        if prompt := st.chat_input("Ask a question about your lecture..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate AI response
            with st.chat_message("assistant"):
                if has_document:
                    try:
                        import gemini_brain
                        with st.spinner("Thinking..."):
                            # Get document content
                            document_text = st.session_state['document_text']
                            # Get chat history (previous messages)
                            chat_history = st.session_state.messages[:-1]  # Exclude current user message
                            
                            # Generate response using Gemini
                            response = gemini_brain.chat_with_document(
                                question=prompt,
                                document_content=document_text,
                                chat_history=chat_history
                            )
                            st.markdown(response)
                            st.session_state.messages.append({"role": "assistant", "content": response})
                    except Exception as e:
                        error_msg = f"Error generating response: {str(e)}"
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
                else:
                    response = "I am ready to help once you upload and process a document! Go to 'Upload & Process' to get started."
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
