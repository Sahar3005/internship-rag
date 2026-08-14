import json
import re


# Load extracted candidate data
with open(
    "data/extracted_candidate.json",
    "r",
    encoding="utf-8"
) as file:
    candidate = json.load(file)


# --------------------------------------------------
# Text cleaning function
# --------------------------------------------------

def clean_text(text):

    if not isinstance(text, str):
        return text

    replacements = {
        "B.T ech": "B.Tech",
        "B.TECH": "B.Tech",
        "F ace": "Face",
        "T echnical": "Technical",
        "T ools": "Tools",
        "devel- opment": "development",
        "vi- sualization": "visualization",
        "princi- ples": "principles",
        "pat- terns": "patterns",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Fix unnecessary spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# --------------------------------------------------
# Clean education
# --------------------------------------------------

candidate["education"] = clean_text(
    candidate["education"]
)


# --------------------------------------------------
# Clean experience
# --------------------------------------------------

candidate["experience"] = clean_text(
    candidate["experience"]
)


# --------------------------------------------------
# Clean skills
# --------------------------------------------------

cleaned_skills = []

for skill in candidate["skills"]:

    skill = clean_text(skill)

    if skill and skill not in cleaned_skills:
        cleaned_skills.append(skill)


candidate["skills"] = cleaned_skills


# --------------------------------------------------
# Clean projects
# --------------------------------------------------

cleaned_projects = []

for project in candidate["projects"]:

    project = clean_text(project)

    if project and project not in cleaned_projects:
        cleaned_projects.append(project)


candidate["projects"] = cleaned_projects


# --------------------------------------------------
# Save cleaned data
# --------------------------------------------------

with open(
    "data/cleaned_candidate.json",
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        candidate,
        file,
        indent=4,
        ensure_ascii=False
    )


# --------------------------------------------------
# Display
# --------------------------------------------------

print("\n")
print("=" * 60)
print("CLEANED CANDIDATE DATA")
print("=" * 60)

print(
    json.dumps(
        candidate,
        indent=4,
        ensure_ascii=False
    )
)

print("\nSaved to:")
print("data/cleaned_candidate.json")