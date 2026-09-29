"""
Fonctions et constantes partagées par tous les scripts du projet.
"""
import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

# Modèle utilisé dans tout le projet (rapide et peu coûteux, suffisant pour ce volume)
MODEL = "claude-haiku-4-5-20251001"

# Température = degré d'aléatoire des réponses (0 = quasi déterministe et
# factuel, 1 = plus créatif/varié). On la met au minimum ici : ce projet
# doit rester factuel (transcription, réponses médicales, jugement d'éval),
# pas créatif.
TEMPERATURE = 0

def afficher_usage(response):
    """Affiche le nombre de tokens consommés par un appel à l'API."""
    usage = response.usage
    print(
        f"[tokens] entrée={usage.input_tokens} "
        f"sortie={usage.output_tokens}"
    )
