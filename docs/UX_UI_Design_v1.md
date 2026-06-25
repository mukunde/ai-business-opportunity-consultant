# AI Business Opportunity Consultant - UX/UI Design Document v1

## 1. Design Principles

### Principle 1 - Context Must Be Visible

Le systeme ne doit jamais donner l'impression de raisonner dans une boite noire.

L'utilisateur doit voir :

- Ce qui est connu
- Ce qui est suppose
- Ce qui manque
- Ce qui influence la decision

### Principle 2 - The System Is a Consultant

L'interface ne doit pas ressembler a ChatGPT.

Elle doit ressembler a :

- Un atelier de cadrage
- Un consultant qui structure un probleme
- Un tableau de decision

### Principle 3 - Decision Support First

La conversation n'est pas le produit.

> La decision est le produit.

La conversation est simplement un mecanisme de collecte de contexte.

## 2. Information Architecture

### Main Navigation

```text
Dashboard
|
+-- Opportunities
+-- New Assessment
+-- Reports
+-- Settings
```

## 3. Core Screen: Opportunity Assessment

C'est l'ecran principal.

### Layout

```text
+------------------------------------------------------+
| Header                                               |
+------------------------------------------------------+

+--------------+--------------------+-----------------+
| Context      | Conversation       | Opportunity     |
| Status       |                    | Model           |
+--------------+--------------------+-----------------+
```

## 4. Left Panel - Context Status

Largeur approximative : 20%.

### Goal

Afficher :

- Progression
- Qualite du contexte
- Zones manquantes

### Components

#### Context Completeness

```text
Context Completeness
[#######-------] 63%
```

#### Confidence Score

```text
Confidence
71%
```

#### Missing Context

```text
Missing Context
[ ] Process Owner
[ ] Historical Data
[ ] Cost Baseline
[ ] KPI Definition
```

#### Risk Indicators

- ROI Estimation Uncertain
- No Historical Dataset
- Stakeholder Missing

## 5. Center Panel - Consultant Conversation

Largeur approximative : 50%.

### Goal

Conduire l'interview adaptative.

### Assistant Message

> You mentioned receiving many customer support emails. Can you estimate how many emails are received per week?

### User Response

> Around 3000 emails.

### Consultant Reasoning (collapsed)

#### Why I'm asking

Email volume directly impacts potential business value and ROI estimation.

### Suggested Answers

- 300-500
- 500-1000
- 1000-3000
- 3000+

Pour accelerer les ateliers.

## 6. Right Panel - Live Opportunity Model

Largeur approximative : 30%.

### Goal

Afficher le raisonnement construit.

### Model Content

```text
Problem Statement
Customer Support Email Overload

Business Impact
High

Opportunity Type
Customer Support Automation
```

### Candidate Solutions

- AI Classification
- Workflow Automation
- Knowledge Retrieval

### Assumptions

- Requests are repetitive
- Historical emails exist
- Categorization is feasible

### Unknowns

- Current resolution time
- Automation rate
- Data quality

## 7. Scoring Screen

Accessible des que :

> Context Completeness > Threshold

### Layout

```text
+-------------------------------+
| Opportunity Summary           |
+-------------------------------+

+----------+----------+---------+
| ROI      | Impact   | Risk    |
+----------+----------+---------+
```

### Example

#### ROI

Estimated Annual Savings: EUR 210,000

#### ICE

- Impact: 8
- Confidence: 7
- Ease: 6
- ICE Score: 336

#### Strategic Alignment

9/10

## 8. Recommendation Screen

### Recommendation Card

```text
RECOMMENDATION

Proceed
```

### Reasoning

- High business impact
- Strong ROI potential
- Moderate implementation effort
- Data availability confirmed

### Confidence

```text
Confidence
82%
```

## 9. Executive Summary Export

Format :

- 1 page
- Decision-ready
- Business audience

Sections :

- Opportunity
- Business Problem
- Proposed Direction
- Expected Impact
- Risks
- Recommendation

## 10. Detailed Assessment Export

Format :

- 5-10 pages

Sections :

- Context Collected
- Assumptions
- Missing Information
- Scoring
- Alternatives Considered
- Recommendation

## 11. Opportunity Dashboard

Liste des opportunites.

### Columns

- Title
- Status
- Priority Score
- Business Value
- Feasibility
- Owner
- Last Updated

### Visual Priority

- Green: Quick Win
- Yellow: Strategic Bet
- Red: Low Priority

## 12. Design Philosophy

L'utilisateur ne doit jamais avoir l'impression de parler a un chatbot.

Il doit avoir l'impression :

> Qu'un consultant IA est en train de construire progressivement un business case avec lui.
