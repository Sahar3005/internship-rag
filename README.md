# Internship RAG Pipeline

## Overview

This project implements a Retrieval-Augmented Generation (RAG)
pipeline for recommending relevant internships based on a
candidate's resume.

The system extracts information from a candidate's resume,
generates embeddings, searches an internship vector database,
and retrieves semantically relevant internship opportunities.

## Architecture

Resume PDF
    ↓
Resume Parsing
    ↓
Candidate Data Extraction
    ↓
Data Cleaning
    ↓
Candidate Embedding
    ↓
FAISS Vector Database
    ↓
Semantic Similarity Search
    ↓
Top-K Internship Retrieval
    ↓
RAG Context
    ↓
LLM Analysis
    ↓
Final Recommendations

## Technologies Used

- Python
- PyPDF
- Sentence Transformers
- FAISS
- NumPy
- Google Gemini
- FastAPI
- JSON

## Features

- Resume PDF parsing
- Candidate information extraction
- Candidate data cleaning
- Internship embedding generation
- FAISS vector database
- Semantic internship matching
- Similarity scoring
- RAG-based internship analysis
- LLM-generated match explanations
- Resume upload API
- Multiple candidate testing

## Candidate Information

The system considers:

- Education
- Technical skills
- Experience
- Projects
- Relevant resume information

## Internship Information

Each internship contains:

- Internship title
- Company
- Description
- Required skills
- Preferred skills
- Education requirements
- Experience requirements
- Location
- Work mode
- Duration

## Vector Search

Internship descriptions are converted into embeddings using
Sentence Transformers.

The candidate resume is also converted into an embedding.

FAISS is then used to perform similarity search and retrieve
the most relevant internships.

## RAG Layer

The retrieved internships are provided to the LLM as context.

The LLM is instructed to use only the candidate and internship
information available in the retrieved context and not invent
additional internship details.

## Testing

The system was tested with multiple candidate profiles:

1. AI/ML Candidate
2. Backend/Python Candidate
3. Data Science Candidate
4. Generative AI Candidate
5. Frontend Candidate

These tests evaluate:

- Skill-based matching
- Education-based matching
- Experience-based matching
- Project-based matching
- Multiple-skill matching
- AI/ML internships
- Backend internships
- Data Science internships
- Generative AI internships
- Frontend internships

## How to Run

### Install dependencies

```bash
pip install -r requirements.txt