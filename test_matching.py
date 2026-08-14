import json

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


# --------------------------------------------------
# 1. Load test candidates
# --------------------------------------------------

with open(
    "data/test_candidates.json",
    "r",
    encoding="utf-8"
) as file:
    candidates = json.load(file)


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
# 4. Load internship vectors
# --------------------------------------------------

index = faiss.read_index(
    "vector_db/internships.index"
)

internship_embeddings = index.reconstruct_n(
    0,
    index.ntotal
)


# Normalize internship embeddings
internship_embeddings = (
    internship_embeddings
    / np.linalg.norm(
        internship_embeddings,
        axis=1,
        keepdims=True
    )
)


# --------------------------------------------------
# 5. Create cosine similarity index
# --------------------------------------------------

dimension = internship_embeddings.shape[1]

cosine_index = faiss.IndexFlatIP(
    dimension
)

cosine_index.add(
    internship_embeddings.astype("float32")
)


# --------------------------------------------------
# 6. Convert candidate to text
# --------------------------------------------------

def candidate_to_text(candidate):

    skills = ", ".join(candidate["skills"])

    return f"""
    Candidate Education:
    {candidate['education']}

    Candidate Skills:
    {skills}

    Candidate Experience:
    {candidate['experience']}

    Candidate Projects:
    {', '.join(candidate['projects'])}
    """


# --------------------------------------------------
# 7. Test every candidate
# --------------------------------------------------

all_results = []


for candidate in candidates:

    candidate_text = candidate_to_text(candidate)

    # Create candidate embedding
    candidate_embedding = model.encode(
        [candidate_text],
        convert_to_numpy=True
    )

    # Normalize
    candidate_embedding = (
        candidate_embedding
        / np.linalg.norm(
            candidate_embedding,
            axis=1,
            keepdims=True
        )
    )

    # Search top 3
    top_k = min(3, len(internships))

    similarities, indices = cosine_index.search(
        candidate_embedding.astype("float32"),
        top_k
    )

    candidate_results = []

    for rank, (similarity, index_id) in enumerate(
        zip(similarities[0], indices[0]),
        start=1
    ):

        internship = internships[index_id]

        score = max(
            0,
            min(100, float(similarity) * 100)
        )

        candidate_results.append(
            {
                "rank": rank,
                "internship": internship["title"],
                "company": internship["company"],
                "similarity_score": round(score, 2)
            }
        )

    all_results.append(
        {
            "candidate_id": candidate["id"],
            "candidate_name": candidate["name"],
            "results": candidate_results
        }
    )


# --------------------------------------------------
# 8. Save evaluation results
# --------------------------------------------------

with open(
    "vector_db/testing_results.json",
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        all_results,
        file,
        indent=4
    )


# --------------------------------------------------
# 9. Display results
# --------------------------------------------------

print("\n")
print("=" * 70)
print("INTERNSHIP RAG TESTING RESULTS")
print("=" * 70)


for result in all_results:

    print(
        f"\nCandidate: "
        f"{result['candidate_name']}"
    )

    for item in result["results"]:

        print(
            f"  {item['rank']}. "
            f"{item['internship']} "
            f"({item['company']}) "
            f"→ {item['similarity_score']}%"
        )


print("\n")
print("Testing completed successfully.")
print("Results saved to:")
print("vector_db/testing_results.json")