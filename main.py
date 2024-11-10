# app.py
import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from spotify_operations import SpotifyOperations


load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

class MusicAssistant:
    def __init__(self):
        self.spotify_ops = SpotifyOperations()

    def get_chat_response(self, user_input, chat_history):
        """Get response from OpenAI based on user input and chat history"""
        system_prompt = """You are a knowledgeable music assistant that helps users discover and learn about music. 
        You can search for songs, provide information about artists, and make recommendations. 
        Keep responses concise and music-focused. If you need to search for specific music information, 
        indicate it with ACTION_REQUIRED: followed by the specific search type (SEARCH_TRACK, SEARCH_ARTIST, etc)."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            *chat_history,
            {"role": "user", "content": user_input}
        ]
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=150
        )
        
        return response.choices[0].message.content

    def handle_user_input(self, user_input):
        """Process user input and generate appropriate response"""
   
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
    
        ai_response = self.get_chat_response(user_input, st.session_state.chat_history)
        
    
        if "ACTION_REQUIRED:" in ai_response:
            action_type = ai_response.split("ACTION_REQUIRED:")[1].split()[0]
            query = " ".join(ai_response.split("ACTION_REQUIRED:")[1].split()[1:])
            
           
            if action_type == "SEARCH_TRACK":
                results = self.spotify_ops.search_spotify(query, 'track')
                if results:
                    formatted_results = self.spotify_ops.process_spotify_results(results, 'track')
                    self.spotify_ops.display_track_results(formatted_results)

            
            elif action_type == "SEARCH_ARTIST":
                results = self.spotify_ops.search_spotify(query, 'artist')
                if results:
                    formatted_results = self.spotify_ops.process_spotify_results(results, 'artist')
                    st.write(formatted_results)
        
  
        st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
        

        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])

def main():
    st.title("🎵 Music Assistant")
    st.write("Chat with me about music! Ask about songs, artists, or get recommendations.")
    
   
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    

    assistant = MusicAssistant()
    

    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        assistant.handle_user_input(user_input)

if __name__ == "__main__":
    main()