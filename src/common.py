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


def afficher_usage(response):
    """Affiche le nombre de tokens consommés par un appel à l'API."""
    usage = response.usage
    print(
        f"[tokens] entrée={usage.input_tokens} "
        f"sortie={usage.output_tokens}"
    )
