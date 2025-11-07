# jobmatcher.py
import re
from typing import Set, List, Tuple, Dict

import spacy
nlp = spacy.load("en_core_web_sm")

# Optional: fuzzy matching (pip install rapidfuzz)
try:
    from rapidfuzz import process, fuzz
    HAVE_FUZZ = True
except Exception:
    HAVE_FUZZ = False

# Tech-friendly token pattern (keeps + # / . _ &)
TECH_TOKEN_RE = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9+\-#/_\.&]*")

def _tech_tokens(text: str) -> Set[str]:
    """Regex tokens to preserve things like C++, C#, Node.js, CI/CD."""
    toks = {t.lower().strip(" ._-/\\") for t in TECH_TOKEN_RE.findall(text)}
    return {t for t in toks if len(t) > 1}

def extract_keywords(text: str) -> Set[str]:
    """
    Extract keywords from text:
    - spaCy lemmas for NOUN/PROPN/ADJ/VERB (skip stopwords/punct/nums)
    - noun chunks (multi-word phrases)
    - regex tech tokens (keeps C++, C#, CI/CD, Node.js, etc.)
    """
    text = text or ""
    doc = nlp(text)

    lemmas: List[str] = []
    for tok in doc:
        if tok.is_stop or tok.is_punct or tok.like_num:
            continue
        if tok.pos_ in {"NOUN", "PROPN", "ADJ", "VERB"}:
            lem = tok.lemma_.lower().strip()
            if len(lem) > 1:
                lemmas.append(lem)

    phrases: List[str] = []
    for chunk in doc.noun_chunks:
        words = [t.lemma_.lower() for t in chunk if not (t.is_stop or t.is_punct)]
        phrase = " ".join(w for w in words if len(w) > 1)
        if phrase.count(" ") >= 1:  # keep 2+ word phrases
            phrases.append(phrase)

    tech = _tech_tokens(text)

    # Combine and lightly prune obvious noise
    out = set(lemmas) | set(phrases) | tech
    # Very small stop additions to avoid junk
    noise = {"experience", "work", "year", "years", "role", "responsibility", "project"}
    return {t for t in out if t not in noise}

def _fuzzy_matched(jd_terms: Set[str], resume_terms: Set[str], cutoff: int = 88) -> Set[str]:
    """Return JD terms that are near-matched in resume terms (token_set similarity)."""
    if not HAVE_FUZZ or not jd_terms or not resume_terms:
        return set()
    res_list = list(resume_terms)
    matched = set()
    for t in jd_terms:
        hit = process.extractOne(t, res_list, scorer=fuzz.token_set_ratio)
        if hit and hit[1] >= cutoff:
            matched.add(t)
    return matched

def calculate_match(resume_keywords: Set[str], jd_keywords: Set[str]) -> Dict:
    """
    Returns a dict with:
      - common (exact set)
      - fuzzy_common (near matches if rapidfuzz present)
      - missing (JD terms not in resume by exact match)
      - score (0..100)
    Scoring: 70% exact Jaccard, 30% fuzzy coverage bonus (capped).
    """
    if not jd_keywords:
        return {"common": set(), "fuzzy_common": set(), "missing": set(), "score": 0.0}

    exact_common = resume_keywords & jd_keywords
    missing = jd_keywords - resume_keywords

    # Fuzzy near matches
    fuzzy_common = _fuzzy_matched(jd_keywords, resume_keywords) - exact_common

    # Exact Jaccard on sets
    jaccard = len(exact_common) / len(jd_keywords)

    # Fuzzy coverage fraction relative to remaining JD terms
    fuzzy_denom = max(1, len(jd_keywords))
    fuzzy_frac = len(fuzzy_common) / fuzzy_denom

    score = 100.0 * (0.7 * jaccard + 0.3 * min(1.0, fuzzy_frac))
    return {
        "common": exact_common,
        "fuzzy_common": fuzzy_common,
        "missing": jd_keywords - (resume_keywords | fuzzy_common),
        "score": round(score, 2),
    }

def match_resume_to_job(resume_text: str, jd_text: str) -> Tuple[Set[str], Set[str], float]:
    """
    Back-compat: returns (common, missing, score)
    Uses improved extraction + scoring (exact + fuzzy). The 'common' here
    includes only exact matches to keep behavior predictable.
    """
    resume_kw = extract_keywords(resume_text)
    jd_kw = extract_keywords(jd_text)
    res = calculate_match(resume_kw, jd_kw)
    return res["common"], res["missing"], res["score"]

def main():
    # Load resume text extracted earlier
    with open("extracted_resume.txt", "r", encoding="utf-8") as f:
        resume_text = f.read()

    # Get job description from user
    jd_text = input("\nPaste Job Description:\n\n")

    resume_keywords = extract_keywords(resume_text)
    jd_keywords = extract_keywords(jd_text)
    result = calculate_match(resume_keywords, jd_keywords)

    # Nice printing with limits to avoid walls of text
    def fmt(sample: Set[str], limit=60):
        arr = sorted(sample)
        return ", ".join(arr[:limit]) + (" …" if len(arr) > limit else "")

    print("\n================ MATCH REPORT ================\n")
    print(f"✅ Resume keywords:\n{fmt(resume_keywords)}\n")
    print(f"📌 JD keywords:\n{fmt(jd_keywords)}\n")
    print(f"🎯 Exact matches:\n{fmt(result['common'])}\n")
    if HAVE_FUZZ:
        print(f"~ Close matches (fuzzy):\n{fmt(result['fuzzy_common'])}\n")
    print(f"➕ Consider adding:\n{fmt(result['missing']) if result['missing'] else 'None 🎉'}\n")
    print(f"🔢 Match Score: {result['score']}%\n")
    print("==============================================\n")

if __name__ == "__main__":
    main()
