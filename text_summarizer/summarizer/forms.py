from django import forms

class FileUploadForm(forms.Form):
    file = forms.FileField()
    prompt = forms.CharField(widget=forms.Textarea, required=False, label="Prompt")
