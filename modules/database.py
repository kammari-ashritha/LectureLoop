import firebase_admin
from firebase_admin import credentials, firestore
import os
from typing import Dict, List, Any, Optional


class FirestoreDB:
    """Firestore database connection and operations class"""
    
    def __init__(self):
        self.db = None
        self.initialized = False
    
    def connect(self, credential_path: str = "firebase_key.json") -> bool:
        """
        Initialize Firebase Admin SDK and connect to Firestore
        
        Args:
            credential_path: Path to the Firebase service account JSON file
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Check if Firebase is already initialized
            if not firebase_admin._apps:
                # Check if credential file exists
                if not os.path.exists(credential_path):
                    raise FileNotFoundError(
                        f"Firebase credential file not found: {credential_path}\n"
                        f"Please ensure the file exists in the project root directory."
                    )
                
                # Load credentials and initialize Firebase
                cred = credentials.Certificate(credential_path)
                firebase_admin.initialize_app(cred)
            
            # Get Firestore client
            self.db = firestore.client()
            self.initialized = True
            return True
            
        except FileNotFoundError as e:
            print(f"Error: {e}")
            return False
        except Exception as e:
            print(f"Error connecting to Firestore: {e}")
            return False
    
    def save_user_notes(self, user_id: str, notes: Dict[str, Any]) -> bool:
        """
        Save user notes to Firestore
        
        Args:
            user_id: Unique identifier for the user
            notes: Dictionary containing notes data (e.g., {'content': str, 'timestamp': str, 'topic': str})
            
        Returns:
            bool: True if save successful, False otherwise
        """
        if not self.initialized or self.db is None:
            print("Error: Database not initialized. Call connect() first.")
            return False
        
        try:
            # Add timestamp if not present
            if 'timestamp' not in notes:
                from datetime import datetime
                notes['timestamp'] = datetime.now().isoformat()
            
            # Save to Firestore: users/{user_id}/notes/{document_id}
            notes_ref = self.db.collection('users').document(user_id).collection('notes')
            notes_ref.add(notes)
            return True
            
        except Exception as e:
            print(f"Error saving user notes: {e}")
            return False
    
    def get_flashcards(self, topic: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve flashcards from Firestore
        
        Args:
            topic: Optional topic filter to retrieve specific flashcards
            
        Returns:
            List of flashcards dictionaries
        """
        if not self.initialized or self.db is None:
            print("Error: Database not initialized. Call connect() first.")
            return []
        
        try:
            flashcards_ref = self.db.collection('flashcards')
            
            # Filter by topic if provided
            if topic:
                query = flashcards_ref.where('topic', '==', topic)
            else:
                query = flashcards_ref
            
            # Fetch documents
            docs = query.stream()
            
            # Convert to list of dictionaries
            flashcards = []
            for doc in docs:
                card_data = doc.to_dict()
                card_data['id'] = doc.id  # Include document ID
                flashcards.append(card_data)
            
            return flashcards
            
        except Exception as e:
            print(f"Error retrieving flashcards: {e}")
            return []
    
    def save_flashcard(self, topic: str, question: str, answer: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Save a flashcard to Firestore (helper method)
        
        Args:
            topic: Topic/category of the flashcard
            question: Question text
            answer: Answer text
            metadata: Optional additional metadata
            
        Returns:
            bool: True if save successful, False otherwise
        """
        if not self.initialized or self.db is None:
            print("Error: Database not initialized. Call connect() first.")
            return False
        
        try:
            flashcard_data = {
                'topic': topic,
                'question': question,
                'answer': answer,
            }
            
            if metadata:
                flashcard_data.update(metadata)
            
            from datetime import datetime
            flashcard_data['created_at'] = datetime.now().isoformat()
            
            self.db.collection('flashcards').add(flashcard_data)
            return True
            
        except Exception as e:
            print(f"Error saving flashcard: {e}")
            return False


