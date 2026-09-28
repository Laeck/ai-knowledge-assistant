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

## Confidentialité des données

Les documents ingérés (PDF, photos) sont envoyés à l'API Anthropic pour être
transcrits (capacité de vision de Claude). Ils ne restent donc pas uniquement
en local pendant cette étape.

Ce que dit la politique de confidentialité d'Anthropic pour l'API (à la date
de rédaction) :
- Les entrées et sorties envoyées à l'API sont automatiquement supprimées des
  serveurs backend dans les 30 jours suivant leur réception ou génération,
  sauf obligation légale ou lutte contre les abus.
- Les données envoyées via l'API commerciale ne sont pas utilisées pour
  entraîner de futurs modèles (contrairement à certains réglages possibles
  sur Claude.ai grand public).

Ce projet traite ici des données médicales vétérinaires (donc non-sensibles
au sens légal, à la différence de données de santé humaines), mais la même
question se poserait pour tout document confidentiel. Une évolution possible
pour un cas d'usage professionnel serait de proposer un mode "zero data
retention" (accord spécifique avec Anthropic pour une suppression immédiate,
sans les 30 jours de délai standard).