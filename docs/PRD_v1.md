# AI Business Opportunity Consultant - PRD v1

## 1. Product Vision

Enable innovation and AI teams to reliably identify, qualify, and prioritize AI opportunities by transforming vague business ideas into structured, context-rich, decision-ready opportunity assessments.

### Core Insight

Most AI initiatives fail not because of model limitations, but because of insufficient or implicit business context at the time of decision-making.

### Product Thesis

> If you cannot fully describe the context of a business problem, you cannot reliably evaluate whether AI is the right solution.

## 2. Problem Statement

Innovation and transformation teams receive a continuous stream of AI-related ideas from business stakeholders.

### However

- Ideas are expressed as solutions, not problems
- Critical context is missing (volume, process, constraints, data)
- Feasibility is assessed too late
- ROI is estimated arbitrarily
- Prioritization is inconsistent across teams

### Result

- Too many low-value POCs are launched
- High-value opportunities are missed
- AI investments are poorly allocated

## 3. Product Goals

### Primary Goal

Reduce the number of low-value or non-feasible AI POCs launched.

### Secondary Goals

- Improve quality of AI opportunity framing
- Standardize evaluation across teams
- Reduce time spent in manual qualification
- Improve alignment between business and AI teams

## 4. Non-Goals

- Building an execution agent for AI solutions
- Automating implementation of AI systems
- Replacing product managers or innovation teams
- Producing final production architecture designs

## 5. Target Users

### Primary Users

- AI Labs
- Innovation Teams
- Digital Transformation Teams

### Secondary Users

- Business stakeholders submitting ideas
- Product owners
- Process owners

## 6. Core Product Concept

### Opportunity as a Living Object

Each AI opportunity is structured and versioned:

- Problem Statement
- Business Context
- Assumptions
- Constraints
- Data Availability
- Business Value
- Feasibility
- Risk Profile
- ROI Estimation
- Recommendations
- Version History
- Decision Log

## 7. Core Workflow

### Step 1 - Input (Unstructured Idea)

User submits a vague or solution-oriented idea:

> "We receive too many customer support emails."

### Step 2 - Interview Engine (Context Discovery)

The system launches a dynamic consultant-like interview:

- Adaptive questioning
- Hypothesis-driven reasoning
- Missing context detection
- Progressive clarification

#### Example

- "How many emails per day do you receive?"
- "What is the average handling time per email?"
- "Are tickets already categorized?"

### Step 3 - Context Gap Analysis

The system identifies missing or uncertain information:

- Missing volume data
- Unclear process structure
- No labeled dataset
- Unknown ownership

### Step 4 - Opportunity Structuring

The system converts the conversation into a structured object:

- Problem type
- AI applicability
- Required data
- Constraints
- Assumptions

### Step 5 - Scoring Engine

The opportunity is evaluated using multiple dimensions:

- ROI (Return on Investment)
- ICE (Impact / Confidence / Ease)
- Business Value
- Technical Feasibility
- Risk Level
- Strategic Alignment
- Time-to-Value

### Step 6 - Recommendation Layer

The system outputs a decision:

- Proceed
- Do not proceed
- Defer (missing context)

And suggests the best approach:

- AI solution
- Automation
- Data product
- Process redesign

### Step 7 - Deliverables

1. **Executive Summary**: 1-page decision-ready output
2. **Detailed Assessment**: structured breakdown of all dimensions
3. **Optional Roadmap**: phased implementation plan

## 8. Key Differentiator - Interview Engine

The core innovation is not scoring.

It is context discovery before evaluation.

### Behavior

Instead of a static form:

- The system behaves like a consultant
- It asks adaptive questions
- It challenges assumptions
- It refines understanding iteratively

### Example

User:

> "We receive too many emails."

System:

- "How many per day?"
- "How long does it take to process one?"
- "Is there categorization today?"

Then:

- Estimates workload
- Identifies bottlenecks
- Evaluates feasibility

## 9. Context Engineering Layer

The system explicitly models:

- Known information
- Unknowns
- Assumptions
- Estimation gaps

### Key Principle

> AI systems should not evaluate incomplete context as if it were complete.

## 10. Scoring System

The system combines:

- ROI model (cost/time-based estimation)
- ICE scoring
- Value vs Feasibility matrix

Outputs:

- Numeric priority score
- Qualitative explanation
- Confidence level

## 11. Outputs

1. **Executive Summary**: decision-oriented, non-technical, readable by business teams
2. **Detailed Assessment**: full breakdown of reasoning, structured scoring, assumptions
3. **Optional Roadmap**: implementation phases, dependencies, risks

## 12. MVP Scope

- Text input interface
- LLM-driven interview engine
- Structured JSON output
- Scoring engine (ROI + ICE)
- Executive summary generation

## 13. V1 Scope

- Opportunity persistence
- Versioning system
- Decision tracking
- Multi-user collaboration
- History of interviews

## 14. V2 Scope

- Knowledge graph of opportunities
- Benchmarking across teams
- Learning from past decisions
- Integration with ticketing / CRM tools

## 15. Risks

- Hallucinated or estimated data
- Overconfidence in scoring
- User distrust in AI recommendations
- Interview fatigue
- Misinterpretation of vague inputs

### Mitigation

- Explicit uncertainty modeling
- Confidence scores
- Explanation of reasoning
- "Insufficient context" mode

## 16. Key Product Principle

> The system must be allowed to say: "We don't know yet."

## 17. Success Metrics

- Reduction in low-value AI POCs
- Improved ROI accuracy of selected projects
- Reduced time spent in qualification phase
- Increased alignment between stakeholders and AI teams
- Adoption rate in innovation teams
