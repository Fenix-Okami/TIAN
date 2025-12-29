# Copilot instructions (TIAN)

## Python execution
- Always run Python scripts with the project virtual environment activated.
- If you need to run commands, prefer calling the venv interpreter explicitly:
  - Windows PowerShell: `./venv/Scripts/python.exe <script.py>`
  - Windows cmd.exe: `venv\Scripts\python.exe <script.py>`
- Do not assume a global `python` is correct.

## Codebase hygiene
- Keep changes minimal and focused on the requested task.
- Prefer small, reusable helpers over new modules.
- Avoid introducing new dependencies unless clearly justified.
- Follow existing file structure and naming patterns.
- Do not reformat unrelated code.
