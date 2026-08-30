---
name: role-architect
description: "AES architecture reviewer: validates layer boundaries, naming, dependencies, orphans, scalability (7-layer spec)."
metadata:
  tags: [architect, aes, architecture, review, layer-boundaries, naming, orphan, scalability, data-flow]
  triggers: [review as architect, architecture review, check architecture, validate architecture, architect review, layer boundary check, architecture audit]
  dependencies: []
  related: [role-tech-lead, role-business-analyst, role-fullstack-developer, role-quality-analysis]
---
# role-architect

Expert AES architecture reviewer.

## Prerequisites

Read first:

1. `.agents/rules/RULES_AES.md` (rules 101-506)
2. `ARCHITECTURE.md` (7-layer spec)
3. `PRD.md` (product context)
4. `.agents/skills/` (skill-driven dev)

## Workflow

Execute sequentially, no skips.

### 1. Identify

- Locate: `modules|crates|packages/<feature>/`
- Read `<feature>/FRD.md`
- List modules

### 2. Reference

- `RULES_AES.md` Groups 1-5
- `ARCHITECTURE.md` 7-layer spec
- Classify files: taxonomy|contract|utility|capabilities|agent|surface|root

### 3. Analyze


| Dimension    | Focus                              |
| -------------- | ------------------------------------ |
| Naming       | Convention compliance              |
| Boundaries   | Import rules, dependency direction |
| Capabilities | Protocol impl                      |
| Agent        | Aggregate impl                     |
| Orphan       | Dead code                          |
| Scalability  | SRP, coupling                      |
| Data Flow    | Unidirectional, no cycles          |


## Template

# Plan: {feature} — Architect

## Summary

{One paragraph}

## Findings

### Layer Boundaries


| # | Severity | Issue | Location | Recommendation |
| --- | ---------- | ------- | ---------- | ---------------- |

### Naming


| # | Severity | Issue | Location | Recommendation |
| --- | ---------- | ------- | ---------- | ---------------- |

### Orphan


| # | Severity | Issue | Location | Recommendation |
| --- | ---------- | ------- | ---------- | ---------------- |

### Scalability


| # | Severity | Issue | Location | Recommendation |
| --- | ---------- | ------- | ---------- | ---------------- |

### Data Flow


| # | Severity | Issue | Location | Recommendation |
| --- | ---------- | ------- | ---------- | ---------------- |

## Violations

{List or "None"}

## Action Items

- [ ]  {Priority} {Item}

## Fixed Code

{Grouped by file}

## Severity


| Level       | Meaning                                              |
| ------------- | ------------------------------------------------------ |
| 🔴 CRITICAL | Layering breach, security, data leak. Immediate fix. |
| 🟡 WARNING  | Convention/perf/maintainability. Fix this cycle.     |
| 🟢 INFO     | Suggestion. Deferrable.                              |

## Checklist

- [ ]  Prerequisites read
- [ ]  Feature identified
- [ ]  All 7 dimensions analyzed
- [ ]  Severity categorized
- [ ]  Saved to correct path
- [ ]  M=0: stopped with report
