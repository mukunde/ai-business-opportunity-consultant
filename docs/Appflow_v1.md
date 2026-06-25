# AI Business Opportunity Consultant - Appflow Document v1

## 1. Purpose

This document describes the end-to-end user flows, system states, transitions, and decision paths within the AI Business Opportunity Consultant.

## 2. High-Level User Journey

```text
Dashboard
    |
New Opportunity
    |
Initial Opportunity Submission
    |
Context Discovery Interview
    |
Context Gap Analysis
    |
Opportunity Structuring
    |
Scoring
    |
Recommendation
    |
Report Generation
    |
Opportunity Dashboard
```

## 3. Flow 1 - Create New Opportunity

### User Goal

Start evaluating a new business opportunity.

### Entry Point

```text
Dashboard
    |
[ New Assessment ]
```

### Screen

Create Opportunity

Fields:

- Opportunity Title
- Business Area
- Stakeholder
- Free-text Description

### Example

```text
Title:
Customer Support Automation

Description:
Our support team receives too many emails.
```

### User Action

> [ Start Assessment ]

### System Action

Create Opportunity

```text
Status:
DRAFT
```

### Next State

Interview Session Started

## 4. Flow 2 - Context Discovery Interview

### Purpose

Collect enough context to understand:

- Problem
- Impact
- Constraints
- Data availability

### Entry Condition

Opportunity Created

### State

> INTERVIEW_ACTIVE

### System Behavior

Generate first hypothesis.

### Example

```text
Hypothesis:
Email volume drives business value.
```

### Assistant Question

> How many support emails are received per week?

### User Answer

> 3000

### State Update

Volume = Known

### Opportunity Model Updated

```text
Business Volume:
3000 emails/week
```

### Loop

```text
Question
    |
Answer
    |
State Update
    |
Gap Detection
    |
Next Question
```

## 5. Flow 3 - Context Gap Detection

### Trigger

After every answer.

### System Checks

- Known Facts
- Unknown Facts
- Assumptions
- Contradictions

### Example

Known:

- Volume

Unknown:

- Handling Time

### Gap Generated

```text
Missing:
Average Handling Time
```

### Next Question

> How long does it take to process one email?

## 6. Flow 4 - Contradiction Resolution

### Trigger

Conflicting information detected.

### Example

User says:

> Emails are repetitive.

Later:

> Every email is unique.

### System Response

> I detected potentially conflicting information. Earlier you indicated requests were repetitive. Can you clarify?

### State

> CONFLICT_RESOLUTION

### Exit

Contradiction resolved

## 7. Flow 5 - Context Completeness Evaluation

### Trigger

After every interview cycle.

### Compute

Completeness Score

### Example

```text
Process Understanding: 90%
Business Value: 80%
Data Availability: 40%

Overall:
70%
```

### Decision

#### If Below Threshold

Continue Interview

#### If Above Threshold

Proceed to Structuring

## 8. Flow 6 - Opportunity Structuring

### Goal

Transform conversation into structured business opportunity.

### Inputs

Interview history.

### Outputs

- Problem Statement
- Business Context
- Constraints
- Stakeholders
- Success Metrics
- Data Requirements

### State

> STRUCTURED

## 9. Flow 7 - Scoring

### Trigger

Structured Opportunity Ready.

### State

> SCORING

### Engine Execution

#### ROI

Annual Savings

#### ICE

- Impact
- Confidence
- Ease

#### Risk

- Operational
- Technical
- Data

#### Strategic Alignment

Business Alignment

### Output

Priority Score

## 10. Flow 8 - Recommendation

### Trigger

Scoring Complete.

### Recommendation Types

#### Proceed

- High Value
- High Feasibility

#### Proceed with Conditions

- Data Preparation Required

#### Defer

- Missing Critical Context

#### Do Not Pursue

- Low ROI
- High Risk

### State

> RECOMMENDED

## 11. Flow 9 - Executive Summary Generation

### Trigger

Recommendation Complete.

### Generated Sections

- Business Problem
- Expected Impact
- Recommended Approach
- Risks
- Recommendation

### Output

Executive Summary PDF

## 12. Flow 10 - Detailed Assessment Generation

### Trigger

Executive Summary Generated.

### Sections

- Context Collected
- Assumptions
- Unknowns
- Scoring
- Alternatives
- Recommendation

### Output

Detailed Assessment PDF

## 13. Flow 11 - Opportunity Reopening

### Purpose

Re-evaluate an opportunity later.

### Trigger

Open Existing Opportunity

### State

> REVIEW

### User Actions

- Add Information
- Update Context
- Update Assumptions

### Result

Create New Version

## 14. Versioning Flow

```text
Opportunity v1
       |
Additional Context
       |
Opportunity v2
       |
Rescoring
       |
Updated Recommendation
```

## 15. Complete State Machine

```text
DRAFT
  |
INTERVIEW_ACTIVE
  |
CONFLICT_RESOLUTION (optional)
  |
STRUCTURED
  |
SCORING
  |
RECOMMENDED
  |
EXPORTED
  |
REVIEW
```

## 16. Exceptional Flows

### User Abandons Interview

State:

> PAUSED

### Context Insufficient

State:

> INSUFFICIENT_CONTEXT

Recommendation:

> Gather Additional Information

### Low Confidence

State:

> LOW_CONFIDENCE

System:

> Recommend Expert Review

## 17. Key Product Principle

> Every recommendation must be traceable to the context that produced it.
