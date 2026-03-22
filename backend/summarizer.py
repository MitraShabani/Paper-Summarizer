from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

def summarize(data, compression_ratio=0.3):

    text_sentences = [s["sentence"] for s in data]
    final_summary = []

    """
    to build the unique vocabulary across all sentences and
    compute TF-IDF vectors for each sentence.
    of course, the output is a matrix.
    each column in the TF-IDF matrix corresponds to one of these words.
    each row corresponds to a sentence.
    X[i, j] = how important the j-th word in the vocabulary is in sentence i.
    rows = sentences, columns = words, values = importance of that word in the sentence.
    """
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(text_sentences)

    """ to add up all the TF-IDF values for each sentence.
        'scores' is a vector of importance.
        sum across columns; sum all word weights for each sentence.
        scores.A1 converts the matrix to a flat 1D NumPy array whichis needed for 'argsort'.
    """

    scores = X.sum(axis=1)
    ranked = np.argsort(scores.A1)[::-1] # sort the array in descending order
    top_k = max(1, int(len(text_sentences) * compression_ratio))

    # choose most important sentences
    selected  = ranked[:top_k]
    # restore original PDF order
    ordered = sorted(selected)

    for index in ordered:

        final_summary.append({
            "header": data[index]["header"],
            "sentence": text_sentences[index],
            "page": data[index]["page"]
        })

    return final_summary