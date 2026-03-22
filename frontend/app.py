# UI LAYER
import streamlit as st
import requests

# Input paragraph & Layout
st.title("Summarizer App")
st.write("Enter your paragraph below to summarize:")

userInput = st.text_area( "Paste your text here", height=220, placeholder=". . . . . . ." )
uploaded_file = st.file_uploader("Upload a paper", type="pdf")

summary  = []

if st.button("Submit"):
    try:
        with st.spinner("Processing…"):
            response = None

        # Send PDF to FastAPI
        if uploaded_file is not None:

            response = requests.post(
                "http://127.0.0.1:8000/parse",
                files={"file": uploaded_file}
            )
            summary  = response.json().get("data", [])

        # Send text to FastAPI
        elif userInput.strip():

            response = requests.post(
                "http://127.0.0.1:8000/Summarize_text",
                json={"text": userInput}
            )
            summary = response.json().get("data", [])
        else:
            st.warning("Please upload a PDF or enter text")

    except Exception as e:
        st.error(f"Error: {e}")

    # group sentences by header
    sections = {}
    if summary:

        for s in summary:
            header = s["header"]

            # replace None header
            if header is None:
                header = ""

            if header not in sections:
                sections[header] = []

            sections[header].append({
                "sentence": s["sentence"],
                "page": s["page"]
            })


        summary_text = ""
        for header, sec in sections.items():

            sentences = (s["sentence"] for s in sec)
            pages = sec[-1]["page"]

            summary_text += f"\n{header}\n{[s for s in sentences]} (p.{pages})\n"

        st.text_area("Full Summary", value=summary_text, height=400)



