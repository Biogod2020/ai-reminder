# Evaluation contract

A personal scheduling secretary cannot be evaluated by how convincing its prose sounds. AI Reminder uses deterministic regression metrics:

- hard-constraint violation rate: overlap, busy-calendar collision, out-of-hours placement, deadline breach, earliest-start breach, or dependency inversion;
- requested-work coverage;
- explicit unscheduled-task count;
- block fragmentation and context switches;
- replan calendar churn: create/update/delete delta rather than wholesale recreation.

Run:

```bash
python scripts/benchmark.py
```

The acceptance gate is zero hard-constraint violations. Capacity shortfalls are valid only when returned explicitly in `unscheduled`; the planner must never hide them by overlapping or compressing work.

For real deployments, additionally track weekly:

1. deadline miss rate;
2. user intervention rate per plan;
3. event churn per replan;
4. estimate calibration by work context;
5. completion rate by local hour;
6. percentage of suggested blocks accepted unchanged.

These product metrics require longitudinal user feedback and are intentionally not fabricated by the repository's offline benchmark.
