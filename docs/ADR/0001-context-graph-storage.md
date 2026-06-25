# ADR 0001 - Context graph storage: relational adjacency in Postgres over a graph database

- Status: Accepted
- Date: 2026-06-26
- Deciders: Gael Mukunde

## Context

The system reasons about context. The Backend Schema (v1) models a context graph
as the central object: typed nodes (FACT, UNKNOWN, ASSUMPTION, CONSTRAINT, KPI,
RISK, STAKEHOLDER), typed relationships (SUPPORTS, CONTRADICTS, DEPENDS_ON,
REQUIRES), supporting Evidence, Contradictions, and a Context Completeness score.

Epic 3 persists this graph. The question is how to store it. The headline choice
is between a dedicated graph database (e.g. Neo4j) and a relational encoding in
the Postgres instance we already run.

Constraints that shape the decision:

- The MVP is single-operator with a EUR 0 / low-cost target. Adding a second
  datastore means another service to run, secure, back up, and pay for.
- The graph is small and opportunity-scoped: tens of nodes per opportunity, not a
  global, densely connected knowledge graph.
- Queries are local: "all nodes for this opportunity", "the contradictions for
  this opportunity", "completeness for this version". No multi-hop traversal or
  global graph analytics is required for the MVP, V1, or the portfolio version.
- The Implementation Plan explicitly defers a distributed knowledge graph to
  Phase 4 (Enterprise), out of MVP scope.

## Decision

Store the context graph **relationally in the existing Postgres database**, as an
adjacency-list / edge-table encoding:

- `context_nodes` - one row per node, carrying `type`, `label`, `description`,
  `confidence`, and `source_id` (the Evidence that produced it).
- `context_relationships` - an edge table with `source_node_id`,
  `target_node_id`, `relation_type`.
- `evidence`, `contradictions`, `context_completeness` - the supporting entities
  from the schema.

No dedicated graph database is introduced for the MVP, V1, or the portfolio
version. A distributed / cross-opportunity knowledge graph remains a Phase 4
concern and is explicitly out of scope here.

## Rationale

- **Zero new infrastructure.** Reuses the Postgres we already provision via
  docker-compose and Terraform-style RBAC, honouring the cost target.
- **Sufficient for the workload.** Opportunity-scoped graphs are small and queried
  locally; indexed foreign keys on `opportunity_id` and the edge endpoints make
  these reads trivial. A graph DB's traversal strengths are not exercised.
- **One source of truth, transactional.** The context graph is written in the same
  transaction as the interview turn that produced it, so the graph never drifts
  from the conversation. Replayability (a TRD requirement) stays simple.
- **Schema fidelity.** The Backend Schema already describes nodes + typed edges,
  which is exactly an adjacency list. The relational model mirrors the spec 1:1.

## Consequences

Positive:

- No second datastore to operate; lower TCO and attack surface.
- Standard SQL, migrations (Alembic), and the existing ORM apply unchanged.
- The graph is a projection of interview state and can be rebuilt idempotently.

Negative / trade-offs:

- Multi-hop / variable-depth traversal would need recursive CTEs rather than a
  native graph query language. Acceptable: the MVP needs no such queries.
- Cross-opportunity learning (find similar opportunities across the corpus) is not
  served by this design. That is the Phase 4 knowledge-graph concern, deliberately
  deferred.

## Notes

Semantic relationship inference (which FACT SUPPORTS which approach) and
contradiction detection (Appflow flow 4: "repetitive" vs "every request is
unique") are LLM-driven and depend on the real Claude client. The deterministic
projection populates nodes, evidence, and completeness; relationships and
contradictions are populated by the LLM enrichment path and are not fabricated by
the offline `FakeLLM`.
