import json


# Load candidate and retrieved internships
with open(
    "data/cleaned_candidate.json",
    "r",
    encoding="utf-8"
) as file:
    candidate = json.load(file)


with open(
    "vector_db/resume_recommendations.json",
    "r",
    encoding="utf-8"
) as file:
    recommendations = json.load(file)


# --------------------------------------------------
# Create RAG context
# --------------------------------------------------

context = ""

for internship in recommendations["recommendations"]:

    context += f"""
Internship:
{internship["title"]}

Company:
{internship["company"]}

Description:
{internship["description"]}

Required Skills:
{internship["required_skills"]}

Preferred Skills:
{internship["preferred_skills"]}

Education:
{internship["education"]}

Experience:
{internship["experience"]}

Location:
{internship["location"]}

Work Mode:
{internship["work_mode"]}

Duration:
{internship["duration"]}

Similarity Score:
{internship["similarity_score"]}%

--------------------------------------------------
"""


# --------------------------------------------------
# RAG Prompt
# --------------------------------------------------

prompt = f"""
You are an internship recommendation assistant.

Your task is to analyze the candidate against the retrieved
internship opportunities.

IMPORTANT RULES:

1. Use ONLY the candidate information provided below.
2. Use ONLY the internship information provided below.
3. Do not invent companies, skills, requirements,
   locations, salaries, or internship details.
4. Do not recommend internships that are not present
   in the retrieved context.
5. Explain why each internship matches the candidate.
6. Mention matching skills and relevant projects or experience.
7. If there is a skill gap, clearly mention it.
8. Keep the response concise and factual.

CANDIDATE:

Name:
{candidate["name"]}

Education:
{candidate["education"]}

Skills:
{candidate["skills"]}

Experience:
{candidate["experience"]}

Projects:
{candidate["projects"]}


RETRIEVED INTERNSHIPS:

{context}


Generate a recommendation summary for the candidate.
"""


print("\n")
print("=" * 70)
print("RAG PROMPT")
print("=" * 70)

print(prompt)