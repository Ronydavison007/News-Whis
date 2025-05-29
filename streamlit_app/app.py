import uuid
import streamlit as st
import requests
import os

st.title("Morning Market Brief")

query = st.text_input("Enter query", "What's our risk exposure in American tech stocks today, and highlight any earnings surprises?")
audio_file = st.file_uploader("Upload voice query (optional)", type=["wav", "mp3"])

if st.button("Submit"):
    try:
        with st.spinner("Processing..."):
            if audio_file:
                audio_path = f"uploaded_audio_{uuid.uuid4()}.wav"
                with open(audio_path, "wb") as f:
                    f.write(audio_file.read())
                with open(audio_path, "rb") as f:
                    response = requests.post("http://localhost:8000/process_query", files={"audio": f})
                os.remove(audio_path)
            else:
                response = requests.post("http://localhost:8000/process_query", json={"query": query})
            
            response.raise_for_status()
            data = response.json()
            
            st.write("Response:", data["response"])
            if data.get("audio"):
                audio_file_path = data["audio"]
                if os.path.exists(audio_file_path):
                    with open(audio_file_path, "rb") as f:
                        audio_bytes = f.read()
                    st.audio(audio_bytes, format="audio/mp3")
            st.write("Sources:", data.get("sources", "No sources available"))
    
    except requests.exceptions.RequestException as e:
        st.error(f"Error: {str(e)}")
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
