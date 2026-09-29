"""
Script d'évaluation.

Pour chaque question du jeu de test (qa_testset.json) :
1. On obtient la réponse réelle de l'assistant (generate.py)
2. On demande à Claude de jouer le rôle de "juge" : est-ce que chaque critère
   attendu est bien respecté dans la réponse obtenue ?

Pourquoi un juge plutôt qu'une comparaison de texte exacte : les réponses de
l'assistant ne sont jamais formulées à l'identique d'un run à l'autre, donc
comparer mot pour mot ne fonctionnerait pas. On vérifie plutôt le contenu.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from common import TEMPERATURE, client, MODEL, afficher_usage
from generate import charger_contexte, poser_question

DOSSIER_EVAL = Path(__file__).parent
FICHIER_TESTSET = DOSSIER_EVAL / "qa_testset.json"

PROMPT_JUGE = """Tu es un juge chargé d'évaluer une réponse d'assistant IA.

Voici la réponse à évaluer :
---
{reponse}
---

Voici la liste des critères attendus. Pour CHAQUE critère, réponds
uniquement par "OK" ou "MANQUANT", suivi d'une justification en une phrase.

Critères :
{criteres}

Format de réponse strict (une ligne par critère) :
1. OK/MANQUANT - justification
2. OK/MANQUANT - justification
...
"""


def evaluer_reponse(reponse: str, criteres: list[str]) -> str:
    criteres_numerotes = "\n".join(f"{i+1}. {c}" for i, c in enumerate(criteres))
    prompt = PROMPT_JUGE.format(reponse=reponse, criteres=criteres_numerotes)

    verdict = client.messages.create(
        model=MODEL,
        max_tokens=500,
        temperature=TEMPERATURE,
        messages=[{"role": "user", "content": prompt}],
    )
    afficher_usage(verdict)
    return verdict.content[0].text


def executer_evaluation():
    tests = json.loads(FICHIER_TESTSET.read_text(encoding="utf-8"))
    contexte = charger_contexte()

    total_criteres = 0
    total_ok = 0

    for test in tests:
        print(f"\n{'='*60}")
        print(f"Test : {test['id']}")
        print(f"Question : {test['question']}")

        reponse = poser_question(test["question"], contexte)
        verdict = evaluer_reponse(reponse, test["criteres_attendus"])

        print(f"\nVerdict :\n{verdict}")

        total_criteres += len(test["criteres_attendus"])
        total_ok += verdict.count("OK")

    print(f"\n{'='*60}")
    print(f"Score global : {total_ok}/{total_criteres} critères validés")


if __name__ == "__main__":
    executer_evaluation()