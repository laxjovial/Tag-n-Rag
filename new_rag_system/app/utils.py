import io
import pypdf
import docx

def read_file_content(file) -> str:
    """
    Reads the content of a file-like object and returns it as a string.
    Supports PDF, DOCX, and TXT files.
    """
    content = ""
    filename = file.filename.lower()

    if filename.endswith(".pdf"):
        pdf_reader = pypdf.PdfReader(file.file)
        for page in pdf_reader.pages:
            content += page.extract_text() or ""
    elif filename.endswith(".docx"):
        doc = docx.Document(file.file)
        for para in doc.paragraphs:
            content += para.text + "\n"
    elif filename.endswith(".txt"):
        content = file.file.read().decode("utf-8")
    else:
        # For other file types, you might want to raise an exception
        # or handle them differently.
        raise ValueError(f"Unsupported file type: {filename}")

    return content
