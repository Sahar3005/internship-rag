import json
import io

import torch
import faiss
import numpy as np

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer


# ============================================================
# FastAPI App
# ============================================================

app = FastAPI(
    title="Internship RAG Recommendation API",
    description="Semantic internship recommendation using FAISS",
    version="1.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",

        # Add your Netlify URL here after deployment
        # "https://your-netlify-site.netlify.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# CPU Optimization
# ============================================================

torch.set_num_threads(1)


# ============================================================
# Health Check
# ============================================================

@app.get("/")
def root():
    return {
        "status": "online",
        "message": "Internship RAG API is running",
        "version": "1.0"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# ============================================================
# Lazy Load Sentence Transformer
# ============================================================

model = None


def get_model():

    global model

    if model is None:

        print("Loading SentenceTransformer model...")

        model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2",
            device="cpu"
        )

        model.eval()

        print("SentenceTransformer model loaded.")

    return model


# ============================================================
# Load FAISS Index
# ============================================================

print("Loading FAISS index...")

index = faiss.read_index(
    "vector_db/internships.index"
)

print(
    f"FAISS index loaded. Total vectors: {index.ntotal}"
)


# ============================================================
# Get Internship Embeddings
# ============================================================

internship_embeddings = index.reconstruct_n(
    0,
    index.ntotal
)


# ============================================================
# Normalize Internship Embeddings
# ============================================================

internship_embeddings = (
    internship_embeddings
    / np.linalg.norm(
        internship_embeddings,
        axis=1,
        keepdims=True
    )
)


# ============================================================
# Create Cosine Similarity Index
# ============================================================

dimension = internship_embeddings.shape[1]

cosine_index = faiss.IndexFlatIP(
    dimension
)

cosine_index.add(
    internship_embeddings.astype("float32")
)

print("Cosine similarity index ready.")


# ============================================================
# Load Internship Metadata
# ============================================================

with open(
    "vector_db/internships_metadata.json",
    "r",
    encoding="utf-8"
) as file:

    internships = json.load(file)


print(
    f"Loaded {len(internships)} internship records."
)


# ============================================================
# Candidate Request Model
# ============================================================

class CandidateRequest(BaseModel):

    name: str

    education: str

    skills: list[str]

    experience: str

    projects: list[str]


# ============================================================
# Convert Candidate Data to Text
# ============================================================

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


# ============================================================
# Generate Embedding
# ============================================================

def create_embedding(text):

    embedding = get_model().encode(
        [text],
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    return embedding


# ============================================================
# Search Internships
# ============================================================

def search_internships(embedding):

    top_k = min(
        5,
        len(internships)
    )

    similarities, indices = cosine_index.search(
        embedding.astype("float32"),
        top_k
    )

    return similarities[0], indices[0]


# ============================================================
# Prepare Internship Results
# ============================================================

def build_results(similarities, indices):

    results = []

    for rank, (similarity, index_id) in enumerate(
        zip(similarities, indices),
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

                "internship_id": internship.get(
                    "id"
                ),

                "title": internship.get(
                    "title",
                    ""
                ),

                "company": internship.get(
                    "company",
                    ""
                ),

                "description": internship.get(
                    "description",
                    ""
                ),

                "required_skills": internship.get(
                    "required_skills",
                    []
                ),

                "preferred_skills": internship.get(
                    "preferred_skills",
                    []
                ),

                "education": internship.get(
                    "education",
                    ""
                ),

                "experience": internship.get(
                    "experience",
                    ""
                ),

                "location": internship.get(
                    "location",
                    ""
                ),

                "work_mode": internship.get(
                    "work_mode",
                    ""
                ),

                "duration": internship.get(
                    "duration",
                    ""
                ),

                "similarity_score": round(
                    score,
                    2
                )
            }
        )

    return results


# ============================================================
# Candidate Recommendation API
# ============================================================

@app.post("/recommend")
def recommend(candidate: CandidateRequest):

    # Convert candidate to text

    candidate_text = candidate_to_text(
        candidate
    )

    # Create embedding

    embedding = create_embedding(
        candidate_text
    )

    # Search FAISS

    similarities, indices = search_internships(
        embedding
    )

    # Prepare results

    results = build_results(
        similarities,
        indices
    )

    return {
        "candidate": candidate.name,

        "total_matches": len(
            results
        ),

        "matches": results
    }


# ============================================================
# Resume Upload + Recommendation API
# ============================================================

@app.post("/recommend-resume")
async def recommend_resume(
    file: UploadFile = File(...)
):

    # --------------------------------------------------------
    # Check file type
    # --------------------------------------------------------

    if file.content_type != "application/pdf":

        raise HTTPException(
            status_code=400,
            detail="Only PDF resumes are supported."
        )


    # --------------------------------------------------------
    # Read uploaded file
    # --------------------------------------------------------

    contents = await file.read()


    if not contents:

        raise HTTPException(
            status_code=400,
            detail="Uploaded resume is empty."
        )


    # --------------------------------------------------------
    # Extract PDF text
    # --------------------------------------------------------

    try:

        reader = PdfReader(
            io.BytesIO(contents)
        )

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=f"Could not read PDF: {str(e)}"
        )


    resume_text = ""


    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:

            resume_text += (
                page_text + "\n"
            )


    # --------------------------------------------------------
    # Check extracted text
    # --------------------------------------------------------

    if not resume_text.strip():

        raise HTTPException(
            status_code=400,
            detail="Could not extract text from resume."
        )


    # --------------------------------------------------------
    # Create resume embedding
    # --------------------------------------------------------

    candidate_embedding = create_embedding(
        resume_text
    )


    # --------------------------------------------------------
    # Search FAISS
    # --------------------------------------------------------

    similarities, indices = search_internships(
        candidate_embedding
    )


    # --------------------------------------------------------
    # Prepare results
    # --------------------------------------------------------

    results = build_results(
        similarities,
        indices
    )


    # --------------------------------------------------------
    # Return response
    # --------------------------------------------------------

    return {
        "message": "Resume processed successfully.",

        "resume_name": file.filename,

        "matches": results
    }


# ============================================================
# Run locally
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )