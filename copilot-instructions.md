# ESLBeginner — Workspace Isolation Rules

This repository is a **standalone project**. Follow these rules strictly on every task.

## Scope

- This project contains ESL beginner grammar notes in `MD/` and (optionally) project-local PDF build scripts.
- Work **only** inside this workspace folder: `F:\AI project\ESLBeginner`.
- Never open, search, read, or modify anything outside this folder.

## Hard prohibitions

- **Never** read, search, reference, copy, or modify files from sibling projects:
  - `F:\AI project\ESLAIO`
  - `F:\AI project\ESLassistant`
  - `F:\AI project\ESLBuddy`
- **Never** run terminal commands from another project's directory. Always `cd` into this project first (`.vscode/settings.json` sets `terminal.integrated.cwd` to `${workspaceFolder}`).
- **Never** use another project's virtual environment (`.venv`), config files, templates, or scripts.
- **Never** reuse or import code, prompts, or config from sibling projects.
- **Never** resolve paths like `F:\AI project\ESLassistant\...` — they belong to other projects.

## Build workflow

- PDF generation (if performed) uses **Pandoc + xelatex (MiKTeX)**.
- All scripts, styles, and templates used by this project must live **inside this repository**.
- Output artifacts go to `PDF/` inside this project — never to a sibling project's directory.

## Verification before acting

- Check the terminal working directory is `F:\AI project\ESLBeginner` before running any command.
- If asked about files that do not exist here (e.g., `build.ps1`, `styles/`, `templates/`), they were removed in a past commit — do **not** fetch them from sibling projects.
