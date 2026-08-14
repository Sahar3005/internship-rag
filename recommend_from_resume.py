import json

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


# --------------------------------------------------
# 1. Load cleaned candidate
# --------------------------------------------------

with open(
    "data/cleaned_candidate.json",
    "r",
    encoding="utf-8"
) as file:
    candidate = json.load(file)


# --------------------------------------------------
# 2. Load internship metadata
# --------------------------------------------------

with open(
    "vector_db/internships_metadata.json",
    "r",
    encoding="utf-8"
) as file:
    internships = json.load(file)


# --------------------------------------------------
# 3. Load embedding model
# --------------------------------------------------

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)


# --------------------------------------------------
# 4. Load FAISS index
# --------------------------------------------------

index = faiss.read_index(
    "vector_db/internships.index"
)


# --------------------------------------------------
# 5. Convert candidate into embedding text
# --------------------------------------------------

candidate_text = f"""
Candidate Name:
{candidate["name"]}

Education:
{candidate["education"]}

Skills:
{", ".join(candidate["skills"])}

Experience:
{candidate["experience"]}

Projects:
{", ".join(candidate["projects"])}
"""


print("\n")
print("=" * 70)
print("CANDIDATE INFORMATION USED FOR MATCHING")
print("=" * 70)

print(candidate_text)


# --------------------------------------------------
# 6. Generate candidate embedding
# --------------------------------------------------

candidate_embedding = model.encode(
    [candidate_text],
    convert_to_numpy=True
)


# Normalize candidate vector

candidate_embedding = (
    candidate_embedding
    / np.linalg.norm(
        candidate_embedding,
        axis=1,
        keepdims=True
    )
)


# --------------------------------------------------
# 7. Normalize internship vectors
# --------------------------------------------------

internship_embeddings = index.reconstruct_n(
    0,
    index.ntotal
)

internship_embeddings = (
    internship_embeddings
    / np.linalg.norm(
        internship_embeddings,
        axis=1,
        keepdims=True
    )
)


# --------------------------------------------------
# 8. Create cosine similarity index
# --------------------------------------------------

dimension = internship_embeddings.shape[1]

cosine_index = faiss.IndexFlatIP(
    dimension
)

cosine_index.add(
    internship_embeddings.astype("float32")
)


# --------------------------------------------------
# 9. Search top 5 internships
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
# 10. Prepare results
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


# --------------------------------------------------
# 11. Save recommendation results
# --------------------------------------------------

output = {
    "candidate": candidate,
    "recommendations": results
}


with open(
    "vector_db/resume_recommendations.json",
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        output,
        file,
        indent=4,
        ensure_ascii=False
    )


# --------------------------------------------------
# 12. Display recommendations
# --------------------------------------------------

print("\n")
print("=" * 70)
print("INTERNSHIP RECOMMENDATIONS")
print("=" * 70)


for result in results:

    print("\n" + "-" * 60)

    print(
        f"Rank: {result['rank']}"
    )

    print(
        f"Internship: {result['title']}"
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


print("\n")
print("Recommendations saved to:")
print("vector_db/resume_recommendations.json")