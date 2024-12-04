from django import forms

class FileUploadForm(forms.Form):
    file = forms.FileField()
    prompt = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'placeholder': 'Enter prompt'}))
