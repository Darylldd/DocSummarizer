from django.shortcuts import render
from django.conf import settings
from .forms import FileUploadForm
from .utils import summarize_with_gpt2
from pathlib import Path
import fitz  # PyMuPDF for PDFs
import docx  # python-docx for DOCX files

# Function to extract text from PDF
def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Function to extract text from DOCX
def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def index(request):
    summary = ""
    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            prompt = form.cleaned_data.get("prompt", "")
            file_path = Path(settings.MEDIA_ROOT) / uploaded_file.name

            # Save the uploaded file
            with open(file_path, 'wb') as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)

            # Check the file type and extract text accordingly
            file_extension = uploaded_file.name.split('.')[-1].lower()
            if file_extension == 'pdf':
                file_content = extract_text_from_pdf(file_path)
            elif file_extension == 'docx':
                file_content = extract_text_from_docx(file_path)
            elif file_extension == 'txt':
                # Ensure proper encoding for txt files
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    file_content = f.read()
            else:
                # Handle unsupported file types
                file_content = "Unsupported file type. Please upload a .txt, .pdf, or .docx file."
            
            # Get the summary from GPT-2
            summary = summarize_with_gpt2(file_content, prompt)

            # Clean up the uploaded file after processing
            file_path.unlink()
    else:
        form = FileUploadForm()

    return render(request, "index.html", {"form": form, "summary": summary})
