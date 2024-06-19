import re
import time

import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '1'
os.environ["CUDA_VISIBLE_DEVICES"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "True"

import torch
from transformers import pipeline

device = 0 if torch.cuda.is_available() else -1
# model = "facebook/bart-large-cnn"x
model = "sshleifer/distilbart-cnn-12-6"
# model = "sshleifer/distilbart-xsum-12-1"
# model="sshleifer/distill-pegasus-cnn-16-4"
revision = "a4f8f3e"
resumeur = pipeline("summarization", model=model, device=device)

remplacement = {
    "to": "vers",
    "that": "que",
    "and": "et",
    "or": "ou",
    "for": "pour",
    "with": "avec",
    "by": "par",
    "in": "dans",
    "on": "sur",
    "as": "comme",
    "is": "est",
    "are": "sont",
    "was": "était",
    "were": "étaient",
    "will": "va",
    "would": "voudrait",
    "could": "pourrait",
    "should": "devrait",
    "can": "peut",
    "of": "de",
    "from": "de",
    "about": "à propos de",
    "into": "dans",
    "over": "au-dessus de",
    "under": "sous",
    "between": "entre",
    "among": "parmi",
    "through": "à travers",
    "before": "avant",
    "after": "après",
    "during": "pendant",
    "without": "sans",
    "against": "contre",
    "within": "au sein de",
    "out": "dehors",
    "across": "à travers",
    "NLP": "traitement automatique du langage naturel"
}


# simplificateur = pipeline("summarization", model="sshleifer/distilbart-xsum-12-1")


def summarization(texte):
    resume = resumeur(texte, max_length=130, min_length=90, do_sample=False)
    return resume[0]['summary_text']


def simplifier_texte(texte):
    global remplacement
    # Remplacer les mots en anglais par leurs équivalents français
    for terme, remplacement in remplacement.items():
        texte = re.sub(r'\b{}\b'.format(terme), remplacement, texte, flags=re.IGNORECASE)
    return texte


def simplification(texte):
    # Résumé pour vulgarisation
    resume = resumeur(texte, max_length=300, min_length=100, do_sample=False)
    texte = resume[0]['summary_text']
    return simplifier_texte(texte)
