from .models import FileHistory
from django.shortcuts import render
from django.conf import settings
from pathlib import Path
from .forms import FileUploadForm
from .utils import summarize_with_gpt2, extract_key_insights
import fitz  # PyMuPDF for extracting text from PDFs
import docx  # python-docx for extracting text from DOCX files
from datetime import datetime
import os

def extract_text_from_pdf(file_path):
    try:
        doc = fitz.open(file_path)
        text = "".join([page.get_text() for page in doc])
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def extract_text_from_docx(file_path):
    try:
        doc = docx.Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        return f"Error reading DOCX: {str(e)}"

def index(request):
    summary = ""
    insights = []
    error = None

    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            prompt = form.cleaned_data.get("prompt", "")
            file_path = Path(settings.MEDIA_ROOT) / uploaded_file.name

            # Save the uploaded file
            try:
                with open(file_path, 'wb') as f:
                    for chunk in uploaded_file.chunks():
                        f.write(chunk)
            except Exception as e:
                error = f"Error saving file: {str(e)}"

            # Extract text based on file type
            if not error:
                file_extension = uploaded_file.name.split('.')[-1].lower()
                if file_extension == 'pdf':
                    file_content = extract_text_from_pdf(file_path)
                elif file_extension == 'docx':
                    file_content = extract_text_from_docx(file_path)
                elif file_extension == 'txt':
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            file_content = f.read()
                    except Exception as e:
                        file_content = f"Error reading TXT file: {str(e)}"
                else:
                    file_content = "Unsupported file type. Please upload a .txt, .pdf, or .docx file."

                # Generate summary and key insights if file content is valid
                if "Error" not in file_content:
                    summary = summarize_with_gpt2(file_content, prompt)
                    insights = extract_key_insights(file_content)

                    # Save history to the database
                    FileHistory.objects.create(
                        user=request.user if request.user.is_authenticated else None,
                        file_name=uploaded_file.name,
                        summary=summary,
                        insights=insights,
                    )

            # Clean up the uploaded file
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                error = f"Error cleaning up file: {str(e)}"
    else:
        form = FileUploadForm()

    # Fetch history from the database
    history = (
        FileHistory.objects.filter(user=request.user).order_by('-timestamp') 
        if request.user.is_authenticated 
        else FileHistory.objects.all().order_by('-timestamp')
    )

    return render(request, "index.html", {"form": form, "summary": summary, "insights": insights, "error": error, "history": history})
