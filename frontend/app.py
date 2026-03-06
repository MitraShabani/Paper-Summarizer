# UI LAYER
import streamlit as st
import requests

# Input paragraph & Layout
st.title("Summarizer App")
st.write("Enter your paragraph below to summarize:")

userInput = st.text_area( "Paste your text here", height=220, placeholder=". . . . . . ." )
uploaded_file = st.file_uploader("Upload a paper", type="pdf")

result_sentences  = []

if st.button("Submit"):
    try:
        with st.spinner("Processing…"):
            response = None

        # Send PDF to FastAPI
        if uploaded_file is not None:
            # files = {"file": uploaded_file.getvalue()}

            response = requests.post(
                "http://127.0.0.1:8000/parse",
                files={"file": uploaded_file}
            )
            result_sentences  = response.json().get("sentences", [])

        # Send text to FastAPI
        elif userInput.strip():

            response = requests.post(
                "http://127.0.0.1:8000/Summarize_text",
                json={"text": userInput}
            )
            result_sentences = response.json().get("sentences", [])
        else:
            st.warning("Please upload a PDF or enter text")

    except Exception as e:
        st.error(f"Error: {e}")

    # Display results
    if result_sentences:
        st.subheader("Summary")
        for r in result_sentences:
            st.write(r)




