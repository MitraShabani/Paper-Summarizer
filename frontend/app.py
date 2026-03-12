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
            # files = {"file": uploaded_file.getvalue()}

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
            header = s.get("header")

            # replace None header
            if header is None:
                header = "Other"

            if header not in sections:
                    sections[header] = []

            page = s.get("page")
            sections[header].append({
                "sentence": s["sentence"],
                "page": page
            })

    # Display results

        st.subheader("Summary")
        summary_text = "\n".join(
            f"{header}\n{' '.join([s['sentence'] for s in sentences])} (p.{sentences[-1]['page']})" for header, sentences in sections.items()
            )

    # instead of List comprehensions we can use regular 'for' :
    # summary_text = ""
    # for header, sents in sections.items():
    #     section_sentences = ""
    #     for s in sents:
    #         section_sentences += s["sentence"] + " "
    #     section_sentences = section_sentences.strip()  # remove trailing space
    #     last_page = sents[-1]["page"]
    #     summary_text += f"{header}\n{section_sentences} (p.{last_page})\n\n"

        st.text_area("Full Summary", value=summary_text, height=400)



