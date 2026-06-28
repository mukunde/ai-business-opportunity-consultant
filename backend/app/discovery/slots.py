"""Discovery interview slots (ADR 0004).

The upstream Discovery interview pursues business + process understanding before
any solution is discussed. Mirrors DiscoveryExtraction's fields. Kept tight (one
business pass + one process), per the council's "one module, not nine agents".
"""

# (key, human label, why it matters - used to phrase questions and explain gaps)
DISCOVERY_SLOTS: list[tuple[str, str, str]] = [
    ("sector", "secteur d'activite", "situe le metier et ses enjeux"),
    ("objectives", "objectifs et KPI suivis", "relient les irritants a la valeur"),
    ("process_name", "processus principal a explorer", "cadre le perimetre"),
    ("process_steps", "etapes du processus", "revelent ou se cachent les irritants"),
]

DISCOVERY_SLOT_KEYS: list[str] = [key for key, _, _ in DISCOVERY_SLOTS]
DISCOVERY_SLOT_LABELS: dict[str, str] = {key: label for key, label, _ in DISCOVERY_SLOTS}
DISCOVERY_SLOT_REASONS: dict[str, str] = {key: reason for key, _, reason in DISCOVERY_SLOTS}
