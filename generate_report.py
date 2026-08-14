import json


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
# 2. Load matching results
# --------------------------------------------------

with open(
    "vector_db/matching_results.json",
    "r",
    encoding="utf-8"
) as file:
    matches = json.load(file)


candidate_skills = {
    skill.lower()
    for skill in candidate["skills"]
}


# --------------------------------------------------
# 3. Analyze each internship
# --------------------------------------------------

final_results = []


for internship in matches:

    required_skills = {
        skill.lower()
        for skill in internship["required_skills"]
    }

    preferred_skills = {
        skill.lower()
        for skill in internship["preferred_skills"]
    }

    matched_required = sorted(
        candidate_skills.intersection(required_skills)
    )

    matched_preferred = sorted(
        candidate_skills.intersection(preferred_skills)
    )

    missing_required = sorted(
        required_skills.difference(candidate_skills)
    )

    final_results.append(
        {
            "rank": internship["rank"],
            "title": internship["title"],
            "company": internship["company"],
            "similarity_score": internship["similarity_score"],
            "matched_required_skills": matched_required,
            "matched_preferred_skills": matched_preferred,
            "missing_required_skills": missing_required,
            "location": internship["location"],
            "work_mode": internship["work_mode"],
            "duration": internship["duration"]
        }
    )


# --------------------------------------------------
# 4. Save final report
# --------------------------------------------------

report = {
    "candidate": candidate["name"],
    "results": final_results
}


with open(
    "vector_db/final_report.json",
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        report,
        file,
        indent=4
    )


# --------------------------------------------------
# 5. Display report
# --------------------------------------------------

print("\n")
print("=" * 70)
print("FINAL RAG MATCHING REPORT")
print("=" * 70)

print(
    f"\nCandidate: {candidate['name']}"
)


for result in final_results:

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
        f"Similarity: "
        f"{result['similarity_score']}%"
    )

    print(
        f"Matched Required Skills: "
        f"{', '.join(result['matched_required_skills']) or 'None'}"
    )

    print(
        f"Matched Preferred Skills: "
        f"{', '.join(result['matched_preferred_skills']) or 'None'}"
    )

    print(
        f"Missing Required Skills: "
        f"{', '.join(result['missing_required_skills']) or 'None'}"
    )

    print(
        f"Location: {result['location']}"
    )

    print(
        f"Work Mode: {result['work_mode']}"
    )

    print(
        f"Duration: {result['duration']}"
    )


print("\n")
print("Final report saved to:")
print("vector_db/final_report.json")