from transformers import GPT2LMHeadModel, GPT2Tokenizer
from datasets import load_dataset

# Load the pre-trained GPT-2 model and tokenizer
model_name = "gpt2" #distilgpt2
model = GPT2LMHeadModel.from_pretrained(model_name)
tokenizer = GPT2Tokenizer.from_pretrained(model_name)

# Set the pad_token to eos_token since GPT-2 does not have a padding token by default
tokenizer.pad_token = tokenizer.eos_token

# Load the CNN/Daily Mail dataset
dataset = load_dataset("cnn_dailymail", "3.0.0")
#dataset = load_dataset("pubmed")
#dataset = load_dataset("gigaword")
#dataset = load_dataset("newsroom")

# Example of how to process a specific article from the dataset
article = dataset["train"][0]["article"]  # Example article from the dataset
summary = dataset["train"][0]["highlights"]  # Summary of the article

# Summarization function using GPT-2
def summarize_with_gpt2(text, prompt=None, dataset=None):
    # If a prompt is provided, prepend it to the text 
    if prompt:
        text = prompt + " " + text

    # If a dataset is provided, prepend the dataset or example text
    if dataset:
        # Assuming `dataset` is a list of relevant data snippets or summaries
        text = dataset + " " + text

    # Encode input text and generate a summary with attention_mask
    inputs = tokenizer(text, return_tensors="pt", max_length=512, truncation=True, padding=True)

    # Set max_new_tokens to ensure we don't exceed the input length
    max_new_tokens = 150  # Define the max tokens to generate
    input_length = inputs['input_ids'].shape[-1]  # Get the length of input text

    # Calculate how many new tokens can be generated
    max_tokens = input_length + max_new_tokens

    # Generate the summary
    outputs = model.generate(
        inputs['input_ids'],  # Use the input_ids
        attention_mask=inputs['attention_mask'],  # Explicitly pass attention_mask
        max_length=max_tokens,  # Ensure we don't exceed the input length + new tokens
        num_return_sequences=1,
        no_repeat_ngram_size=2,
        pad_token_id=tokenizer.eos_token_id  # Set pad_token_id to eos_token_id
    )

    # Decode the generated summary
    summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return summary