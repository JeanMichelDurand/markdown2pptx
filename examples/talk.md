---
title: Moving the team to self-service reporting
subtitle: Proposal for the steering committee, Q4
author: Data platform team
---

# Why change

## Where we are

- 140 report requests a month reach the data team
- **Median wait: 9 days**, a third of them for a filter or a column
- Analysts spend *most* of their week on extracts, not analysis
  - two people full time on recurring exports
  - no time left for the forecasting work

::: notes
Open with the wait time: it is the number the business units quote back to us.
:::

## What users ask for

| Request type        | Share | Median wait |
|:--------------------|------:|------------:|
| New column / filter |   34% |      6 days |
| New report          |   27% |     15 days |
| Data extract        |   22% |      4 days |
| Access request      |   17% |      2 days |

Two thirds of the requests change an existing report.

# The proposal

## How a request flows today

```mermaid
flowchart LR
    U([Business user]) --> T[Ticket]
    T --> Q{Data team<br>available?}
    Q -->|yes| B[Build the report]
    Q -->|no| W[Wait in backlog]
    W --> Q
    B --> R[(Report server)]
    R --> U
```

## With self-service

```mermaid
sequenceDiagram
    participant U as Business user
    participant C as Certified dataset
    participant D as Data team
    U->>C: build or change a report
    C-->>U: governed data, same definitions
    U->>D: only new sources
    D->>C: publish a certified dataset
```

The data team curates datasets; users build their own reports on them.

## Rollout plan

```mermaid
gantt
    title Self-service rollout
    dateFormat YYYY-MM-DD
    section Foundations
    Certified datasets      :a1, 2026-11-02, 30d
    Access model            :a2, after a1, 14d
    section Pilot
    Finance pilot           :b1, after a2, 21d
    Training                :b2, after a2, 10d
    section Scale
    All business units      :c1, after b1, 45d
```

## What we need

1. Two weeks of a security engineer for the access model
2. Licences for **25 report authors**
3. A sponsor in each business unit

> [!NOTE]
> The licences replace the current extract tool, so the running cost stays flat.

---

### Decision requested today

Approve the pilot with Finance, starting **2 November**.

<!-- Ask for the decision before questions: the committee has 20 minutes. -->
