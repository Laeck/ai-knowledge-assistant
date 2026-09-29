# AI Knowledge Assistant

Assistant qui répond à des questions en s'appuyant sur une base documentaire,
en citant ses sources et en évitant d'inventer une réponse quand l'information
n'est pas disponible.

## Cas d'usage

Suivi de l'historique médical d'un animal (résultats d'analyses,
échographies, comptes-rendus d'opération, et tout autre document
vétérinaire courant) : poser des questions en langage naturel sur ces
documents plutôt que de les relire un par un.

Exemples de questions cibles :
- "Quelle était sa valeur de T4 lors du dernier bilan ?"
- "Est-ce que sa fonction rénale a évolué depuis l'échographie de [date] ?"

## Approche technique

RAG (Retrieval-Augmented Generation) : les documents sont découpés, indexés,
puis recherchés au moment de la question pour donner du contexte pertinent
au modèle avant qu'il ne génère une réponse.

## Choix d'architecture : pas de recherche par embeddings
 
Anthropic ne propose pas son propre modèle d'embeddings ; le fournisseur
recommandé (Voyage AI) nécessite un compte et une clé API séparés.
 
Vu le faible volume de documents visé pour ce projet (moins d'une dizaine),
une recherche par embeddings (vector search) n'apporte pas de bénéfice réel :
tous les documents tiennent largement dans le contexte d'une seule requête.
Le choix retenu est donc d'envoyer systématiquement l'intégralité des
documents transcrits (+ une fiche de contexte sur l'animal) à chaque
question, sans étape de recherche préalable.
 
Cette approche ne serait plus adaptée à partir d'un volume de documents
qui ne tiendrait plus dans une seule requête (au-delà de quelques dizaines
de pages, selon les modèles) : il faudrait alors introduire une étape de
recherche (embeddings + similarité) pour ne sélectionner que les passages
pertinents avant de générer une réponse.

## Itérations sur le prompt (retour d'expérience)

Le jeu de test (`eval/qa_testset.json`) a révélé un défaut que l'observation
manuelle avait déjà repéré : sur une synthèse globale, l'assistant listait
les résultats document par document sans relier des signaux qui, mis
ensemble, méritaient d'être présentés comme convergents (ici : une perte de
poids progressive et une valeur de T4 en zone limite pour un chat âgé).

Itération 1 : ajout d'une consigne générale ("croise les informations entre
elles") → insuffisant, l'assistant continuait à lister les résultats sans
les relier explicitement.

Itération 2 : ajout d'un exemple concret directement dans le prompt,
formulant la conclusion attendue mot pour mot. Le test passait, mais ce
n'était pas une preuve de raisonnement : le modèle pouvait simplement
recopier l'exemple fourni. Un jeu de test ne vaut que si le prompt ne
contient pas déjà la réponse qu'il est censé vérifier.

Itération 3 : retrait de l'exemple concret, conservation d'une seule
consigne de méthode générale ("ne liste jamais côte à côte des signaux
convergents, relie-les explicitement"). Le test est passé sans qu'aucune
réponse n'ait été soufflée au modèle, avec une formulation plus nuancée
que l'exemple retiré (hypothèses alternatives envisagées, recommandation
de suivi plutôt qu'affirmation d'un diagnostic).

Enseignement principal : le blocage initial était un problème de consigne
(le modèle n'était pas explicitement invité à cesser de juxtaposer les
résultats), pas un problème de capacité du modèle. Ajouter des exemples
trop proches du cas testé aurait masqué ce diagnostic.

## Limites connues (périmètre assumé)

- Conçu pour un seul animal, pas pour gérer plusieurs dossiers en parallèle
- Suppose que l'ensemble des documents tient dans le contexte d'une seule
  requête (l'approche "option A" ci-dessus) ; à revoir si le volume de
  documents devenait important sur plusieurs années
- Pas de garantie de qualité sur des documents très dégradés ou manuscrits
  (l'extraction repose sur la vision de Claude, pas sur un OCR spécialisé)
- N'importe quel type de compte-rendu vétérinaire peut être ajouté sans
  modification du code (l'ingestion et la génération ne sont pas
  spécifiques à un type d'examen), mais chaque nouveau type de document
  mériterait d'ajouter un ou deux cas dans `eval/qa_testset.json` pour
  vérifier que l'assistant l'exploite correctement

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
 
## Statut

V1 fonctionnelle bout en bout : ingestion des documents (vision), génération
de réponses avec citation des sources, jeu d'évaluation (5 tests, 11 critères).