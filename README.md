# AI Knowledge Assistant

Assistant qui répond à des questions en s'appuyant sur une base documentaire,
en citant ses sources et en évitant d'inventer une réponse quand l'information
n'est pas disponible.

## Cas d'usage

Suivi de l'historique médical d'un animal (résultats d'analyses, échographies,
bilans) : poser des questions en langage naturel sur des documents médicaux
plutôt que de les relire un par un.

Exemples de questions cibles :
- "Quelle était sa valeur de T4 lors du dernier bilan ?"
- "Est-ce que sa fonction rénale a évolué depuis l'échographie de [date] ?"

## Approche technique

RAG (Retrieval-Augmented Generation) : les documents sont découpés, indexés,
puis recherchés au moment de la question pour donner du contexte pertinent
au modèle avant qu'il ne génère une réponse.

## Statut

En construction — étape actuelle : ingestion des documents.
