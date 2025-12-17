from fastapi import FastAPI, UploadFile, File
from .parsing import extract_blocks
import os
import uuid
from .sentences import split_into_sentences

app = FastAPI()

@app.get("/")
def read_root():
    # When the browser hits http://127.0.0.1:8000/, it will receive this dictionary.
    return {"status": "Server running successfully!"}

# app = FastAPI()

@app.post("/parse")
async  def parse_paper(file: UploadFile = File(...)):

    # FastAPI gives the PDF in memory, not as a real file.But our PDF extractor (PyMuPDF) only works with real files on disk.

    # Generate a unique, safe filename (e.g., temp_12345.pdf)
    # This avoids issues with spaces or special characters in original filenames
    unique_id = uuid.uuid4().hex
    file_path = f"temp_{unique_id}.pdf"

    try:
        content = await file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(content)

        # Verify the file actually exists on disk before proceeding
        if not os.path.exists(file_path):
            return {"error": "File failed to save to disk."}

        # 1. Extract the data
        # Note: We use the unpacking doc, pages_data
        doc, pages_data = extract_blocks(file_path)

        # 2. Process the sentences
        sentences = split_into_sentences(pages_data)

        # 3. Clean up and return
        return {"sentences": sentences}

    except Exception as e:
        print(f"CRITICAL API ERROR: {e}")
        return {"error": str(e)}

    finally:
        # Crucial: Close the doc so Windows releases the file lock
        if 'doc' in locals() and doc:
            doc.close()

        # Try to remove the file, but don't crash if it fails
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as cleanup_error:
                print(f"Cleanup warning: {cleanup_error}")

@app.post("/summarize")
async  def summarize_paper():
    return {"message": "summarize endpoint reached"}

