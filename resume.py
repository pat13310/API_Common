import time

from transformers import pipeline
import torch
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
device = 0 if torch.cuda.is_available() else -1
model = "facebook/bart-large-cnn"
#model = "sshleifer/distilbart-cnn-12-6"

resumeur = pipeline("summarization", device=device)


def summarization(texte):
    resume = resumeur(texte, max_length=130, min_length=30, do_sample=False)
    return resume[0]['summary_text']


texte_a_resumer = (
    "Les technologies de traitement automatique du langage naturel (NLP) ont considérablement évolué, "
    "offrant des solutions sophistiquées pour transformer de longs textes en résumés concis. "
    "Parmi les leaders dans ce domaine, les API d'OpenAI, Hugging Face et Google Cloud se distinguent "
    "par leurs capacités et leurs fonctionnalités uniques. Voici un aperçu détaillé des avantages de chaque service "
    "et comment choisir celui qui convient le mieux à vos besoins."
)

start_time = time.time()  # Get the start time (in seconds)
resume = summarization(texte_a_resumer)
end_time = time.time()  # Get the end time (in seconds)

print("Résumé :", resume)
print("Temps (en secondes): ", end_time - start_time)  # Prints the elapsed time in seconds
