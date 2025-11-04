import spacy

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

def extract_keywords(text):
    doc = nlp(text.lower())
    # Use lemma to normalize words (developing → develop, machine-learning → machine learning)
    keywords = [token.lemma_ for token in doc if token.is_alpha and not token.is_stop]
    return set(keywords)

def calculate_match(resume_keywords, jd_keywords):
    common = resume_keywords & jd_keywords
    missing = jd_keywords - resume_keywords

    # Avoid division by zero
    if len(jd_keywords) == 0:
        score = 0
    else:
        score = (len(common) / len(jd_keywords)) * 100

    return common, missing, round(score, 2)


def main():
    # Load resume text extracted earlier
    with open("extracted_resume.txt", "r", encoding="utf-8") as f:
        resume_text = f.read()

    # Get job description from user
    jd_text = input("\nPaste Job Description:\n\n")

    # Extract keywords
    resume_keywords = extract_keywords(resume_text)
    jd_keywords = extract_keywords(jd_text)

    # Compare
    common, missing, score = calculate_match(resume_keywords, jd_keywords)

    print("\n================ MATCH REPORT ================\n")

    print(f"✅ Skills found in Resume:\n{', '.join(sorted(resume_keywords))}\n")
    print(f"📌 Skills required in Job Description:\n{', '.join(sorted(jd_keywords))}\n")
    print(f"🎯 Matching Skills:\n{', '.join(sorted(common))}\n")
    print(f"➕ Skills you may need to add:\n{', '.join(sorted(missing)) if missing else 'None 🎉'}\n")
    print(f"🔢 Match Score: {score}%\n")

    print("==============================================\n")


if __name__ == "__main__":
    main()
    
def match_resume_to_job(resume_text, jd_text):
    resume_keywords = extract_keywords(resume_text)
    jd_keywords = extract_keywords(jd_text)
    return calculate_match(resume_keywords, jd_keywords)

