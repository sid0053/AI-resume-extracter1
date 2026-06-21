# JD ↔ Resume Matcher

An NLP-powered tool that compares a resume against a job description and returns a match score, along with the keywords that align and the ones that are missing — helping users tailor their resume to a specific job posting.

## Overview

This tool extracts and cleans text from resumes (PDF/DOCX), processes both the resume and job description using spaCy's NLP pipeline, and computes a match score using a combination of exact keyword overlap and fuzzy string matching. The results are presented through an interactive Streamlit web app.

## Features

- **Multi-format resume parsing** — extracts text from PDF and DOCX resumes
- **Scanned PDF detection** — flags image-only PDFs that would need OCR, instead of silently returning empty results
- **Smart text cleaning** — normalizes bullet points, strips noise characters, and removes repeated headers/footers across pages
- **NLP-based keyword extraction** — uses spaCy to extract lemmatized nouns, proper nouns, adjectives, verbs, and multi-word noun phrases
- **Tech-token preservation** — a custom regex layer ensures terms like `C++`, `C#`, `CI/CD`, and `Node.js` aren't broken apart during cleaning/extraction
- **Hybrid scoring** — combines exact keyword overlap (Jaccard similarity) with fuzzy matching (via RapidFuzz) to catch near-matches (e.g. "developed" vs "development")
- **Interactive web UI** — upload a resume and paste a JD to instantly see a match score, matched keywords, and missing keywords
- **Downloadable reports** — export matched/missing keywords as CSV, or a full summary as a text report

## Tech Stack

- **Language:** Python
- **NLP:** spaCy (`en_core_web_sm`)
- **Fuzzy Matching:** RapidFuzz
- **Web Framework:** Streamlit
- **PDF Parsing:** pdfplumber
- **DOCX Parsing:** python-docx
- **Data Handling:** pandas

## How It Works

1. **Extraction** (`extract.py`) — Pulls raw text from an uploaded PDF or DOCX resume, detects whether a PDF is scanned (image-only), and cleans the text (normalizing bullets, removing noise characters and duplicate headers/footers).
2. **Keyword Extraction & Matching** (`jobmatcher.py`) — Processes both the resume and job description text through spaCy to extract meaningful keywords and phrases, then computes a match score using a weighted combination of exact and fuzzy matching.
3. **Interface** (`app.py`) — A Streamlit app ties it together: users upload a resume and paste a job description, and instantly see their match score, matched/missing keywords, and can download a report.

## Getting Started

### Prerequisites
- Python 3.8+

### Setup

```bash
git clone https://github.com/sid0053/AI-resume-extracter1.git
cd AI-resume-extracter1
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Run

```bash
streamlit run app.py
```

This opens the app in your browser (typically `http://localhost:8501`).

## Usage

1. Upload your resume (PDF, DOCX, or paste as plain text)
2. Paste the job description you're targeting
3. Click **Calculate Match** to see your match score, matched keywords, and gaps to address
4. Download a CSV or text report of the results

## What I Learned

- Using spaCy for real NLP tasks (lemmatization, POS tagging, noun chunking) instead of basic string matching
- Designing a hybrid scoring system that balances exact and fuzzy matching for more realistic results
- Handling messy, real-world PDF/DOCX text (headers, footers, inconsistent bullet styles, scanned documents)
- Building a usable interactive UI with Streamlit, including caching for performance

## Future Improvements

- OCR support for scanned PDFs (via `pytesseract` + `pdf2image`)
- Section-aware parsing (separating skills, experience, and education for more targeted matching)
- Support for multiple job descriptions compared against one resume at once
- Resume improvement suggestions based on missing high-priority keywords
