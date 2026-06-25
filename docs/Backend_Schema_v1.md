# Backend Schema v1

## Core Entities

### Opportunity

- id
- title
- raw_input
- problem_statement
- status
- created_at
- updated_at

### InterviewSession

- id
- opportunity_id
- status
- started_at
- completed_at

### MessageTurn

- id
- interview_session_id
- role
- content
- created_at

### ContextSnapshot

- id
- opportunity_id
- known_facts
- unknowns
- assumptions
- estimated_values
- completeness_score
- created_at

### ScoreSnapshot

- id
- opportunity_id
- roi
- ice
- impact
- risk
- strategic_alignment
- confidence
- created_at

### Recommendation

- id
- opportunity_id
- decision
- rationale
- next_steps
- created_at

