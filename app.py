import json
from fastapi import UploadFile, File, HTTPException
from pypdf import PdfReader
import io
import torch
import faiss
import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer


app = FastAPI(
    title="Internship RAG Recommendation API",
    description="Semantic internship recommendation using FAISS",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# Load model
# --------------------------------------------------

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2",
    device="cpu"
)

model.eval()

torch.set_num_threads(1)


# --------------------------------------------------
# Load FAISS vectors
# --------------------------------------------------

index = faiss.read_index(
    "vector_db/internships.index"
)


internship_embeddings = index.reconstruct_n(
    0,
    index.ntotal
)


# Normalize vectors

internship_embeddings = (
    internship_embeddings
    / np.linalg.norm(
        internship_embeddings,
        axis=1,
        keepdims=True
    )
)


# --------------------------------------------------
# Create cosine similarity index
# --------------------------------------------------

dimension = internship_embeddings.shape[1]

cosine_index = faiss.IndexFlatIP(
    dimension
)

cosine_index.add(
    internship_embeddings.astype("float32")
)


# --------------------------------------------------
# Load internship metadata
# --------------------------------------------------

with open(
    "vector_db/internships_metadata.json",
    "r",
    encoding="utf-8"
) as file:

    internships = json.load(file)


# --------------------------------------------------
# Request model
# --------------------------------------------------

class CandidateRequest(BaseModel):

    name: str

    education: str

    skills: list[str]

    experience: str

    projects: list[str]


# --------------------------------------------------
# Convert candidate to text
# --------------------------------------------------

def candidate_to_text(candidate):

    return f"""
    Candidate Education:
    {candidate.education}

    Candidate Skills:
    {', '.join(candidate.skills)}

    Candidate Experience:
    {candidate.experience}

    Candidate Projects:
    {', '.join(candidate.projects)}
    """


# --------------------------------------------------
# API endpoint
# --------------------------------------------------

@app.post("/recommend")
def recommend(candidate: CandidateRequest):

    candidate_text = candidate_to_text(candidate)


    # Create embedding

    embedding = model.encode(
    [candidate_text],
    convert_to_numpy=True,
    normalize_embeddings=True,
    show_progress_bar=False
)

    # Search

    top_k = min(
        5,
        len(internships)
    )

    similarities, indices = cosine_index.search(
        embedding.astype("float32"),
        top_k
    )


    results = []


    for rank, (similarity, index_id) in enumerate(
        zip(similarities[0], indices[0]),
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


        results.append(
            {
                "rank": rank,
                "internship_id": internship["id"],
                "title": internship["title"],
                "company": internship["company"],
                "description": internship["description"],
                "required_skills": internship["required_skills"],
                "preferred_skills": internship["preferred_skills"],
                "education": internship["education"],
                "experience": internship["experience"],
                "location": internship["location"],
                "work_mode": internship["work_mode"],
                "duration": internship["duration"],
                "similarity_score": round(
                    score,
                    2
                )
            }
        )


    return {
        "candidate": candidate.name,
        "total_matches": len(results),
        "matches": results
    }

# --------------------------------------------------
# Resume Upload + Recommendation
# --------------------------------------------------

@app.post("/recommend-resume")
async def recommend_resume(
    file: UploadFile = File(...)
):

    # Check PDF
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF resumes are supported."
        )

    # Read uploaded file
    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="Uploaded resume is empty."
        )

    # Extract PDF text
    reader = PdfReader(
        io.BytesIO(contents)
    )

    resume_text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            resume_text += page_text + "\n"


    if not resume_text.strip():

        raise HTTPException(
            status_code=400,
            detail="Could not extract text from resume."
        )


    # --------------------------------------------------
    # Create candidate embedding directly from resume
    # --------------------------------------------------

    candidate_embedding = model.encode(
    [resume_text],
    convert_to_numpy=True,
    normalize_embeddings=True,
    show_progress_bar=False
)


    # --------------------------------------------------
    # Search FAISS
    # --------------------------------------------------

    top_k = min(
        5,
        len(internships)
    )

    similarities, indices = cosine_index.search(
        candidate_embedding.astype("float32"),
        top_k
    )


    # --------------------------------------------------
    # Prepare results
    # --------------------------------------------------

    results = []


    for rank, (similarity, index_id) in enumerate(
        zip(similarities[0], indices[0]),
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


        results.append(
            {
                "rank": rank,
                "title": internship["title"],
                "company": internship["company"],
                "description": internship["description"],
                "required_skills": internship["required_skills"],
                "preferred_skills": internship["preferred_skills"],
                "education": internship["education"],
                "experience": internship["experience"],
                "location": internship["location"],
                "work_mode": internship["work_mode"],
                "duration": internship["duration"],
                "similarity_score": round(
                    score,
                    2
                )
            }
        )


    return {
        "message": "Resume processed successfully.",
        "matches": results
    }