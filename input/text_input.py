"""
Text Input Handler
Simple text-based input for symptom descriptions
"""

from typing import Optional


class TextInputHandler:
    """
    Handles direct text input from users
    
    Example:
        handler = TextInputHandler()
        text = handler.get_input("Describe your symptoms: ")
    """
    
    def __init__(self):
        """Initialize text input handler"""
        self.last_input = None
    
    def get_input(self, prompt: str = "Enter symptoms: ") -> str:
        """
        Get text input from user
        
        Args:
            prompt: Display prompt for user
            
        Returns:
            User's text input (stripped)
        """
        try:
            text = input(prompt)
            self.last_input = text.strip()
            
            if not self.last_input:
                raise ValueError("Input cannot be empty")
            
            return self.last_input
        except KeyboardInterrupt:
            print("\nInput cancelled by user")
            raise
        except Exception as e:
            print(f"Error reading input: {e}")
            raise
    
    def validate_input(self, text: str) -> bool:
        """
        Validate text input
        
        Args:
            text: Text to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not text or len(text.strip()) == 0:
            return False
        
        if len(text) < 5:
            print("Warning: Input is very short (< 5 characters)")
            return False
        
        if len(text) > 5000:
            print("Warning: Input is very long (> 5000 characters)")
            return False
        
        return True
    
    def get_last_input(self) -> Optional[str]:
        """
        Get the last input provided
        
        Returns:
            Last input text or None
        """
        return self.last_input
    
    def clear_history(self):
        """Clear input history"""
        self.last_input = None


# Streamlit-compatible version
def streamlit_text_input(key: str = "text_input") -> str:
    """
    Streamlit wrapper for text input
    
    Args:
        key: Streamlit widget key
        
    Returns:
        User's text input
    """
    import streamlit as st
    
    text = st.text_area(
        "Describe your symptoms:",
        placeholder="Example: I have joint pain in the knees, feel cold, and have poor digestion...",
        height=120,
        key=key
    )
    
    return text.strip() if text else ""
