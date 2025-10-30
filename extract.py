import pdfplumber
import docx
import re

def extract_text_from_pdf(path):
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(path):
    doc = docx.Document(path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9@\.\+\-\s\n]', ' ', text)  # allow newline
    text = re.sub(r'[ ]{2,}', ' ', text)  # collapse only multiple spaces
    text = re.sub(r'\n{3,}', '\n\n', text)  # prevent too many blank lines
    return text.strip()


def main():
    file_path = input("Enter resume file path (.pdf or .docx): ")

    if file_path.endswith(".pdf"):
        raw_text = extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        raw_text = extract_text_from_docx(file_path)
    else:
        print("❌ Unsupported format. Use PDF or DOCX.")
        return

    cleaned_text = clean_text(raw_text)

    with open("extracted_resume.txt", "w", encoding="utf-8") as f:
        f.write(cleaned_text)

    print("✅ Resume text extracted and saved to extracted_resume.txt")

if __name__ == "__main__":
    main()
