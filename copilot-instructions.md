# ESLBeginner — Workspace Isolation Rules

This repository is a **standalone project**. Follow these rules strictly on every task.

## Scope

- This project contains ESL beginner grammar notes in `MD/` and (optionally) project-local PDF build scripts.
- Work **only** inside this workspace folder: `F:\AI project\ESLBeginner`.
- Never open, search, read, or modify anything outside this folder.

## 内容原则

- **受众与时代定位**：所有内容面向 **2026 年的中国成年英语学习者（A1–B1）**。例句、讨论题、练习场景必须贴近当代中国成年人生活（外卖、地铁通勤、加班、面试、租房、微信等），不用过时或陌生场景。
- **习语必须当代、真实在用**：只选 2020 年代英语口语中真实高频的习语/俚语，避免教科书式、老套、过时的表达（如 over the moon、raining cats and dogs、down in the dumps 之类）。拿不准就先查证再写。
- **例句要有具体画面**：每条例句必须包含具体场景、人物和动作，让读者能立刻在脑中成像并代入（如 "I'm in a good mood — my coffee was free today."），禁止写干巴巴的通用例句（如 "I'm happy today."）。

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

## 课程介绍同步

- 每门课程 MD 的标题下方都有 `## 课程介绍`（一句话开场介绍，模板见根目录 `课程介绍总览.md`）。
- 新增或修改课程时，先更新根目录 `课程介绍总览.md`：在"各课课程介绍"末尾按"课程名 + 介绍"两行一段的格式加/改内容，课程名要和该课 MD 的一级标题一致。
- 然后运行同步脚本，把介绍写入所有课程 MD（已存在则覆盖、不会重复插入）：

  ```powershell
  .venv\Scripts\python build\sync_intro.py
  ```

- 只同步某一课时可加文件名关键字，例如 `.venv\Scripts\python build\sync_intro.py 14`。

## Verification before acting

- Check the terminal working directory is `F:\AI project\ESLBeginner` before running any command.
- If asked about files that do not exist here (e.g., `build.ps1`, `styles/`, `templates/`), they were removed in a past commit — do **not** fetch them from sibling projects.
