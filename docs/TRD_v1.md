# AI Business Opportunity Consultant - TRD v1

## 1. System Overview

### 1.1 Goal

Build an AI system that conducts adaptive interviews with business stakeholders to:

- Discover missing context
- Structure AI opportunities
- Assess feasibility
- Compute ROI / ICE / impact scores
- Generate decision-ready outputs

### 1.2 Core Concept

The system is a:

> Stateful reasoning engine for AI opportunity qualification

It is not a chatbot and not a workflow tool.

### 1.3 Key Design Choice

LangGraph is used for:

- State management
- Interview flow control
- Conditional transitions
- Iterative reasoning loops

## 2. High-Level Architecture

```text
User Input
   |
API Layer (FastAPI)
   |
LangGraph Orchestrator
   |
+------------------------------+
| Interview State Machine      |
|                              |
|  Node 1: Intake              |
|  Node 2: Context Discovery   |
|  Node 3: Gap Analysis        |
|  Node 4: Structuring         |
|  Node 5: Scoring             |
|  Node 6: Recommendation      |
+------------------------------+
   |
Context Store (Postgres / JSON)
   |
Output Generator
   |
UI (optional)
```

## 3. Core Component: Interview Engine (LangGraph)

### 3.1 Design Principle

The interview is:

> Hypothesis-driven, not question-driven

Meaning:

- The system starts with uncertainty
- It generates hypotheses
- It tests them via questions
- It updates state continuously

### 3.2 State Definition

```text
OpportunityState:
    raw_input: str
    problem_statement: str | None

    context:
        business_process: str | None
        volume: int | None
        frequency: str | None
        stakeholders: list[str]

    assumptions: list[str]
    unknowns: list[str]

    feasibility:
        data_available: bool | None
        technical_complexity: int | None

    scoring:
        roi: float | None
        ice: float | None
        impact: float | None
        risk: float | None
        strategic_alignment: float | None

    recommendation: str | None

    conversation_history: list[dict]
```

## 4. LangGraph State Machine

### 4.1 Nodes

#### Node 1 - Intake

- Normalize input
- Detect solution vs problem framing

#### Node 2 - Context Discovery

- Extract missing key variables
- Generate first hypotheses

#### Node 3 - Adaptive Interview Loop (core node)

Responsibilities:

- Ask next best question
- Evaluate completeness
- Decide whether to continue

#### Node 4 - Context Gap Analysis

- List missing required info
- Quantify uncertainty

#### Node 5 - Structuring

Convert conversation into an Opportunity object.

#### Node 6 - Scoring Engine

Compute:

- ROI
- ICE
- Feasibility score
- Risk score

#### Node 7 - Recommendation Engine

Decide:

- Proceed
- Do not proceed
- Defer

### 4.2 Transitions

```text
Intake
  |
Context Discovery
  |
Adaptive Interview Loop
  |  (repeats while more context is needed)
  |
Structuring
  |
Scoring
  |
Recommendation
```

### 4.3 Loop Logic (critical part)

The interview loop continues if:

- Missing context > threshold
- Confidence < 0.7
- Contradictions detected

## 5. Context Engineering Layer

### 5.1 Core Principle

The system explicitly tracks:

- Known facts
- Unknown variables
- Assumptions
- Estimated values

### 5.2 Context Gap Model

- Missing data
- Ambiguous process
- Unvalidated assumptions
- No historical baseline

### 5.3 Output of this layer

- Context completeness score
- List of missing critical inputs
- Uncertainty map

## 6. Scoring Engine Design

### 6.1 Models used

- ROI model (time saved x cost saved)
- ICE (Impact x Confidence x Ease)
- Risk score
- Strategic alignment score

### 6.2 Aggregation

```text
Final Score =
(w1 * ROI) +
(w2 * ICE) +
(w3 * Strategic Alignment) -
(w4 * Risk)
```

### 6.3 Output

- Numeric score
- Explanation
- Confidence level

## 7. LLM Strategy

### 7.1 Multi-step reasoning

Instead of one call:

- Decomposition step
- Extraction step
- Question generation step
- Scoring step

### 7.2 Prompt roles

- Analyst role (context extraction)
- Consultant role (questioning)
- Evaluator role (scoring)
- Synthesizer role (report generation)

## 8. Data Storage

### 8.1 Entities

- Opportunity
- InterviewSession
- MessageTurn
- ContextSnapshot
- ScoreSnapshot
- Recommendation

### 8.2 Key requirement

Everything must be:

> Versioned and replayable

## 9. API Design (high level)

### Endpoints

```text
POST /opportunities
POST /opportunities/{id}/interview
POST /opportunities/{id}/continue
GET  /opportunities/{id}
GET  /opportunities/{id}/report
```

## 10. Failure Modes & Safety

### 10.1 Risks

- Hallucinated metrics
- Overconfident scoring
- Missing business constraints
- Premature recommendation

### 10.2 Mitigation

- Confidence scoring
- Explicit uncertainty representation
- "Insufficient context" state
- Explainable reasoning trace

## 11. Key Architectural Principle

> The system must not be forced to conclude.

This is critical.

If context is insufficient:

- It continues interview
- Or explicitly defers decision

## 12. MVP Scope

- LangGraph state machine
- Single-user flow
- Text interface
- Scoring engine v1
- Structured output JSON
- Executive summary generator

## 13. V1 Scope

- Persistence layer
- Multi-session support
- Versioning
- UI dashboard
- Opportunity comparison

## 14. V2 Scope

- Knowledge graph of opportunities
- Learning from past decisions
- Benchmarking across teams
- Integration with tools (Jira, Notion, CRM)
