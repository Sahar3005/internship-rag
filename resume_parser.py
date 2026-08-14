from pypdf import PdfReader


def extract_resume_text(pdf_path):

    reader = PdfReader(pdf_path)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


if __name__ == "__main__":

    pdf_path = "data/Sahar_Ansari (5).pdf"

    text = extract_resume_text(pdf_path)

    print("\n")
    print("=" * 60)
    print("EXTRACTED RESUME TEXT")
    print("=" * 60)

    print(text)