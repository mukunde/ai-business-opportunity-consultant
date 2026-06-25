# AI Business Opportunity Consultant - Backend Schema v1

## Philosophy

Everything revolves around context.

Every recommendation, score, assumption and decision must be traceable to context.

## Entity Relationship Diagram

```text
Opportunity
│
├── Versions
│
├── Interview Sessions
│
├── Context Graph
│    ├── Facts
│    ├── Unknowns
│    ├── Assumptions
│    ├── Contradictions
│    └── Evidence
│
├── Scores
│
├── Recommendations
│
└── Reports
```

## 1. Opportunity

### Purpose

Represents a business opportunity being evaluated.

### Fields

```yaml
Opportunity:
  id: UUID
  title: string
  business_area: string
  status:
    - DRAFT
    - INTERVIEW_ACTIVE
    - STRUCTURED
    - SCORING
    - RECOMMENDED
    - REVIEW
  current_version: integer
  owner_id: UUID
  created_at: datetime
  updated_at: datetime
```

## 2. OpportunityVersion

### Purpose

Snapshot of the opportunity at a point in time.

### Fields

```yaml
OpportunityVersion:
  id: UUID
  opportunity_id: UUID
  version_number: integer
  summary: text
  created_at: datetime
  created_by: UUID
```

## 3. InterviewSession

### Purpose

Represents a qualification workshop.

### Fields

```yaml
InterviewSession:
  id: UUID
  opportunity_id: UUID
  status:
    - ACTIVE
    - PAUSED
    - COMPLETED
  started_at: datetime
  completed_at: datetime
```

## 4. ConversationTurn

### Purpose

Store every interaction.

### Fields

```yaml
ConversationTurn:
  id: UUID
  session_id: UUID
  role:
    - USER
    - CONSULTANT
  message: text
  reasoning_trace: text
  created_at: datetime
```

## 5. Context Graph

The most important object in the system.

### Why?

The system reasons about context.

Therefore context must be modeled explicitly.

### 5.1 ContextNode

```yaml
ContextNode:
  id: UUID
  opportunity_id: UUID
  type:
    - FACT
    - UNKNOWN
    - ASSUMPTION
    - CONSTRAINT
    - KPI
    - RISK
    - STAKEHOLDER
  label: string
  description: text
  confidence: float
  source_id: UUID
  created_at: datetime
```

#### Example

```yaml
FACT:
  label: Email Volume
  value: 3000/week

UNKNOWN:
  label: Average Handling Time

ASSUMPTION:
  label: Requests are repetitive
```

### 5.2 ContextRelationship

Relationships between context elements.

#### Fields

```yaml
ContextRelationship:
  id: UUID
  source_node_id: UUID
  target_node_id: UUID
  relation_type:
    - SUPPORTS
    - CONTRADICTS
    - DEPENDS_ON
    - REQUIRES
```

#### Example

```text
Historical Dataset
     SUPPORTS
Classification AI
```

## 6. Evidence

### Purpose

Stores supporting evidence.

### Fields

```yaml
Evidence:
  id: UUID
  opportunity_id: UUID
  type:
    - USER_STATEMENT
    - DOCUMENT
    - METRIC
    - CALCULATION
  content: text
  confidence: float
```

### Example

```text
3000 emails/week
```

becomes:

```yaml
Evidence:
  type: USER_STATEMENT
```

## 7. Contradiction

### Purpose

Track conflicting information.

### Fields

```yaml
Contradiction:
  id: UUID
  opportunity_id: UUID
  node_a_id: UUID
  node_b_id: UUID
  status:
    - OPEN
    - RESOLVED
  resolution_note: text
```

### Example

```text
Requests are repetitive
```

vs

```text
Every request is unique
```

## 8. Context Completeness

This is a first-class object.

Not a derived UI value.

### Fields

```yaml
ContextCompleteness:
  id: UUID
  opportunity_id: UUID
  business_context_score: float
  process_understanding_score: float
  data_readiness_score: float
  roi_readiness_score: float
  overall_score: float
```

## 9. Scoring

### Purpose

Store scoring snapshots.

### Fields

```yaml
ScoreSnapshot:
  id: UUID
  opportunity_id: UUID
  version_id: UUID
  roi_score: float
  impact_score: float
  feasibility_score: float
  risk_score: float
  strategic_alignment_score: float
  time_to_value_score: float
  final_score: float
  confidence: float
```

## 10. Recommendation

### Purpose

Store system decisions.

### Fields

```yaml
Recommendation:
  id: UUID
  opportunity_id: UUID
  score_snapshot_id: UUID
  type:
    - PROCEED
    - PROCEED_WITH_CONDITIONS
    - DEFER
    - DO_NOT_PURSUE
  rationale: text
  confidence: float
```

## 11. Executive Summary

```yaml
ExecutiveSummary:
  id: UUID
  opportunity_id: UUID
  version_id: UUID
  markdown_content: text
  generated_at: datetime
```

## 12. Detailed Assessment

```yaml
DetailedAssessment:
  id: UUID
  opportunity_id: UUID
  version_id: UUID
  markdown_content: text
  generated_at: datetime
```

## 13. Audit Trail

Critical for enterprise credibility.

```yaml
AuditEvent:
  id: UUID
  opportunity_id: UUID
  actor:
    - USER
    - SYSTEM
  event_type: string
  payload: json
  created_at: datetime
```
