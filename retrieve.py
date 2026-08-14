import json

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


# --------------------------------------------------
# 1. Load candidate
# --------------------------------------------------

with open(
    "data/candidate.json",
    "r",
    encoding="utf-8"
) as file:
    candidate = json.load(file)


# --------------------------------------------------
# 2. Load embedding model
# --------------------------------------------------

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)


# --------------------------------------------------
# 3. Convert candidate into text
# --------------------------------------------------

def candidate_to_text(candidate):

    education = candidate["education"]

    skills = ", ".join(candidate["skills"])

    experience = "\n".join(
        f"{item['role']}: {item['description']}"
        for item in candidate["experience"]
    )

    projects = "\n".join(
        f"{item['name']}: {item['description']}"
        for item in candidate["projects"]
    )

    return f"""
    Candidate Education:
    Degree: {education['degree']}
    Branch: {education['branch']}
    Specialization: {education['specialization']}
    Graduation Year: {education['graduation_year']}

    Candidate Skills:
    {skills}

    Candidate Experience:
    {experience}

    Candidate Projects:
    {projects}
    """


candidate_text = candidate_to_text(candidate)


# --------------------------------------------------
# 4. Create candidate embedding
# --------------------------------------------------

candidate_embedding = model.encode(
    [candidate_text],
    convert_to_numpy=True
)

# Normalize candidate embedding
candidate_embedding = candidate_embedding / np.linalg.norm(
    candidate_embedding,
    axis=1,
    keepdims=True
)


# --------------------------------------------------
# 5. Load internship FAISS database
# --------------------------------------------------

index = faiss.read_index(
    "vector_db/internships.index"
)


# --------------------------------------------------
# IMPORTANT:
# Internship embeddings must also be normalized
# --------------------------------------------------

# Reconstruct stored vectors from FAISS
internship_embeddings = index.reconstruct_n(
    0,
    index.ntotal
)

internship_embeddings = internship_embeddings / np.linalg.norm(
    internship_embeddings,
    axis=1,
    keepdims=True
)


# --------------------------------------------------
# 6. Create cosine-similarity FAISS index
# --------------------------------------------------

dimension = internship_embeddings.shape[1]

cosine_index = faiss.IndexFlatIP(dimension)

cosine_index.add(
    internship_embeddings.astype("float32")
)


# --------------------------------------------------
# 7. Load internship metadata
# --------------------------------------------------

with open(
    "vector_db/internships_metadata.json",
    "r",
    encoding="utf-8"
) as file:
    internships = json.load(file)


# --------------------------------------------------
# 8. Search
# --------------------------------------------------

top_k = min(5, len(internships))

similarities, indices = cosine_index.search(
    candidate_embedding.astype("float32"),
    top_k
)


# --------------------------------------------------
# 9. Prepare matching results
# --------------------------------------------------

matching_results = []

for rank, (similarity, index_id) in enumerate(
    zip(similarities[0], indices[0]),
    start=1
):

    internship = internships[index_id]

    score = max(
        0,
        min(100, float(similarity) * 100)
    )

    result = {
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
        "similarity_score": round(score, 2)
    }

    matching_results.append(result)


# --------------------------------------------------
# 10. Save results
# --------------------------------------------------

with open(
    "vector_db/matching_results.json",
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        matching_results,
        file,
        indent=4
    )


# --------------------------------------------------
# 11. Display results
# --------------------------------------------------

print("\n")
print("=" * 65)
print("TOP MATCHING INTERNSHIPS")
print("=" * 65)

for result in matching_results:

    print(
        f"\nRank {result['rank']}: "
        f"{result['title']}"
    )

    print(
        f"Company: {result['company']}"
    )

    print(
        f"Similarity Score: "
        f"{result['similarity_score']}%"
    )

    print(
        f"Location: "
        f"{result['location']}"
    )

    print(
        f"Work Mode: "
        f"{result['work_mode']}"
    )

    print(
        f"Duration: "
        f"{result['duration']}"
    )