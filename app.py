import json
import io
import os

import numpy as np
import faiss

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pypdf import PdfReader

from sklearn.feature_extraction.text import TfidfVectorizer


# =========================================================
# FASTAPI
# =========================================================

app = FastAPI(
    title="Internship RAG Recommendation API",
    description="Internship recommendation using TF-IDF + FAISS",
    version="2.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# FILE PATHS
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
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
# LOAD INTERNSHIP METADATA
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
# LOAD FAISS INDEX
# =========================================================

if not os.path.exists(INDEX_FILE):

    raise RuntimeError(
        "FAISS index not found. "
        "Run create_embeddings.py first."
    )


index = faiss.read_index(
    INDEX_FILE
)


# =========================================================
# LOAD TF-IDF VECTORIZER
# =========================================================

import pickle


if not os.path.exists(VECTORIZER_FILE):

    raise RuntimeError(
        "TF-IDF vectorizer not found. "
        "Run create_embeddings.py first."
    )


with open(
    VECTORIZER_FILE,
    "rb"
) as file:

    vectorizer = pickle.load(file)


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/")
def home():

    return {
        "status": "online",
        "message": "Internship RAG API is running",
        "version": "2.0"
    }


# =========================================================
# REQUEST MODEL
# =========================================================

class CandidateRequest(BaseModel):

    name: str

    education: str

    skills: list[str]

    experience: str

    projects: list[str]


# =========================================================
# CANDIDATE → TEXT
# =========================================================

def candidate_to_text(candidate):

    return f"""
    Education:
    {candidate.education}

    Skills:
    {' '.join(candidate.skills)}

    Experience:
    {candidate.experience}

    Projects:
    {' '.join(candidate.projects)}
    """


# =========================================================
# SEARCH INTERNSHIPS
# =========================================================

def search_internships(text, top_k=5):

    query_vector = vectorizer.transform(
        [text]
    )

    query_array = query_vector.toarray().astype(
        "float32"
    )

    similarities, indices = index.search(
        query_array,
        min(top_k, len(internships))
    )

    results = []

    for rank, (similarity, index_id) in enumerate(
        zip(
            similarities[0],
            indices[0]
        ),
        start=1
    ):

        internship = internships[index_id]

        score = max(
            0,
            min(
                100,
                float(similarity) * 100
            )
        )

        results.append({

            "rank": rank,

            "internship_id":
                internship.get("id"),

            "title":
                internship.get("title"),

            "company":
                internship.get("company"),

            "description":
                internship.get("description"),

            "required_skills":
                internship.get(
                    "required_skills",
                    []
                ),

            "preferred_skills":
                internship.get(
                    "preferred_skills",
                    []
                ),

            "education":
                internship.get("education"),

            "experience":
                internship.get("experience"),

            "location":
                internship.get("location"),

            "work_mode":
                internship.get("work_mode"),

            "duration":
                internship.get("duration"),

            "similarity_score":
                round(score, 2)

        })

    return results


# =========================================================
# JSON RECOMMENDATION API
# =========================================================

@app.post("/recommend")
def recommend(
    candidate: CandidateRequest
):

    candidate_text = candidate_to_text(
        candidate
    )

    results = search_internships(
        candidate_text
    )

    return {

        "candidate":
            candidate.name,

        "total_matches":
            len(results),

        "matches":
            results
    }


# =========================================================
# RESUME RECOMMENDATION API
# =========================================================

@app.post("/recommend-resume")
async def recommend_resume(
    file: UploadFile = File(...)
):

    # -----------------------------------------------------
    # Validate PDF
    # -----------------------------------------------------

    if file.content_type != "application/pdf":

        raise HTTPException(
            status_code=400,
            detail="Only PDF resumes are supported."
        )


    # -----------------------------------------------------
    # Read file
    # -----------------------------------------------------

    contents = await file.read()


    if not contents:

        raise HTTPException(
            status_code=400,
            detail="Uploaded resume is empty."
        )


    # -----------------------------------------------------
    # Extract PDF text
    # -----------------------------------------------------

    try:

        reader = PdfReader(
            io.BytesIO(contents)
        )

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="Invalid PDF file."
        )


    resume_text = ""


    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:

            resume_text += (
                page_text + "\n"
            )


    if not resume_text.strip():

        raise HTTPException(
            status_code=400,
            detail="Could not extract text from resume."
        )


    # -----------------------------------------------------
    # Limit text size
    # Helps keep memory usage low
    # -----------------------------------------------------

    resume_text = resume_text[:20000]


    # -----------------------------------------------------
    # Recommendation
    # -----------------------------------------------------

    results = search_internships(
        resume_text,
        top_k=5
    )


    # -----------------------------------------------------
    # Response
    # -----------------------------------------------------

    return {

        "message":
            "Resume processed successfully.",

        "resume_name":
            file.filename,

        "matches":
            results
    }