import spacy
import re
from .heading import detect_heading

# Load language model once
nlp = spacy.load("en_core_web_sm")


def fix_hyphenation(text):
    # remove hyphen + newline breaks like:
    #   "self-\nidentify" → "selfidentify"
    text = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", text)

    # also remove hyphen at end of line when block extraction puts the line in one string:
    # "self-" + "identify" → "selfidentify"
    text = re.sub(r"(\w)-\s*(\w)", r"\1\2", text)

    return text


def split_into_sentences(pages):

    sentences = []

    for page in pages:
        page_number = page["page"]
        body_text_size = page["body_text_size"]

        previousBlock_y1 = None
        current_header = None

        # collecting sentences for the current page
        page_sentences = []

        for block_text, block_font_size, x0, y0, x1, y1 in page["blocks"]:

            # header detection
            header = detect_heading(block_text, block_font_size, body_text_size, y0, previousBlock_y1)
            if header:
                current_header = header
                page_sentences.append({"sentence": block_text.strip(), "header": None})
                previousBlock_y1 = y1
                continue

            # caption and footer filtering
            if block_font_size < (body_text_size - 1.1):   # if the font size is similar
                continue
            if re.match(r"^\s*(Figure|Fig\.|Table)\s*\d+", block_text, re.IGNORECASE):    # If it starts with Figure, ...
                continue
            if re.search(r"^\s*(Algorithm|Input:|Output:|Require:|Ensure:)", block_text, re.IGNORECASE) or \
               re.match(r"^\s*\d+:", block_text) or \
               re.search(r"^\s*(end if|end function|end for|return)\b", block_text, re.IGNORECASE) or \
               "←" in block_text: # The assignment arrow is a dead giveaway
                continue

            # content processing
            cleanText = fix_hyphenation(block_text)
            doc = nlp(cleanText)
            for sent in doc.sents:
                cleanSentence = sent.text.strip()
                if cleanSentence:
                    page_sentences.append({"sentence": cleanSentence, "header": current_header})
            previousBlock_y1 = y1

        # HYPHENATION
        repaired_sentences = []
        i = 0
        while i < len(page_sentences):
            current = page_sentences[i]

            # hold the combined text if a merge occurs
            merged_text = None

            if i + 1 < len(page_sentences):
                next_sent = page_sentences[i+1]

                # 1: Hyphenation Fix
                if current["sentence"].endswith('-'):

                    # merge the words by removing the hyphen and joining immediately
                    s1_clean = current["sentence"].rstrip('-').rstrip()
                    s2 = next_sent["sentence"]

                    merged_text = f"{s1_clean}{s2}"

                    # Consolidate header context for the merged block
                    merged_header = current["header"] or next_sent["header"]

                    i += 2   # skip both current and next (because they are merged)

                # 2: Punctuation Fix
                elif current["sentence"].endswith(('.', '?', '!', ':')) and next_sent["sentence"] and next_sent["sentence"][0].isalpha() and not next_sent["sentence"][0].isupper():

                    # If a sentence ends with punctuation and the next one starts lowercase, it means spaCy missed something. Join them with a space.
                    merged_text = f"{current['sentence']} {next_sent['sentence']}"
                    merged_header = current["header"] or next_sent["header"]

                    i += 2

            # process Current or Merged Text
            if merged_text:
                # If text was merged, pass the *new* string through spaCy again because merging can creat new sentence boundaries.

                doc = nlp(merged_text)
                for new_sent in doc.sents:
                    cleanSentence = new_sent.text.strip()
                    if cleanSentence:
                         repaired_sentences.append({
                            "page": page_number,
                            "sentence": cleanSentence,
                            "header": merged_header
                        })
            else:
                # If no merge, process the sentence normally
                repaired_sentences.append({
                    "page": page_number,
                    "sentence": current["sentence"],
                    "header": current["header"]
                })
                i += 1

        # 3: Add the repaired sentences to the final output list
        sentences.extend(repaired_sentences)

    return sentences
