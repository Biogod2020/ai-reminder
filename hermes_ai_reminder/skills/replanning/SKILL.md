---
name: replanning
description: Replan only the future after overruns, skipped blocks, new meetings, cancellations, or changed deadlines.
version: 1.0.0
author: Biogod2020
license: MIT
---

# Replanning

Replanning is a state transition, not a fresh brainstorm.

1. Record what happened through `secretary_feedback` when the user reports completion, overrun, snooze, or skip.
2. Re-read the affected Calendar horizon using `google-workspace`; never assume the old event list is still correct.
3. Call `secretary_plan(action="replan", plan_id=..., busy_blocks=...)`.
4. Preserve started, completed, locked, and past blocks. The plugin does this automatically; do not ask it to move them.
5. Present only the delta:
   - removed or shortened blocks;
   - newly scheduled blocks;
   - tasks now at risk or unscheduled.
6. Ask for confirmation before changing Calendar events. On approval, apply only the returned create/update/delete delta. Acknowledge creates and updates with `link_calendar`; acknowledge deletes with `unlink_calendar` on the source block.

Prefer a small feasible repair over rewriting the entire week. Do not punish one overrun by compressing every later task into unrealistic blocks.
