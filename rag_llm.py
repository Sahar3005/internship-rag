import os
import json

from google import genai


# --------------------------------------------------
# Load candidate
# --------------------------------------------------

with open(
    "data/cleaned_candidate.json",
    "r",
    encoding="utf-8"
) as file:
    candidate = json.load(file)


# --------------------------------------------------
# Load retrieved internships
# --------------------------------------------------

with open(
    "vector_db/resume_recommendations.json",
    "r",
    encoding="utf-8"
) as file:
    recommendations = json.load(file)


# --------------------------------------------------
# Get Gemini API key
# --------------------------------------------------

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY environment variable is not set."
    )


# --------------------------------------------------
# Gemini Client
# --------------------------------------------------

client = genai.Client(
    api_key=api_key
)


# --------------------------------------------------
# Build internship context
# --------------------------------------------------

context = ""

for internship in recommendations["recommendations"]:

    context += f"""
Internship Title:
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

Analyze the candidate using ONLY the candidate data
and retrieved internship data provided below.

STRICT RULES:

1. Do not invent internship details.
2. Do not invent company names.
3. Do not invent skills.
4. Do not invent salary information.
5. Do not invent locations.
6. Recommend only internships present in the retrieved data.
7. Explain the match using the candidate's actual skills,
   education, projects, and experience.
8. Mention skill gaps when relevant.
9. Keep the answer factual and concise.

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


Return the result in this format:

1. Internship Name - Company
   Match Score:
   Why it matches:
   Matching skills:
   Relevant project/experience:
   Skill gaps:

2. Internship Name - Company
   Match Score:
   Why it matches:
   Matching skills:
   Relevant project/experience:
   Skill gaps:
"""


# --------------------------------------------------
# Generate LLM response
# --------------------------------------------------

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=prompt
)


# --------------------------------------------------
# Display result
# --------------------------------------------------

print("\n")
print("=" * 70)
print("AI INTERNSHIP RECOMMENDATION")
print("=" * 70)

print(response.text)