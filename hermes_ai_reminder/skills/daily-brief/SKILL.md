---
name: daily-brief
description: Produce a concise morning brief from Calendar, durable tasks, deadline risk, and the current internal plan.
version: 1.0.0
author: Biogod2020
license: MIT
---

# Daily Brief

1. Determine the user's configured timezone with `secretary_preferences(action="get", key="timezone")`.
2. Load `google-workspace` and list Calendar events from local midnight through the end of the day. Include timezone offsets.
3. Call `secretary_brief(range="today")`.
4. If there is no usable committed plan for today, convert Calendar events to `busy_blocks` and call `secretary_plan(action="generate")` for today. Do not create events during an unattended cron run.
5. Deliver no more than:
   - next fixed meeting;
   - current/next focus block;
   - three highest-risk tasks;
   - one decision requiring the user's confirmation.

Do not pad the brief with motivational prose. If there is no risk or decision, say so plainly.
