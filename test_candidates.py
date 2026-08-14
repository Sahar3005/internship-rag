import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


# Load internship data
with open(
    "vector_db/internships_metadata.json",
    "r",
    encoding="utf-8"
) as file:
    internships = json.load(file)


# Load model
model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)


# Load FAISS embeddings
embeddings = faiss.read_index(
    "vector_db/internships.index"
).reconstruct_n(
    0,
    len(internships)
)


# Normalize
embeddings = embeddings / np.linalg.norm(
    embeddings,
    axis=1,
    keepdims=True
)


# Create cosine similarity index
index = faiss.IndexFlatIP(
    embeddings.shape[1]
)

index.add(
    embeddings.astype("float32")
)


# --------------------------------------------------
# TEST CANDIDATES
# --------------------------------------------------

candidates = [

    {
        "name": "AI ML Candidate",
        "education": "B.Tech Computer Science",
        "skills": [
            "Python",
            "Machine Learning",
            "Scikit-learn",
            "NumPy",
            "Pandas",
            "OpenCV"
        ],
        "experience": "ML project experience",
        "projects": [
            "Breast Cancer Detection",
            "Crop Disease Detection"
        ]
    },

    {
        "name": "Backend Python Candidate",
        "education": "B.Tech Computer Science",
        "skills": [
            "Python",
            "Django",
            "Flask",
            "REST API",
            "SQL",
            "MySQL"
        ],
        "experience": "Python development internship",
        "projects": [
            "REST API",
            "Backend applications"
        ]
    },

    {
        "name": "Data Science Candidate",
        "education": "B.Tech Computer Science",
        "skills": [
            "Python",
            "Pandas",
            "NumPy",
            "SQL",
            "Matplotlib",
            "Seaborn",
            "Power BI"
        ],
        "experience": "Data analysis experience",
        "projects": [
            "Exploratory Data Analysis",
            "Data Visualization"
        ]
    },

    {
        "name": "Generative AI Candidate",
        "education": "B.Tech Computer Science",
        "skills": [
            "Python",
            "Generative AI",
            "LLM",
            "LangChain",
            "Vector Database",
            "RAG"
        ],
        "experience": "AI development experience",
        "projects": [
            "RAG Pipeline",
            "LLM Application"
        ]
    },

    {
        "name": "Frontend Candidate",
        "education": "B.Tech Computer Science",
        "skills": [
            "HTML",
            "CSS",
            "JavaScript",
            "React.js"
        ],
        "experience": "Frontend development experience",
        "projects": [
            "React Web Application",
            "Todo Application"
        ]
    }
]


# --------------------------------------------------
# TEST EACH CANDIDATE
# --------------------------------------------------

for candidate in candidates:

    candidate_text = f"""
    Education:
    {candidate["education"]}

    Skills:
    {", ".join(candidate["skills"])}

    Experience:
    {candidate["experience"]}

    Projects:
    {", ".join(candidate["projects"])}
    """


    vector = model.encode(
        [candidate_text],
        convert_to_numpy=True
    )


    vector = vector / np.linalg.norm(
        vector,
        axis=1,
        keepdims=True
    )


    scores, indices = index.search(
        vector.astype("float32"),
        min(3, len(internships))
    )


    print("\n")
    print("=" * 70)
    print(candidate["name"])
    print("=" * 70)


    for rank, (score, idx) in enumerate(
        zip(scores[0], indices[0]),
        start=1
    ):

        internship = internships[idx]

        print(
            f"{rank}. {internship['title']} "
            f"- {internship['company']}"
        )

        print(
            f"   Similarity: {score * 100:.2f}%"
        )