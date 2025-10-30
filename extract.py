import pdfplumber

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

file = input("Enter PDF file path: ").strip('"')

raw_text = extract_text_from_pdf(file)

# ✅ Clean but keep formatting
cleaned_text = "\n".join(
    line.strip().lower()
    for line in raw_text.splitlines()
    if line.strip() != ""
)

print("\n✅ Text Extracted Successfully!\n")

# Save to file
output_file = "extracted_resume.txt"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(cleaned_text)

print(f"📄 Saved cleaned text to: {output_file}")
