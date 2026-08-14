import json
import os

import faiss
from sentence_transformers import SentenceTransformer


# 1. Load internship dataset
with open("data/internships.json", "r", encoding="utf-8") as file:
    internships = json.load(file)


# 2. Load embedding model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


# 3. Convert internship information into text
def internship_to_text(internship):

    return f"""
    Internship Title: {internship['title']}
    Company: {internship['company']}

    Description:
    {internship['description']}

    Required Skills:
    {', '.join(internship['required_skills'])}

    Preferred Skills:
    {', '.join(internship['preferred_skills'])}

    Education:
    {internship['education']}

    Experience:
    {internship['experience']}

    Location:
    {internship['location']}

    Work Mode:
    {internship['work_mode']}

    Duration:
    {internship['duration']}
    """


# 4. Create documents
documents = [
    internship_to_text(internship)
    for internship in internships
]


# 5. Generate embeddings
embeddings = model.encode(
    documents,
    convert_to_numpy=True
)


# 6. Create FAISS index
dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)

index.add(embeddings)


# 7. Create vector_db folder if it doesn't exist
os.makedirs("vector_db", exist_ok=True)


# 8. Save FAISS index
faiss.write_index(
    index,
    "vector_db/internships.index"
)


# 9. Save internship metadata
with open(
    "vector_db/internships_metadata.json",
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        internships,
        file,
        indent=4
    )


print("Internship embeddings created successfully.")
print("Total internships:", len(internships))
print("Embedding dimension:", dimension)