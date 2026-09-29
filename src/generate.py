"""
Script de génération de réponses.

Approche "option A" (documentée dans le README) : vu le faible volume de
documents (une dizaine maximum), on n'utilise pas de recherche par
embeddings. On envoie systématiquement tout le contexte disponible
(fiche animal + tous les documents transcrits) à Claude à chaque question.

Garde-fous mis en place :
- Consigne explicite de ne jamais inventer une valeur absente du contexte
- Consigne de citer le document source de chaque information utilisée
"""
from pathlib import Path

from common import client, MODEL, afficher_usage, TEMPERATURE

DOSSIER_PROCESSED = Path(__file__).parent.parent / "data" / "processed"
FICHE_ANIMAL = Path(__file__).parent.parent / "data" / "fiche_animal.txt"

PROMPT_SYSTEME = """Tu es un assistant qui aide un propriétaire d'animal à
comprendre les résultats d'examens médicaux de son animal, à partir des
documents fournis en contexte.

Règles strictes :
- Réponds uniquement à partir des informations présentes dans le contexte
  fourni. Si l'information demandée n'y figure pas, dis clairement que tu
  ne la trouves pas dans les documents fournis. N'invente jamais une valeur.
- Pour chaque information donnée, précise de quel document elle provient
  (ex. "d'après la prise de sang du [date]").
- Quand la question porte sur une synthèse globale, ne te contente pas de
  lister les résultats document par document. Croise activement les
  informations entre elles (évolution dans le temps, signaux cliniques
  associés à un contexte comme l'âge ou une perte de poids, valeurs en
  limite de plage même si techniquement "normales") pour identifier des
  points de vigilance que l'analyse isolée de chaque document ne ferait
  pas ressortir.
- La fiche animal peut mentionner un contexte de suivi particulier (ex. une
  perte de poids progressive). Si c'est le cas, reprends explicitement ce
  fil dans toute synthèse globale : vérifie et cite l'évolution du poids
  relevé dans chaque document (même quand ce n'est pas la donnée
  principale du document), et mets-la en regard des autres résultats.
- Ne te contente jamais de lister côte à côte plusieurs signaux qui
  pointent vers une même hypothèse clinique. Quand plusieurs éléments
  distincts (issus de documents différents ou de la fiche animal) semblent
  converger, formule explicitement cette convergence comme une seule
  observation reliée, plutôt que de les présenter comme des points
  séparés, même sous une même rubrique "points de vigilance".
- Tu n'es pas vétérinaire : formule tes réponses comme une aide à la
  lecture des documents, pas comme un diagnostic médical. Recommande de
  contacter le vétérinaire pour toute question clinique importante.
"""


def charger_contexte() -> str:
    """Assemble la fiche animal et tous les documents transcrits en un seul texte."""
    morceaux = []

    if FICHE_ANIMAL.exists():
        morceaux.append(f"--- Fiche animal ---\n{FICHE_ANIMAL.read_text(encoding='utf-8')}")

    fichiers_documents = sorted(DOSSIER_PROCESSED.glob("*.txt"))
    for fichier in fichiers_documents:
        morceaux.append(f"--- Document : {fichier.name} ---\n{fichier.read_text(encoding='utf-8')}")

    return "\n\n".join(morceaux)


def poser_question(question: str, contexte: str) -> str:
    reponse = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        extra_body={"temperature": TEMPERATURE},
        system=PROMPT_SYSTEME,
        messages=[
            {
                "role": "user",
                "content": f"Contexte disponible :\n\n{contexte}\n\nQuestion : {question}",
            }
        ],
    )
    afficher_usage(reponse)
    return reponse.content[0].text


def boucle_questions():
    contexte = charger_contexte()
    if not contexte.strip():
        print("Aucun document trouvé. Lance d'abord ingest.py.")
        return

    print("Assistant prêt. Pose tes questions (Ctrl+C ou 'quit' pour quitter).\n")
    while True:
        question = input("Question > ").strip()
        if question.lower() in {"quit", "exit"}:
            break
        if not question:
            continue

        reponse = poser_question(question, contexte)
        print(f"\n{reponse}\n")


if __name__ == "__main__":
    boucle_questions()