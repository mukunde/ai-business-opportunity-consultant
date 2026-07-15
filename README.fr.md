# AI Business Opportunity Consultant

[![English](https://img.shields.io/badge/English-6E6662?style=for-the-badge)](README.md)
[![Français](https://img.shields.io/badge/Fran%C3%A7ais-8A1C34?style=for-the-badge)](README.fr.md)

Imaginez un consultant IA qui interroge vos équipes, comprend votre contexte
métier, évalue les opportunités d'automatisation, et produit une recommandation
structurée, prête à être mise en oeuvre.

**AI Business Opportunity Consultant** aide les organisations à découvrir,
qualifier, prioriser et valider leurs opportunités IA avant d'engager un effort
d'ingénierie. C'est un système de raisonnement à état : entretien adaptatif,
context engineering explicite, scoring guidé par l'opérateur, recommandation,
revue humaine, et génération d'un dossier de reprise.

L'idée directrice : une opportunité IA ne mérite pas d'être construite parce
qu'un modèle en est capable. Elle le mérite quand le contexte est assez complet
pour décider, et qu'un humain a décidé. Le système rend ce contexte explicite, et
garde l'humain dans la boucle à chaque étape.

## Démo produit

🎥 **[Démonstration vidéo de bout en bout (Loom)](https://www.loom.com/share/f655345c29024669ac4d07ba077a6989)** :
d'un flux de mails clients trié par un workflow n8n, jusqu'aux opportunités
détectées, la qualification, le scoring, la revue humaine, le portefeuille et le
dossier de reprise généré. L'interface est en français ; l'API et le code sont en
anglais.

## Pourquoi ce projet existe

- Les organisations identifient beaucoup d'idées IA mais peinent à les prioriser.
- Les projets échouent parce que le contexte métier est incomplet quand la
  construction démarre.
- Les équipes construisent avant d'avoir validé la valeur, les données et le
  responsable du processus.
- Métier et technique n'ont pas de cadre d'évaluation commun.

L'essentiel du coût d'une initiative IA ratée est dépensé avant que quiconque ne
remette la prémisse en question. Ce système déplace ce questionnement en amont,
de manière peu coûteuse et systématique.

## Ce que fait le système

```text
signaux / idée brute
        |
   Découverte           faire émerger des opportunités candidates depuis des signaux
        |
   Entretien            questionnement adaptatif jusqu'à complétude du contexte
        |
   Context graph        faits, inconnues, hypothèses, liens typés, contradictions
        |
   Scoring              critères guidés, opérés par l'humain, priorité calculée
        |
   Recommandation       un verdict proposé, avec sa justification
        |
   Revue humaine        approuver ou rejeter (la décision reste humaine)
        |
   Livrables            dossier de reprise généré à la demande
```

En parallèle du pipeline : une vue **portefeuille** qui place les opportunités
dans un quadrant de priorité, et un **versionnage** qui fige un instantané de
l'opportunité à chaque transition significative.

## Exemple : d'un signal métier à une opportunité IA

Le scénario de la vidéo de démo, de bout en bout :

```text
Signaux métier (issus du workflow de triage des mails) :
  demandes de devis répétées, relances, réclamations avec références commande
        |
Découverte :
  opportunité candidate détectée : "Génération automatisée de devis"
        |
Promotion + entretien :
  le consultant collecte les quatre informations de contexte requises :
  volume d'activité, temps de traitement, disponibilité des données, responsable
        |
Context graph :
  faits (chacun adossé à une preuve), hypothèses, inconnues restantes,
  relations typées et contradictions entre eux
        |
Scoring (humain, guidé) :
  l'opérateur note l'impact, la faisabilité et l'alignement stratégique sur des
  critères explicites ; le moteur calcule ROI, faisabilité, risque et priorité
        |
Recommandation :
  verdict proposé avec justification, par exemple "Quick Win : fort impact,
  données disponibles"
        |
Revue humaine :
  approuvée (ou rejetée), enregistrée avec la justification du relecteur
        |
Livrables (à la demande) :
  note de synthèse, roadmap d'implémentation, PRD, TRD, cadrage UI/UX,
  schéma backend, appflow : un dossier prêt pour l'équipe de réalisation
```

## Un seul workflow, deux dépôts

La découverte n'a pas besoin d'une conversation humaine pour démarrer. Ce dépôt
est la moitié aval d'une chaîne complète ; la moitié amont vit dans
[`ai-mail-triage-poc`](https://github.com/mukunde/ai-mail-triage-poc) :

```text
ai-mail-triage-poc                          ce dépôt
------------------                          --------
mails clients entrants                      session de découverte
  -> triage n8n + Claude                      -> opportunités candidates
     (classer, extraire, router)              -> entretien de qualification
  -> besoins clients extraits                 -> scoring, recommandation
     poussés comme signaux  ------------->    -> revue humaine
                                              -> portefeuille + dossier de reprise
```

L'idée derrière ce lien : les mails entrants expriment des frictions réelles et
récurrentes. Au lieu de seulement les router, la chaîne les **transforme en
candidats qualifiés à l'automatisation**. Le triage règle le flux ; la
qualification exploite le gisement.

Le pont est du simple HTTP, donc n'importe quel système amont peut alimenter les
signaux de la même façon :

```text
POST /discovery                      créer une session
POST /discovery/{id}/signal          pousser un signal métier
POST /discovery/{id}/detect          lancer la détection sur les signaux
GET  /discovery/{id}/opportunities   lire les candidates
```

## Ce qui rend ce projet différent

| Assistants IA génériques | AI Business Opportunity Consultant |
| --- | --- |
| Répondent à des questions | Construisent un contexte de décision |
| Conversations sans état | Cycle de vie persistant de l'opportunité |
| Le LLM décide de tout | Règles déterministes + raisonnement LLM, séparés à dessein |
| Génèrent du texte | Soutiennent des décisions métier validées |
| Aucune traçabilité | Preuves, versionnage, piste d'audit |
| Retour humain après génération | Validation humaine comme point de passage obligé |

## Comment ça marche

**L'entretien est un moteur à un tour, pas un chatbot.** Une invocation LangGraph
traite exactement un tour utilisateur : intégrer la réponse, recalculer l'écart de
contexte, puis soit poser la question suivante, soit structurer l'opportunité. La
boucle multi-tours vit entre les appels HTTP, la base de données faisant foi.
Voir `backend/app/interview/graph.py`.

**Le context engineering est explicite.** Le consultant doit remplir un ensemble
fixe d'informations requises (volume d'activité, temps de traitement,
disponibilité des données, responsable du processus) avant d'avoir le droit de
structurer quoi que ce soit. L'analyse d'écart est du code déterministe, pas un
jugement du modèle : la complétude est simplement la fraction d'informations
remplies.

**Le context graph est une projection.** À chaque tour, l'état de l'entretien est
projeté en noeuds persistants (FACT / UNKNOWN / ASSUMPTION), chaque fait étant
adossé à une preuve. La projection est idempotente : on efface et on reconstruit,
donc aucun noeud périmé ne survit. Une fois le contexte complet, une unique passe
LLM infère les liens typés (SUPPORTS / DEPENDS_ON / REQUIRES) et les
contradictions entre les noeuds. Le modèle ne voit jamais les identifiants de la
base ; les noeuds reçoivent des clés opaques.

**Un graphe n'a pas besoin d'une base graphe.** Des noeuds et une table d'arêtes
typées dans Postgres suffisent à cette volumétrie, évitent d'ajouter une
technologie, et restent lisibles par quiconque connaît SQL. Voir
[ADR 0001](docs/ADR/0001-context-graph-storage.md).

## Principes de conception

- Logique déterministe là où la justesse compte ; raisonnement LLM uniquement là
  où il y a de l'ambiguïté.
- La validation humaine reste le point de décision final.
- Le contexte est stocké comme un actif métier réutilisable, avec ses preuves.
- Chaque transition d'une opportunité est auditable (versionnage par instantané).
- L'état en base fait foi ; le moteur est reconstruit depuis la base à chaque tour.
- Les livrables sont générés à la demande, jamais en silence.

## Architecture technique

```text
              Frontend Next.js (interface en français)
                          |
                    Backend FastAPI
                          |
    ------------------------------------------------
    |           |            |           |          |
Découverte   Entretien    Scoring     Revue     Reporting
    |           |            |           |          |
    ------------------------------------------------
                          |
                   Couche contexte
        (projection + enrichissement sémantique LLM)
                          |
                  PostgreSQL (Alembic)
                          |
                 Couche fournisseur LLM
             API Claude  /  stub déterministe
```

## Structure du dépôt

```text
ai-business-opportunity-consultant/
├── backend/                 FastAPI, SQLAlchemy 2.0, Alembic, LangGraph
│   ├── app/
│   │   ├── api/routes/      context, discovery, interview, opportunities,
│   │   │                    recommendation, reporting, review, scoring, versions
│   │   ├── interview/       machine à états LangGraph, noeuds, prompts, client LLM
│   │   ├── context/         projection (déterministe) + enrichissement (LLM)
│   │   ├── discovery/       phase amont : des signaux aux opportunités candidates
│   │   ├── scoring/         moteur de scoring
│   │   ├── recommendation/  verdict + justification
│   │   ├── review/          approbation / rejet humain
│   │   ├── reporting/       rapports et livrables à la demande
│   │   ├── versioning/      instantanés d'opportunité
│   │   ├── dashboard/       agrégation du portefeuille
│   │   └── models/          modèles SQLAlchemy
│   └── alembic/versions/    migrations 0001 à 0011
├── frontend/                Next.js App Router, TanStack Query, shadcn/ui
├── docs/
│   ├── ADR/                 décisions d'architecture
│   ├── PRD_v1.md            exigences produit
│   ├── TRD_v1.md            exigences techniques
│   ├── UX_UI_Design_v1.md
│   ├── Appflow_v1.md
│   ├── Backend_Schema_v1.md
│   └── Implementation_Plan_v1.md
├── docker-compose.yml       Postgres local
├── start-demo.ps1           lancement de la stack locale en une commande (Windows)
└── README.md
```

## Démarrage rapide

Prérequis : Docker Desktop, Python avec [uv](https://docs.astral.sh/uv/), Node.js.

```powershell
# 1. Configurer le backend
cd backend
cp .env.example .env      # puis renseigner ANTHROPIC_API_KEY, ou LLM_PROVIDER=fake

# 2. Tout démarrer (Postgres, migrations, API, frontend)
cd ..
./start-demo.ps1
```

Le script démarre Postgres, attend son health check, applique les migrations en
attente, puis ouvre l'API et le frontend chacun dans sa fenêtre.

- Frontend : http://localhost:3000
- Documentation de l'API : http://localhost:8000/docs

Options : `-NoFrontend` (base et API seulement), `-SkipMigrations`.

### Essayer la démo

1. Créer une opportunité (ou alimenter des signaux via l'API de découverte).
2. Répondre aux questions de l'entretien adaptatif, regarder la complétude monter.
3. Examiner le contexte extrait : faits, hypothèses, inconnues, contradictions.
4. Scorer l'opportunité sur les critères guidés.
5. Lire la recommandation, puis l'approuver ou la rejeter en tant que relecteur.
6. Générer le dossier de reprise et parcourir l'historique des versions.

### Démarrage manuel

```powershell
docker compose up -d db

cd backend
uv run alembic upgrade head
uv run uvicorn app.main:app --host 0.0.0.0 --reload

# dans un autre terminal
cd frontend
npm run dev
```

L'API écoute sur `0.0.0.0` afin qu'un client conteneurisé (par exemple le
workflow de triage n8n) puisse la joindre via `host.docker.internal:8000`. Une
écoute limitée au loopback ne le permet pas.

### Fonctionner sans clé API

Mettre `LLM_PROVIDER=fake` pour dérouler tout le flux hors ligne sur un stub
déterministe : sans clé, sans coût, et avec des tests reproductibles.

## Configuration

Les réglages du backend sont lus depuis l'environnement ou `backend/.env`
(voir `backend/app/config.py`) :

| Variable | Défaut | Rôle |
| --- | --- | --- |
| `DATABASE_URL` | Postgres du compose local | chaîne de connexion SQLAlchemy |
| `LLM_PROVIDER` | `claude` | `claude` ou `fake` (stub hors ligne) |
| `ANTHROPIC_API_KEY` | aucune | requise quand `LLM_PROVIDER=claude` |
| `LLM_MODEL` | `claude-opus-4-8` | identifiant du modèle |
| `CONTEXT_COMPLETENESS_THRESHOLD` | `1.0` | seuil à partir duquel l'entretien peut structurer |
| `CORS_ORIGINS` | `http://localhost:3000` | origines navigateur autorisées |

Une variable supplémentaire vit dans un `.env` **à la racine**, lue par docker
compose et non par l'application : `POSTGRES_HOST_PORT` (défaut `5432`) fixe le
port hôte de la base du compose, utile quand un Postgres natif occupe déjà 5432.

Ne jamais committer `.env`. Il est dans le `.gitignore`.

## À qui ça s'adresse

- Équipes d'innovation et Labs IA qualifiant des idées de cas d'usage avant
  prototypage.
- Cabinets de conseil menant des évaluations d'opportunités IA.
- Équipes en entreprise priorisant des initiatives d'automatisation.
- Équipes produit validant des idées de produits IA face au contexte réel.

## État du projet

Implémenté :

- ✅ Pipeline de découverte (par entretien ou par signaux)
- ✅ Entretien de qualification adaptatif (LangGraph)
- ✅ Context graph avec preuves, liens sémantiques et contradictions
- ✅ Scoring guidé par l'opérateur et priorité calculée
- ✅ Recommandation avec justification
- ✅ Workflow de revue humaine (approuver / rejeter)
- ✅ Tableau de bord portefeuille (quadrant de priorité)
- ✅ Versionnage des opportunités par instantané
- ✅ Livrables à la demande (note de synthèse, roadmap, PRD, TRD, UI/UX, schéma, appflow)
- ✅ Ingestion amont par triage de mails (workflow n8n, dépôt séparé)

À venir :

- authentification de production ;
- multi-tenant ;
- métriques d'évaluation systématiques pour les étapes LLM ;
- d'autres connecteurs amont (ticketing, CRM) alimentant la découverte.

## Décisions d'architecture

- [ADR 0001](docs/ADR/0001-context-graph-storage.md) stockage du context graph
- [ADR 0002](docs/ADR/0002-llm-semantic-enrichment.md) enrichissement sémantique par le LLM
- [ADR 0003](docs/ADR/0003-opportunity-versioning-snapshot.md) versionnage par instantané
- [ADR 0004](docs/ADR/0004-discovery-phase-upstream.md) phase de découverte en amont
- [ADR 0005](docs/ADR/0005-on-demand-deliverables.md) livrables à la demande
- [ADR 0006](docs/ADR/0006-human-review-decision.md) décision par revue humaine
- [ADR 0007](docs/ADR/0007-data-readiness-assessed-not-presence.md) disponibilité des données évaluée, pas simplement présente

## Documents

- [PRD v1](docs/PRD_v1.md)
- [TRD v1](docs/TRD_v1.md)
- [UX/UI Design v1](docs/UX_UI_Design_v1.md)
- [Appflow v1](docs/Appflow_v1.md)
- [Backend Schema v1](docs/Backend_Schema_v1.md)
- [Implementation Plan v1](docs/Implementation_Plan_v1.md)
