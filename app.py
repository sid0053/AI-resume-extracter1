import os
import io
import tempfile
import pandas as pd
import streamlit as st

# import your modules
from extract import extract_resume_text, clean_text
from jobmatcher import extract_keywords, calculate_match

st.set_page_config(page_title="JD ↔ Resume Matcher", page_icon="🎯", layout="wide")

def _read_text_file(uploaded):
    bytes_data = uploaded.read()
    for enc in ("utf-8", "latin-1"):
        try:
            return bytes_data.decode(enc)
        except Exception:
            continue
    return bytes_data.decode(errors="ignore")

@st.cache_data(show_spinner=False)
def _extract_from_path(tmp_path):
    raw, cleaned = extract_resume_text(tmp_path, clean=True)
    return raw, cleaned

@st.cache_data(show_spinner=False)
def _keywords(text):
    return extract_keywords(text)

@st.cache_data(show_spinner=False)
def _match(resume_kw, jd_kw):
    return calculate_match(resume_kw, jd_kw)

st.title("JD ↔ Resume Matcher (MVP)")
st.caption("Weeks 7–8 – Upload your resume & JD to see how well they match.")

with st.sidebar:
    st.header("How it works")
    st.write("1️⃣ Upload resume (PDF/DOCX/TXT)\n\n2️⃣ Paste JD\n\n3️⃣ See score + missing skills")
    st.divider()
    st.write("⚠️ Scanned PDFs may show empty text – use OCR if needed.")

colL, colR = st.columns([1,1])
with colL:
    st.subheader("Resume")
    resume_file = st.file_uploader("Upload .pdf / .docx / .txt",
                                   type=["pdf","docx","txt"], accept_multiple_files=False)
    resume_text = st.text_area("Or paste resume text", height=200)
with colR:
    st.subheader("Job Description")
    jd_text = st.text_area("Paste JD", height=300)

run_btn = st.button("Calculate Match", type="primary")

if run_btn:
    if not (resume_file or resume_text.strip()):
        st.warning("Please upload or paste your resume."); st.stop()
    if not jd_text.strip():
        st.warning("Please paste the Job Description."); st.stop()

    if resume_file:
        ext = os.path.splitext(resume_file.name)[1].lower()
        if ext == ".txt":
            extracted_raw = _read_text_file(resume_file)
            extracted_clean = clean_text(extracted_raw)
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                tmp.write(resume_file.read()); tmp_path = tmp.name
            try:
                extracted_raw, extracted_clean = _extract_from_path(tmp_path)
            finally:
                os.remove(tmp_path)
    else:
        extracted_raw = resume_text; extracted_clean = clean_text(extracted_raw)

    with st.spinner("Extracting & matching..."):
        resume_kw = _keywords(extracted_clean)
        jd_kw = _keywords(jd_text)
        result = _match(resume_kw, jd_kw)

    st.success("Done!")

    c1, c2, c3 = st.columns(3)
    c1.metric("Match Score", f"{result['score']}%")
    c2.metric("Exact Matches", f"{len(result.get('common', []))}")
    c3.metric("Missing (JD)", f"{len(result.get('missing', []))}")
    st.progress(min(100, int(result['score'])) / 100)

    left, right = st.columns(2)
    with left:
        st.subheader("Matched Keywords")
        st.write(", ".join(sorted(result.get("common", []))) or "—")
        if "fuzzy_common" in result:
            st.subheader("Close Matches (Fuzzy)")
            st.caption("Near matches counted as partial credit.")
            st.write(", ".join(sorted(result.get("fuzzy_common", []))) or "—")
    with right:
        st.subheader("Missing Keywords (from JD)")
        st.write(", ".join(sorted(result.get("missing", []))) or "None 🎉")

    st.divider()
    st.subheader("Download Reports")
    csv_matched = pd.DataFrame(sorted(result.get("common", [])), columns=["matched"]).to_csv(index=False).encode()
    st.download_button("Download Matched CSV", csv_matched, "matched_keywords.csv")

    csv_missing = pd.DataFrame(sorted(result.get("missing", [])), columns=["missing"]).to_csv(index=False).encode()
    st.download_button("Download Missing CSV", csv_missing, "missing_keywords.csv")

    report = io.StringIO()
    report.write(f"Match Score: {result['score']}%\n\n")
    report.write("Matched:\n" + ", ".join(sorted(result.get("common", []))) + "\n\n")
    report.write("Missing:\n" + ", ".join(sorted(result.get("missing", []))))
    st.download_button("Download Text Report", report.getvalue().encode(), "match_report.txt")
else:
    st.info("Upload resume + paste JD → click Calculate Match to start.")
