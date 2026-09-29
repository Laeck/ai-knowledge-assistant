"""
Script d'ingestion.

Lit chaque document dans data/raw/ (PDF ou photo), envoie son contenu à
Claude (capacité "vision") pour en obtenir une transcription fidèle, puis
sauvegarde le résultat en texte dans data/processed/.

Pourquoi passer par la vision de Claude plutôt qu'un outil d'OCR classique :
avec seulement une dizaine de documents et des photos parfois imparfaites
(angle, luminosité), la vision de Claude est plus robuste qu'un OCR
traditionnel, en particulier pour lire des tableaux de valeurs médicales.
"""
import base64
from pathlib import Path

import fitz  # PyMuPDF, sert à transformer les pages PDF en images

from common import client, MODEL, afficher_usage, TEMPERATURE

DOSSIER_RAW = Path(__file__).parent.parent / "data" / "raw"
DOSSIER_PROCESSED = Path(__file__).parent.parent / "data" / "processed"

EXTENSIONS_IMAGE = {".png", ".jpg", ".jpeg"}

PROMPT_TRANSCRIPTION = """Tu es assistant de transcription. Transcris intégralement
le contenu de ce document médical (analyses vétérinaires : prise de sang,
bilan thyroïdien, échographie, etc.).

Consignes strictes :
- Conserve toutes les valeurs, unités et plages de référence telles qu'elles
  apparaissent, sans les reformuler ni les arrondir.
- Indique la date de l'examen si elle est visible.
- N'invente rien : si un mot ou un nombre est illisible, écris [illisible]
  plutôt que de deviner.
- Ne résume pas : restitue le contenu complet, sous forme de texte structuré
  (utilise des tirets ou un tableau si utile).
"""


def image_vers_bloc_base64(donnees_image: bytes, media_type: str) -> dict:
    """Encode des octets d'image en bloc 'image' au format attendu par l'API."""
    return {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": media_type,
            "data": base64.standard_b64encode(donnees_image).decode("utf-8"),
        },
    }


def charger_blocs_images(chemin_fichier: Path) -> list[dict]:
    """Transforme un fichier (image ou PDF) en une liste de blocs image."""
    extension = chemin_fichier.suffix.lower()

    if extension in EXTENSIONS_IMAGE:
        media_type = "image/png" if extension == ".png" else "image/jpeg"
        return [image_vers_bloc_base64(chemin_fichier.read_bytes(), media_type)]

    if extension == ".pdf":
        blocs = []
        pdf = fitz.open(chemin_fichier)
        for page in pdf:
            # zoom=2 augmente la résolution du rendu, pour une meilleure lecture
            # des petits caractères (valeurs de laboratoire notamment)
            pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            blocs.append(image_vers_bloc_base64(pixmap.tobytes("png"), "image/png"))
        pdf.close()
        return blocs

    raise ValueError(f"Extension non gérée : {extension}")


def transcrire_document(chemin_fichier: Path) -> str:
    """Envoie un document à Claude et renvoie sa transcription en texte."""
    blocs_images = charger_blocs_images(chemin_fichier)

    reponse = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        temperature=TEMPERATURE,
        messages=[
            {
                "role": "user",
                "content": blocs_images + [{"type": "text", "text": PROMPT_TRANSCRIPTION}],
            }
        ],
    )
    afficher_usage(reponse)
    return reponse.content[0].text


def ingerer_tous_les_documents():
    fichiers = [
        f for f in DOSSIER_RAW.iterdir()
        if f.suffix.lower() in EXTENSIONS_IMAGE | {".pdf"}
    ]

    if not fichiers:
        print(f"Aucun document trouvé dans {DOSSIER_RAW}")
        return

    for chemin_fichier in fichiers:
        print(f"→ Transcription de {chemin_fichier.name}...")
        texte = transcrire_document(chemin_fichier)

        chemin_sortie = DOSSIER_PROCESSED / f"{chemin_fichier.stem}.txt"
        chemin_sortie.write_text(texte, encoding="utf-8")
        print(f"  Sauvegardé dans {chemin_sortie.name}\n")


if __name__ == "__main__":
    ingerer_tous_les_documents()
