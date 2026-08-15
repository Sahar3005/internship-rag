import json
import os
import pickle

import faiss
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer


# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

VECTOR_DIR = os.path.join(
    BASE_DIR,
    "vector_db"
)

METADATA_FILE = os.path.join(
    VECTOR_DIR,
    "internships_metadata.json"
)

INDEX_FILE = os.path.join(
    VECTOR_DIR,
    "internships.index"
)

VECTORIZER_FILE = os.path.join(
    VECTOR_DIR,
    "tfidf_vectorizer.pkl"
)


# =========================================================
# LOAD INTERNSHIPS
# =========================================================

with open(
    METADATA_FILE,
    "r",
    encoding="utf-8"
) as file:

    internships = json.load(file)


print(
    f"Loaded {len(internships)} internship records."
)


# =========================================================
# CREATE TEXT
# =========================================================

texts = []


for internship in internships:

    text = f"""

    Internship Title:
    {internship.get('title', '')}

    Company:
    {internship.get('company', '')}

    Description:
    {internship.get('description', '')}

    Required Skills:
    {' '.join(internship.get('required_skills', []))}

    Preferred Skills:
    {' '.join(internship.get('preferred_skills', []))}

    Education:
    {internship.get('education', '')}

    Experience:
    {internship.get('experience', '')}

    Location:
    {internship.get('location', '')}

    Work Mode:
    {internship.get('work_mode', '')}

    Duration:
    {internship.get('duration', '')}

    """

    texts.append(text)


# =========================================================
# TF-IDF
# =========================================================

vectorizer = TfidfVectorizer(
    lowercase=True,
    stop_words="english",
    max_features=3000
)


embeddings = vectorizer.fit_transform(
    texts
)


print(
    "Created TF-IDF embeddings:",
    embeddings.shape
)


# =========================================================
# SAVE VECTORIZER
# =========================================================

with open(
    VECTORIZER_FILE,
    "wb"
) as file:

    pickle.dump(
        vectorizer,
        file
    )


print(
    "Saved:",
    VECTORIZER_FILE
)


# =========================================================
# CONVERT TO FLOAT32
# =========================================================

embedding_array = embeddings.toarray().astype(
    "float32"
)


# =========================================================
# NORMALIZE
# =========================================================

faiss.normalize_L2(
    embedding_array
)


# =========================================================
# CREATE FAISS INDEX
# =========================================================

dimension = embedding_array.shape[1]


index = faiss.IndexFlatIP(
    dimension
)


index.add(
    embedding_array
)


# =========================================================
# SAVE INDEX
# =========================================================

faiss.write_index(
    index,
    INDEX_FILE
)


print(
    "Saved FAISS index:",
    INDEX_FILE
)


print(
    f"FAISS index contains {index.ntotal} records."
)

print("Done!")