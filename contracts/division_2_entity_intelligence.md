# Division 2 Entity Intelligence → NeonDB Contract

## 1. Purpose

Division 2 (Entity Intelligence) transforms processed criminal intelligence data into validated entity mentions, candidate identities, resolution results, and supporting provenance.

The output of Division 2 is consumed by NeonDB / downstream Division 3 components.

---

## 2. Input

Division 2 consumes processed data from Division 1, including:

* FIR narratives
* Person registry
* Case entities
* Phone registry
* Vehicle registry
* Location data

---

## 3. Output

Primary output:

`divisions/02-entity-intelligence/output/person_resolutions.csv`

Current output size:

* 20,000 PERSON resolution records
* 8,269 RESOLVED
* 11,731 AMBIGUOUS
* 0 UNRESOLVED

---

## 4. PERSON Resolution Record Schema

| Field                         | Type        |    Required | Description                                        |
| ----------------------------- | ----------- | ----------: | -------------------------------------------------- |
| `mention_id`                  | string      |         Yes | Unique identifier for the extracted entity mention |
| `document_id`                 | string      |         Yes | Source document identifier                         |
| `case_id`                     | string      |         Yes | Associated case identifier                         |
| `text_span`                   | string      |         Yes | Original text containing the entity mention        |
| `start_char`                  | integer     |         Yes | Start character offset in source text              |
| `end_char`                    | integer     |         Yes | End character offset in source text                |
| `entity_type`                 | string      |         Yes | Entity type. Currently `PERSON`                    |
| `candidate_person_ids`        | JSON array  |         Yes | Candidate canonical person IDs                     |
| `candidate_count`             | integer     |         Yes | Number of generated candidates                     |
| `candidate_generation_method` | string      |         Yes | Method used for candidate generation               |
| `resolved_entity_id`          | string/null | Conditional | Canonical person ID when resolution succeeds       |
| `resolution_status`           | string      |         Yes | `RESOLVED`, `AMBIGUOUS`, or `UNRESOLVED`           |
| `resolution_method`           | string      |         Yes | Method used by the resolver                        |
| `resolution_confidence`       | float       |         Yes | Resolution confidence value                        |
| `evidence`                    | JSON object |         Yes | Evidence and provenance associated with candidates |

---

## 5. Resolution Status Semantics

### RESOLVED

Exactly one candidate is currently identified by the resolver.

Example:

```text
candidate_person_ids = ["P002189"]
resolved_entity_id = "P002189"
resolution_status = "RESOLVED"
```

### AMBIGUOUS

Multiple candidates remain and the available evidence does not justify selecting one.

Example:

```text
candidate_person_ids = ["P001807", "P002378"]
resolved_entity_id = null
resolution_status = "AMBIGUOUS"
```

**Downstream systems must not arbitrarily select one candidate from an AMBIGUOUS record.**

### UNRESOLVED

No candidate could be generated.

```text
candidate_person_ids = []
resolved_entity_id = null
resolution_status = "UNRESOLVED"
```

---

## 6. Candidate Generation Semantics

Candidate generation answers:

> Which registered people could this mention refer to?

It does not determine the final identity.

Current candidate-generation methods include:

* `EXACT_NAME`
* `INITIAL_SURNAME`
* `NO_MATCH`

Candidate generation has been evaluated against 8,604 ground-truth name variants:

```text
Correct candidate inclusion: 8,604 / 8,604
Candidate recall:             100%
Missing:                      0
```

---

## 7. Resolution Semantics

The current resolver is intentionally conservative.

Current behavior:

```text
0 candidates
    → UNRESOLVED

1 candidate
    → RESOLVED

>1 candidates
    → AMBIGUOUS
```

Contextual evidence is preserved but is not automatically treated as proof of identity.

A case-level relationship such as `INVOLVES` or `MENTIONS` must not automatically be interpreted as proof that a particular PERSON mention refers to that candidate.

---

## 8. Provenance

Downstream systems should preserve:

* `mention_id`
* `document_id`
* `case_id`
* source text span
* character offsets
* candidate IDs
* resolution method
* resolution status
* resolution confidence
* evidence

This allows downstream users to trace an entity decision back to its source document.

---

## 9. NeonDB Integration Requirements

NeonDB should preserve the distinction between:

```text
Entity Mention
        ↓
Candidate Person
        ↓
Resolved Canonical Person
```

Recommended logical relationships:

```text
document
   ↓
entity_mention
   ↓
candidate_person
   ↓
canonical_person
```

For an AMBIGUOUS mention, multiple candidate relationships may exist while `resolved_entity_id` remains NULL.

---

## 10. Data Integrity Rules

1. Do not overwrite source text.
2. Do not discard candidate IDs for ambiguous records.
3. Do not convert `AMBIGUOUS` into `RESOLVED` without additional identity evidence.
4. Preserve source document and case references.
5. Preserve character offsets.
6. Preserve provenance/evidence.
7. Treat `resolution_confidence` as a resolver output, not automatically as a probability.
8. Maintain the canonical `person_id` namespace used by the person registry.

---

## 11. Current Validation

Division 2 validation status:

```text
Unit tests:                  15 / 15 passed
Ground-truth name variants:  8,604
Candidate recall:            100%
Missing candidates:          0
Output records:              20,000
```

---

## 12. Handoff

Division 2 provides the entity-intelligence output.

NeonDB / downstream systems are responsible for persistence and downstream consumption.

Pipeline boundary:

```text
Division 1
    ↓
Division 2 Entity Intelligence
    ↓
person_resolutions.csv
    ↓
NeonDB
    ↓
Division 3 / Knowledge Graph / Application
```
