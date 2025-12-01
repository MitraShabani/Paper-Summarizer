from fastapi import FastAPI, UploadFile, File
from .parsing import extract_blocks
import os
from .sentences import split_into_sentences

app = FastAPI()

@app.post("/parse")
async  def parse_paper(file: UploadFile = File(...)):

    # FastAPI gives the PDF in memory, not as a real file.But our PDF extractor (PyMuPDF) only works with real files on disk.

    file_path = f"temp_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    pages = extract_blocks(file_path)

    # convert pages to sentences
    sentences = split_into_sentences(pages)

    os.remove(file_path)

    return {"sentences": sentences}

@app.post("/summarize")
async  def summarize_paper():
    return {"message": "summarize endpoint reached"}

