---
name: task-capture
description: Convert vague goals into minimal, schedulable task records without over-questioning the user.
version: 1.0.0
author: Biogod2020
license: MIT
---

# Task Capture

Turn user language into a durable `secretary_task` record.

## Required reasoning

Extract or estimate:

- a concrete deliverable-oriented title;
- remaining duration in minutes;
- priority from 1 to 5;
- deadline and earliest start when stated;
- energy need (`low`, `medium`, `high`);
- cognitive load from 0 to 1;
- whether the work can be split;
- minimum and maximum useful block size;
- a stable context such as `writing`, `coding`, `reading`, `admin`, or `calls`;
- dependencies on existing task ids.

Use conservative defaults when the missing field has low consequence. Ask one concise question when duration or deadline uncertainty could make the plan infeasible. Do not ask for every optional field.

## Defaults

- priority: 3
- duration: 30 minutes, but report that this was defaulted
- energy: medium
- cognitive load: 0.5
- splittable: true
- minimum block: 25 minutes
- maximum block: 90 minutes

Large projects should remain one parent-level task unless separate deliverables have independently meaningful deadlines or dependencies. Avoid generating dozens of tiny pseudo-tasks merely to appear thorough.
