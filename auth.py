import os
import requests
import streamlit as st

# PASTE YOUR WEB API KEY HERE FROM STEP 1
FIREBASE_WEB_API_KEY = "AIzaSyCjg65sbYtvGEeYG--sbMG1tlw2b60WohE"

def sign_in_with_email_and_password(email, password):
    request_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {"email": email, "password": password, "returnSecureToken": True}
    return requests.post(request_url, headers=headers, json=payload)

def sign_up_with_email_and_password(email, password):
    request_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_WEB_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {"email": email, "password": password, "returnSecureToken": True}
    return requests.post(request_url, headers=headers, json=payload)

def handle_auth():
    if 'user' not in st.session_state:
        st.session_state.user = None

    # Style the container
    st.markdown("""
    <style>
    /* Make the text inputs look like "cards" */
    .stTextInput input {
        padding: 12px;
        border-radius: 10px;
        border: 1px solid #E5E7EB;
        background-color: #F9FAFB;
    }
    /* Make the button purple and wide */
    .stButton button {
        background-color: #7C3AED;
        color: white;
        border-radius: 10px;
        padding: 12px;
        font-weight: bold;
        border: none;
    }
    .stButton button:hover {
        background-color: #6D28D9;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    
    with col2:
        st.title("LectureLoop AI")
        tab1, tab2 = st.tabs(["Login", "Sign Up"])

        with tab1:
            email_in = st.text_input("Email", key="login_email")
            pass_in = st.text_input("Password", type="password", key="login_pass")
            if st.button("Log In", use_container_width=True):
                if email_in and pass_in:
                    resp = sign_in_with_email_and_password(email_in, pass_in)
                    if resp.status_code == 200:
                        user_data = resp.json()
                        st.session_state.user = user_data
                        st.session_state.logged_in = True
                        st.success("Success! Reloading...")
                        st.rerun()
                    else:
                        st.error(f"Login failed: {resp.json().get('error', {}).get('message')}")

        with tab2:
            name_up = st.text_input("Full Name", key="signup_name")
            email_up = st.text_input("Email", key="signup_email")
            pass_up = st.text_input("Password", type="password", key="signup_pass")
            if st.button("Create Account", use_container_width=True):
                if email_up and pass_up:
                    resp = sign_up_with_email_and_password(email_up, pass_up)
                    if resp.status_code == 200:
                        # Save name to Firebase if provided
                        if name_up:
                            try:
                                import firebase_admin
                                from firebase_admin import firestore
                                db = firestore.client()
                                user_id = email_up.split('@')[0]
                                db.collection('users').document(user_id).set({
                                    'name': name_up,
                                    'email': email_up
                                }, merge=True)
                            except:
                                pass
                        st.success("Account created! Please log in.")
                    else:
                        st.error(f"Error: {resp.json().get('error', {}).get('message')}")
                else:
                    st.warning("Please fill in all required fields.")