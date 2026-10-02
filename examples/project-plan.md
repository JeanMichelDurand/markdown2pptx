---
title: CRM migration
subtitle: Project kick-off
author: Sales operations
---

# The project

## Goals

- Move **all 42,000 accounts** and their history to the new CRM by the end of June
- Retire the old CRM and its licences: €180k a year
- Keep sales running: no more than one weekend of downtime

## Scope

| In scope                         | Out of scope                     |
|:---------------------------------|:---------------------------------|
| Accounts, contacts, opportunities | Marketing campaigns (phase 2)   |
| Five years of activity history   | Older history: archived as files |
| Quote templates                  | Custom reports: rebuilt on demand |
| Outlook and phone integration    | The partner portal               |

# The plan

## Timeline

```mermaid
gantt
    title CRM migration
    dateFormat YYYY-MM-DD
    section Prepare
    Data audit and cleaning    :a1, 2026-01-12, 4w
    Field mapping              :a2, after a1, 2w
    section Build
    Configure the new CRM      :b1, 2026-02-09, 6w
    Integrations               :b2, after a2, 5w
    section Move
    Trial migration            :c1, after b1, 2w
    User training              :c2, after c1, 3w
    Cut-over weekend           :milestone, m1, 2026-05-16, 0d
    Old CRM switched off       :milestone, m2, 2026-06-30, 0d
```

## How the data moves

```mermaid
flowchart LR
    subgraph Old [Old CRM]
        X[Export] --> V[Validate]
    end
    subgraph New [New CRM]
        L[Load] --> R{Reconciled?}
    end
    V --> L
    R -->|yes| S([Sign-off])
    R -->|no| F[Fix the mapping]
    F --> X
```

Each trial migration runs this loop until the counts and totals match.

## Who does what

| Task                 | Sales ops | IT | Sales managers | Vendor |
|:---------------------|:---------:|:--:|:--------------:|:------:|
| Data cleaning        |     R     | C  |       A        |        |
| CRM configuration    |     A     | C  |       C        |   R    |
| Integrations         |     C     | R  |                |   C    |
| Training             |     R     |    |       A        |   C    |
| Cut-over             |     A     | R  |       I        |   R    |

R: responsible, A: accountable, C: consulted, I: informed.

# Next steps

## This month

1. Name a data owner in each sales region
2. Freeze changes to the old CRM's fields
3. Book the cut-over weekend with the vendor
4. Send the first newsletter to the sales teams

::: notes
Ask each regional manager for their data owner's name before the end of the meeting.
:::
