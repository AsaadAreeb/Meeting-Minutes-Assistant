import time
import numpy as np
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge_score import rouge_scorer
from nltk.util import ngrams
import google.generativeai as genai
from google.oauth2 import service_account
from google.cloud import storage, speech
import logging
import os

# Initialize logging with append mode
logging.basicConfig(
    filename="../logs/week_4/model_evaluation_logs/model_evaluation.lo",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode='a'  # Append mode
)

# Path to the service account JSON file
SERVICE_ACCOUNT_FILE = ""  # Update the name as needed

# Initialize Google Cloud clients
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
storage_client = storage.Client(credentials=credentials)
speech_client = speech.SpeechClient(credentials=credentials)
bucket_name = "meeting-ai-storage"  # Replace with your bucket name
bucket = storage_client.bucket(bucket_name)

# Initialize Gemini API
os.environ["GEMINI_API_KEY"] = ""

# Function to read transcript from a file
def read_transcript_from_file(file_path):
    """
    Reads the transcript from a text file and returns it.
    """
    try:
        with open(file_path, 'r') as file:
            transcript = file.read().strip()  # Remove any leading/trailing whitespace
        return transcript
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {e}")
        return ""

# Function to calculate BLEU score
def calculate_bleu(reference, generated):
    """
    Calculates BLEU score between reference and generated text.
    """
    smoothing_function = SmoothingFunction().method1
    reference_tokens = reference.split()
    generated_tokens = generated.split()
    
    bleu_score = sentence_bleu([reference_tokens], generated_tokens, smoothing_function=smoothing_function)
    return bleu_score

# Function to calculate ROUGE score
def calculate_rouge(reference, generated):
    """
    Calculates ROUGE score between reference and generated text.
    """
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    scores = scorer.score(reference, generated)
    return scores

# Function to calculate Self-BLEU score (Diversity Metric)
def calculate_self_bleu(texts):
    """
    Calculates Self-BLEU score to measure the diversity of the generated texts.
    A lower score indicates higher diversity.
    """
    # Tokenizing each text into n-grams
    n = 2  # For bigrams, can be adjusted
    ngram_list = []
    
    for text in texts:
        tokens = text.split()
        ngrams_list = list(ngrams(tokens, n))
        ngram_list.append(set(ngrams_list))  # Using set to remove duplicate n-grams within the same text
    
    # Self-BLEU (lower is better)
    bleu_scores = []
    for i, text_ngrams in enumerate(ngram_list):
        other_ngrams = [ngram_list[j] for j in range(len(ngram_list)) if j != i]
        intersection = set.intersection(*other_ngrams)
        bleu_scores.append(len(intersection) / len(text_ngrams) if len(text_ngrams) > 0 else 0)
    
    self_bleu_score = np.mean(bleu_scores)
    return self_bleu_score


# Function to normalize text by removing line breaks and extra whitespace
def normalize_text(text):
    """
    Normalizes text by removing line breaks and reducing extra whitespace.
    """
    return " ".join(text.split())

# Function to read and normalize a transcript from a file
def read_and_normalize_transcript(file_path):
    """
    Reads a transcript from a text file and normalizes it.
    """
    try:
        with open(file_path, 'r') as file:
            transcript = file.read().strip()  # Remove leading/trailing whitespace
            normalized_transcript = normalize_text(transcript)
        return normalized_transcript
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {e}")
        return ""

# Function to log evaluation results with timestamps
def log_evaluation_results(bleu_score, rouge_scores, self_bleu_score, generated_transcript_filename):
    """
    Logs the evaluation results with timestamps in a structured format.
    """
    logging.info(f"Evaluation Results for {generated_transcript_filename} - BLEU Score: {bleu_score}")
    logging.info(f"ROUGE-1: {rouge_scores['rouge1']}")
    logging.info(f"ROUGE-2: {rouge_scores['rouge2']}")
    logging.info(f"ROUGE-L: {rouge_scores['rougeL']}")
    logging.info(f"Self-BLEU Score (for all generated transcripts): {self_bleu_score}")

# Function to evaluate the model's performance
def evaluate_model(reference_transcript, generated_transcripts):
    """
    Evaluates the model based on BLEU, ROUGE, Self-BLEU.
    Logs the results with timestamps.
    """
    # Calculate Self-BLEU (for all generated transcripts)
    self_bleu_score = calculate_self_bleu(generated_transcripts)

    # Evaluate for each generated transcript
    for generated_transcript in generated_transcripts:
        # Similarity Metrics
        bleu_score = calculate_bleu(reference_transcript, generated_transcript)
        rouge_scores = calculate_rouge(reference_transcript, generated_transcript)

        # Log the evaluation results for each generated transcript
        generated_transcript_filename = generated_transcript_files[generated_transcripts.index(generated_transcript)]  # Get the filename
        log_evaluation_results(bleu_score, rouge_scores, self_bleu_score, generated_transcript_filename)

# Example usage:
# Get file paths for the original and generated transcripts
original_transcript_file = input("Enter the path to the original transcript file: ")
generated_transcript_files = input("Enter the paths to the generated transcript files (separate multiple files with commas): ").split(',')

# Read and normalize the original transcript from the file
original_transcript = read_and_normalize_transcript(original_transcript_file)

# Read and normalize the generated transcripts from the provided files
generated_transcripts = [read_and_normalize_transcript(file.strip()) for file in generated_transcript_files]

# Evaluate the model and log the results
evaluate_model(original_transcript, generated_transcripts)
