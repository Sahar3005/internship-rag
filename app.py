import json
import io
import os
import pickle
import requests

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

# =========================================================
# AI COVER LETTER GENERATOR
# =========================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_MODEL = "gemini-2.5-flash"


@app.post("/generate-cover-letter")
async def generate_cover_letter(
    file: UploadFile = File(...),
    internship: str = ""
):

    # -----------------------------------------------------
    # Validate API key
    # -----------------------------------------------------

    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is not configured on the server."
        )

    # -----------------------------------------------------
    # Validate resume
    # -----------------------------------------------------

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF resumes are supported."
        )

    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="Uploaded resume is empty."
        )

    # -----------------------------------------------------
    # Extract resume text
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

    # Limit resume size
    resume_text = resume_text[:20000]

    # -----------------------------------------------------
    # Parse internship data
    # -----------------------------------------------------

    try:

        internship_data = json.loads(
            internship
        )

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="Invalid internship data."
        )

    # -----------------------------------------------------
    # Extract internship information
    # -----------------------------------------------------

    title = internship_data.get(
        "title",
        "Internship"
    )

    company = internship_data.get(
        "company",
        ""
    )

    description = internship_data.get(
        "description",
        ""
    )

    location = internship_data.get(
        "location",
        ""
    )

    work_mode = internship_data.get(
        "work_mode",
        ""
    )

    duration = internship_data.get(
        "duration",
        ""
    )

    required_skills = internship_data.get(
        "required_skills",
        []
    )

    preferred_skills = internship_data.get(
        "preferred_skills",
        []
    )

    # -----------------------------------------------------
    # Create AI prompt
    # -----------------------------------------------------

    prompt = f"""
You are a professional career assistant.

Write a professional, personalized cover letter
for the candidate applying to the internship below.

IMPORTANT RULES:

1. Use ONLY information that is actually present
   in the candidate's resume.
2. Do NOT invent experience, companies, achievements,
   certifications, projects or skills.
3. Match the candidate's real skills and projects
   with the internship requirements.
4. Make the letter specific to this internship.
5. Keep it professional and suitable for a fresher.
6. Do not use unnecessary headings like
   "Cover Letter".
7. Do not use markdown.
8. Do not use bullet points.
9. Keep it around 300-450 words.
10. Make it sound natural and human-written.
11. Mention relevant projects from the resume
    when they are useful for this role.
12. If the resume does not contain enough information
    for a specific claim, do not make that claim.

--------------------------------------------------
CANDIDATE RESUME
--------------------------------------------------

{resume_text}

--------------------------------------------------
INTERNSHIP DETAILS
--------------------------------------------------

Job Title:
{title}

Company:
{company}

Location:
{location}

Work Mode:
{work_mode}

Duration:
{duration}

Description:
{description}

Required Skills:
{", ".join(required_skills)}

Preferred Skills:
{", ".join(preferred_skills)}

--------------------------------------------------

Write the final cover letter now.

Start directly with:

Dear Hiring Manager,

End with:

Sincerely,
[Candidate Name]
"""

    # -----------------------------------------------------
    # Gemini API request
    # -----------------------------------------------------

    url = (
        "https://generativelanguage.googleapis.com/"
        "v1beta/models/"
        f"{GEMINI_MODEL}:generateContent"
    )

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
    }

    payload = {

        "contents": [

            {
                "role": "user",

                "parts": [

                    {
                        "text": prompt
                    }

                ]
            }

        ],

        "generationConfig": {

            "temperature": 0.7,

            "maxOutputTokens": 1000

        }

    }

    # -----------------------------------------------------
    # Call Gemini
    # -----------------------------------------------------

    try:

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=60
        )

    except requests.exceptions.Timeout:

        raise HTTPException(
            status_code=504,
            detail="AI generation timed out. Please try again."
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"AI service connection failed: {str(e)}"
        )

    # -----------------------------------------------------
    # Handle Gemini error
    # -----------------------------------------------------

    if response.status_code != 200:

        try:

            error_data = response.json()

            error_message = (
                error_data
                .get("error", {})
                .get(
                    "message",
                    "Gemini API request failed."
                )
            )

        except Exception:

            error_message = response.text

        raise HTTPException(
            status_code=500,
            detail=error_message
        )

    # -----------------------------------------------------
    # Read Gemini response
    # -----------------------------------------------------

    try:

        result = response.json()

        candidates = result.get(
            "candidates",
            []
        )

        if not candidates:

            raise Exception(
                "No AI response generated."
            )

        parts = (
            candidates[0]
            .get("content", {})
            .get("parts", [])
        )

        cover_letter = ""

        for part in parts:

            if "text" in part:

                cover_letter += (
                    part["text"]
                )

        cover_letter = cover_letter.strip()

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Invalid AI response: {str(e)}"
        )

    # -----------------------------------------------------
    # Final validation
    # -----------------------------------------------------

    if not cover_letter:

        raise HTTPException(
            status_code=500,
            detail="AI returned an empty cover letter."
        )

    # -----------------------------------------------------
    # Response
    # -----------------------------------------------------

    return {

        "message":
            "Cover letter generated successfully.",

        "internship": {

            "title": title,

            "company": company

        },

        "cover_letter":
            cover_letter

    }