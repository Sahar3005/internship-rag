import json
from resume_parser import extract_resume_text


PDF_PATH = "data/Sahar_Ansari (5).pdf"


def extract_section(text, start, end=None):

    start_index = text.find(start)

    if start_index == -1:
        return ""

    start_index += len(start)

    if end:
        end_index = text.find(end, start_index)

        if end_index == -1:
            return text[start_index:].strip()

        return text[start_index:end_index].strip()

    return text[start_index:].strip()


# --------------------------------------------------
# Extract resume text
# --------------------------------------------------

text = extract_resume_text(PDF_PATH)


# --------------------------------------------------
# Name
# --------------------------------------------------

lines = [
    line.strip()
    for line in text.splitlines()
    if line.strip()
]

name = lines[0] if lines else ""


# --------------------------------------------------
# Education
# --------------------------------------------------

education = extract_section(
    text,
    "EDUCATION",
    "CERTIFICATIONS & ACHIEVEMENTS"
)


# --------------------------------------------------
# Skills
# --------------------------------------------------

skills_section = extract_section(
    text,
    "TECHNICAL SKILLS",
    "PROJECTS"
)


# --------------------------------------------------
# Projects
# --------------------------------------------------

projects_section = extract_section(
    text,
    "PROJECTS",
    "EXPERIENCE"
)


# --------------------------------------------------
# Experience
# --------------------------------------------------

experience_section = extract_section(
    text,
    "EXPERIENCE",
    "EDUCATION"
)


# --------------------------------------------------
# Convert skills into list
# --------------------------------------------------

skills = []

skill_lines = skills_section.splitlines()

for line in skill_lines:

    if ":" in line:

        _, values = line.split(
            ":",
            1
        )

        for skill in values.split(","):

            skill = skill.strip()

            if skill:
                skills.append(skill)


# Remove duplicates
skills = list(dict.fromkeys(skills))


# --------------------------------------------------
# Convert projects into list
# --------------------------------------------------

projects = []

for line in projects_section.splitlines():

    line = line.strip()

    if not line:
        continue

    # Ignore bullet descriptions
    if line.startswith("•"):
        continue

    projects.append(line)


# --------------------------------------------------
# Create structured candidate
# --------------------------------------------------

candidate = {

    "name": name,

    "education": education,

    "skills": skills,

    "experience": experience_section,

    "projects": projects
}


# --------------------------------------------------
# Save JSON
# --------------------------------------------------

with open(
    "data/extracted_candidate.json",
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
print("STRUCTURED CANDIDATE DATA")
print("=" * 60)

print(
    json.dumps(
        candidate,
        indent=4,
        ensure_ascii=False
    )
)

print("\nSaved to:")
print("data/extracted_candidate.json")