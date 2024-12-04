import spacy
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
from datasets import load_dataset

# Load the pre-trained GPT-2 model and tokenizer
model_name = "gpt2"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = GPT2LMHeadModel.from_pretrained(model_name).to(device)
tokenizer = GPT2Tokenizer.from_pretrained(model_name)

# Set pad_token to eos_token as GPT-2 lacks a padding token
tokenizer.pad_token = tokenizer.eos_token

# Load the CNN/Daily Mail dataset for fallback summaries
dataset = load_dataset("cnn_dailymail", "3.0.0")

# Load spaCy model for NER (Named Entity Recognition)
nlp = spacy.load("en_core_web_sm")

def summarize_with_gpt2(text, prompt=None):
    """
    Summarizes the input text using GPT-2. If no text is provided, it uses a default article from the dataset.
    
    Parameters:
    - text (str): The input text to summarize.
    - prompt (str): An optional prompt to guide the summarization.

    Returns:
    - summary (str): The generated summary.
    """
    if not text:
        default_article = dataset["train"][0]["article"]
        text = default_article if not prompt else prompt + " " + default_article
    else:
        if prompt:
            text = prompt + " " + text

    # Tokenize and encode the text
    inputs = tokenizer(text, return_tensors="pt", max_length=512, truncation=True, padding=True).to(device)

    # Generate the summary
    max_new_tokens = 1024
    input_length = inputs['input_ids'].shape[-1]
    max_tokens = min(input_length + max_new_tokens, 1024)

    outputs = model.generate(
        inputs['input_ids'],
        attention_mask=inputs['attention_mask'],
        max_length=max_tokens,
        num_return_sequences=1,
        no_repeat_ngram_size=1,
        temperature=0.8,
        top_p=0.9,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id,
    )

    summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return summary


def extract_key_insights(text):
    """
    Extract key insights from the text using spaCy (Named Entity Recognition).
    
    Parameters:
    - text (str): The input text to analyze.

    Returns:
    - insights (list): A list of key insights (named entities).
    """
    doc = nlp(text)
    insights = []
    for ent in doc.ents:
        insights.append({'text': ent.text, 'label': ent.label_})
    
    return insights
