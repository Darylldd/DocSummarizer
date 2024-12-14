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
        selected_history_ids = request.POST.getlist("history_ids")  # IDs from selected history records

        combined_text = ""

        # Process selected history records
        if selected_history_ids:
            try:
                selected_history = FileHistory.objects.filter(id__in=selected_history_ids)
                combined_text = " ".join([record.summary for record in selected_history])
            except Exception as e:
                error = f"Error fetching history: {str(e)}"

        # Handle file uploads or prompts
        if form.is_valid() or combined_text:
            uploaded_file = request.FILES.get('file', None)
            prompt = form.cleaned_data.get("prompt", "")

            if uploaded_file:
                file_path = Path(settings.MEDIA_ROOT) / uploaded_file.name

                # Save and process uploaded file
                try:
                    with open(file_path, 'wb') as f:
                        for chunk in uploaded_file.chunks():
                            f.write(chunk)

                    # Extract text based on file type
                    file_extension = uploaded_file.name.split('.')[-1].lower()
                    if file_extension == 'pdf':
                        file_content = extract_text_from_pdf(file_path)
                    elif file_extension == 'docx':
                        file_content = extract_text_from_docx(file_path)
                    elif file_extension == 'txt':
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            file_content = f.read()
                    else:
                        file_content = "Unsupported file type. Please upload a .txt, .pdf, or .docx file."

                    # Append uploaded content to combined text
                    combined_text += f" {file_content}" if "Error" not in file_content else ""

                    # Clean up uploaded file
                    os.remove(file_path)

                except Exception as e:
                    error = f"Error processing file: {str(e)}"

            # Generate summary and insights
            if combined_text:
                summary = summarize_with_gpt2(combined_text, prompt)
                insights = extract_key_insights(combined_text)

                # Save combined summary to history
                FileHistory.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    file_name="Combined Summary",
                    summary=summary,
                    insights=insights,
                )
    else:
        form = FileUploadForm()

    # Fetch history from the database
    history = (
        FileHistory.objects.filter(user=request.user).order_by('-timestamp') 
        if request.user.is_authenticated 
        else FileHistory.objects.all().order_by('-timestamp')
    )

    return render(request, "index.html", {"form": form, "summary": summary, "insights": insights, "error": error, "history": history})
