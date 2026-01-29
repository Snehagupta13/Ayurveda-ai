"""
Streamlit UI for Ayurveda AI System
Main interface for user interactions
"""

import streamlit as st
from api import AyurvedaAPI

def main():
    st.set_page_config(page_title="Ayurveda AI", layout="wide")
    
    st.title("🌿 Ayurveda AI Assistant")
    st.write("Your personalized Ayurvedic health guidance powered by AI")
    
    # Initialize API
    api = AyurvedaAPI()
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select a feature:", 
                           ["Symptom Analysis", "Dosha Assessment", "Guidance", "Safety Check"])
    
    if page == "Symptom Analysis":
        st.header("Symptom Analysis")
        # Add symptom analysis UI components
        
    elif page == "Dosha Assessment":
        st.header("Dosha Assessment")
        # Add dosha assessment UI components
        
    elif page == "Guidance":
        st.header("Personalized Guidance")
        # Add guidance UI components
        
    elif page == "Safety Check":
        st.header("Safety Verification")
        # Add safety check UI components

if __name__ == "__main__":
    main()
