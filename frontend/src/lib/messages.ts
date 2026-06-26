/**
 * French translations, keyed by the English source string. Anything not present
 * falls back to the English key, so partial coverage degrades gracefully.
 * Only UI chrome is translated; backend-generated content (interview questions,
 * rationales, reports) follows the backend language.
 */
export const fr: Record<string, string> = {
  // Header
  "AI use-case qualification": "Qualification de cas d'usage IA",

  // Dashboard
  Dashboard: "Tableau de bord",
  "Turn a vague idea into a structured, scored, decision-ready AI opportunity assessment.":
    "Transformez une idée vague en évaluation d'opportunité IA structurée, scorée et prête à décider.",
  "New assessment": "Nouvelle évaluation",
  "Opportunity title": "Titre de l'opportunité",
  "Business area": "Domaine métier",
  "Start assessment": "Démarrer l'évaluation",
  "Creating…": "Création…",
  Opportunities: "Opportunités",
  Title: "Titre",
  Status: "Statut",
  Created: "Créée le",
  "No opportunities yet": "Aucune opportunité pour l'instant",
  "Create one above to start a context-driven interview, then score it and get a recommendation.":
    "Créez-en une ci-dessus pour lancer un entretien guidé par le contexte, puis scorez-la et obtenez une recommandation.",
  "Could not reach the API. Is the backend running on":
    "Impossible de joindre l'API. Le backend tourne-t-il sur",
  "Opportunity created": "Opportunité créée",
  "Failed to create": "Échec de la création",

  // Status badge
  Draft: "Brouillon",
  Interview: "Entretien",
  Structured: "Structurée",
  Scoring: "Scoring",
  Recommended: "Recommandée",
  Review: "Revue",

  // Detail page
  "No business area": "Aucun domaine métier",
  "Opportunity not found.": "Opportunité introuvable.",
  "Back to dashboard": "Retour au tableau de bord",
  Decision: "Décision",

  // Cockpit
  Conversation: "Conversation",
  "Could not load the interview. Is the API running?":
    "Impossible de charger l'entretien. L'API tourne-t-elle ?",
  "Start the qualification interview": "Démarrer l'entretien de qualification",
  "Describe the idea or problem in your own words. The consultant will ask adaptive questions to build the context.":
    "Décrivez l'idée ou le problème avec vos mots. Le consultant posera des questions adaptatives pour construire le contexte.",
  "We receive too many customer support emails…":
    "Nous recevons trop d'e-mails de support client…",
  "Start interview": "Démarrer l'entretien",
  "Starting…": "Démarrage…",

  // Conversation
  "Consultant · AI": "Consultant · IA",
  "Why I'm asking": "Pourquoi je demande",
  "Consultant is thinking…": "Le consultant réfléchit…",
  "Type your answer…": "Tapez votre réponse…",
  "Interview complete. The opportunity is structured and ready to score.":
    "Entretien terminé. L'opportunité est structurée et prête à être scorée.",
  Send: "Envoyer",

  // Context status panel
  "Context completeness": "Complétude du contexte",
  "Business context": "Contexte métier",
  "Process understanding": "Compréhension du process",
  "Data readiness": "Disponibilité des données",
  "ROI readiness": "Préparation du ROI",
  "Missing context": "Contexte manquant",
  "All required context collected.": "Tout le contexte requis est collecté.",
  "Do we understand the business problem and who owns it? Built from business volume and the process owner.":
    "Comprend-on le problème métier et qui en est responsable ? Construit à partir du volume d'activité et du propriétaire du process.",
  "Do we understand how the current process works? Built from the average handling time.":
    "Comprend-on le fonctionnement du process actuel ? Construit à partir du temps de traitement moyen.",
  "Is there data available to build the AI on? Drives feasibility and time to value; its absence raises risk.":
    "Y a-t-il des données disponibles pour construire l'IA ? Détermine la faisabilité et le délai de valeur ; son absence augmente le risque.",
  "Can we estimate the return? Needs both business volume and handling time to size the savings.":
    "Peut-on estimer le retour ? Nécessite le volume d'activité et le temps de traitement pour chiffrer les gains.",

  // Opportunity model panel
  Facts: "Faits",
  Assumptions: "Hypothèses",
  Unknowns: "Inconnues",
  "Nothing established yet.": "Rien d'établi pour l'instant.",
  "None recorded.": "Aucune enregistrée.",
  "None.": "Aucune.",
  Connections: "Connexions",
  Tensions: "Tensions",
  supports: "soutient",
  "depends on": "dépend de",
  requires: "requiert",
  contradicts: "contredit",
  vs: "vs",

  // Decision: scoring
  Impact: "Impact",
  Ease: "Facilité",
  "Strategic align.": "Align. stratégique",
  "Scoring…": "Scoring…",
  "Re-score": "Re-scorer",
  "Score opportunity": "Scorer l'opportunité",
  "Priority score": "Score de priorité",
  Confidence: "Confiance",
  "= overall context completeness. An incomplete interview lowers the score's confidence rather than faking certainty.":
    "= complétude globale du contexte. Un entretien incomplet baisse la confiance du score plutôt que de feindre la certitude.",
  "ICE = Impact × Confidence × Ease (normalized to 0-10). Click any metric below for its rationale and calculation.":
    "ICE = Impact × Confiance × Facilité (normalisé sur 0-10). Cliquez une métrique ci-dessous pour son rationale et son calcul.",
  ROI: "ROI",
  Feasibility: "Faisabilité",
  Risk: "Risque",
  Strategic: "Stratégique",
  "Time to value": "Délai de valeur",
  "How much value would solving this create? Higher means bigger business impact. Your judgement, 1 to 10.":
    "Quelle valeur créerait la résolution ? Plus haut = impact métier plus fort. Votre jugement, de 1 à 10.",
  "How easy is it to deliver? Higher means simpler to build and roll out. Feeds the ICE score. 1 to 10.":
    "Quelle facilité de livraison ? Plus haut = plus simple à construire et déployer. Alimente le score ICE. De 1 à 10.",
  "How well does it fit the company strategy and priorities? 1 to 10.":
    "À quel point cela colle-t-il à la stratégie et aux priorités ? De 1 à 10.",
  "Can we size the return? Driven by whether business volume and handling time are known, the inputs an ROI estimate needs.":
    "Peut-on chiffrer le retour ? Dépend de la connaissance du volume d'activité et du temps de traitement, les entrées d'une estimation de ROI.",
  "Analyst-judged business impact of solving this problem.":
    "Impact métier de la résolution, évalué par l'analyste.",
  "Is there data to build on? High when data availability is known.":
    "Y a-t-il des données pour construire ? Élevé quand la disponibilité des données est connue.",
  "Rises with missing context and missing data. Lower is better; it is subtracted in the final score.":
    "Augmente avec le contexte et les données manquants. Plus bas = mieux ; il est soustrait dans le score final.",
  "Analyst-judged fit with strategy.":
    "Adéquation avec la stratégie, évaluée par l'analyste.",
  "Proxied by feasibility: more data-ready means value lands sooner.":
    "Approximé par la faisabilité : plus de données prêtes = valeur plus rapide.",

  // Decision: recommendation
  Recommendation: "Recommandation",
  Proceed: "Avancer",
  "Proceed with conditions": "Avancer sous conditions",
  Defer: "Différer",
  "Do not pursue": "Ne pas poursuivre",
  "Turn the score into a decision.": "Transformez le score en décision.",
  "Score the opportunity first.": "Scorez d'abord l'opportunité.",
  "Deciding…": "Décision…",
  "Re-decide": "Re-décider",
  "Get recommendation": "Obtenir une recommandation",
  confidence: "confiance",

  // Decision: report
  Report: "Rapport",
  "Generating…": "Génération…",
  "Regenerate report": "Régénérer le rapport",
  "Generate report": "Générer le rapport",
  "Download PDF": "Télécharger le PDF",
  "Get a recommendation first.": "Obtenez d'abord une recommandation.",
  "Executive summary": "Résumé exécutif",
  "Detailed assessment": "Évaluation détaillée",
  "Request failed": "Échec de la requête",
};
