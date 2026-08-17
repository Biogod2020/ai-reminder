# Security and privacy

## Trust model

A Hermes Python plugin executes in the Hermes process with the current user's permissions. Install only code you trust and validate it with `hermes plugins doctor`.

AI Reminder stores task and plan data locally. It does not require API credentials and does not make network requests itself. Calendar access is delegated to the separately configured Hermes Google Workspace skill.

## Side-effect policy

- Plan generation is read/write only within the local plugin database.
- Calendar create/update/delete operations must be shown to the user and confirmed.
- Events with attendees must never be moved or deleted autonomously.
- Preference changes require confirmation; learned internal estimate/hour statistics are bounded and reversible.

## Historical secret exposure

Earlier revisions of this repository tracked `.env`, SQLite databases, and a large personal memory markdown file. Their removal from the current branch does not erase Git objects in prior history.

Required response:

1. Rotate every credential that ever appeared in the repository.
2. Treat prior database and memory contents as disclosed.
3. Use `git filter-repo` or an equivalent audited history rewrite if the repository must become clean.
4. Force-push only after coordinating with all clones and forks.

This rewrite intentionally does not force-rewrite repository history.

## Reporting

Open a private security advisory in the GitHub repository for vulnerabilities. Do not put live credentials or personal schedule data in a public issue.
