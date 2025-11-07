import streamlit as st
from extract import extract_resume_text
from jobmatcher import match_resume_to_job

st.title("💼 AI Resume Matcher (MVP)")

resume = st.file_uploader("Upload Resume (.pdf/.docx)", type=["pdf","docx"])
jd_text = st.text_area("Paste Job Description Here")

if resume and jd_text:
    # Save file with original extension
    filename = "uploaded_" + resume.name
    with open(filename, "wb") as f:
        f.write(resume.read())

    # Extract resume text
    resume_text = extract_resume_text(filename)

    # Match resume to job description
    common, missing, score = match_resume_to_job(resume_text, jd_text)

    st.subheader("🎯 Match Report")
    st.write(f"**Match Score:** {score}%")
    st.progress(score / 100)

    st.write("✅ **Matching Skills:**", ", ".join(sorted(common)) if common else "None")
    st.write("❌ **Missing Skills:**", ", ".join(sorted(missing)) if missing else "None")
