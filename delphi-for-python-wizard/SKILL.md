---
name: delphi-for-python-wizard
description: >-
  Wizard to initialize and configure new Delphi+Python (VCL or FMX) projects on Windows with smart Python version detection, virtual environment setup, library installation, and template file generation (including event and style guides).
---

# Delphi for Python Wizard

## Overview
This skill provides the agent with an automated wizard to initialize new Delphi + Python projects using either the **DelphiVCL** (Windows-native) or **DelphiFMX** (cross-platform) framework. It includes automatic detection of compatible Python versions (3.8 to 3.13) to avoid issues with incompatible alpha/beta versions (like Python 3.14+), sets up clean virtual environments, upgrades package managers, installs dependencies, and generates solid starter templates containing educational comments about VCL Styling (`StyleElements`) and Python set-based `Font.Style` declarations.

## Dependencies
None. This is a self-contained automation skill.

## Quick Start

To use this skill to create a new project, simply command the agent:
> *"Crie um novo projeto Delphi VCL chamado Financeiro no caminho C:\Projetos\Financeiro"*

The agent will run the utility script `wizard.py` to set up everything automatically:
```bash
uv run python wizard.py init --name "Financeiro" --framework vcl --path "C:\Projetos\Financeiro"
```

## Utility Scripts

The skill wraps a highly robust automation script `wizard.py` that can be run with the following syntax:

```bash
python wizard.py init --name <ProjectName> --framework <vcl|fmx> --path <DestinationPath>
```

### Arguments:
*   `--name`: The human-readable name of the project.
*   `--framework`: Visual GUI framework to use:
    *   `vcl`: High-performance native Windows GUI (Windows only).
    *   `fmx`: FireMonkey multi-device GUI (Windows, macOS, Linux, Android).
*   `--path`: The absolute path where the project directory will be created.

---

## Workflow

When the user asks to start a new Delphi + Python project, follow these steps:

### 1. Plan and Create Directory
Select the destination path requested by the user and determine the framework (VCL or FMX). If the user doesn't specify a framework, ask them if they need cross-platform (FMX) or native Windows (VCL).

### 2. Execute the Wizard
Run the `wizard.py` script located in the skill directory:
```bash
python {SKILL_DIR}/wizard.py init --name "{NAME}" --framework {vcl|fmx} --path "{PATH}"
```
This will automatically:
1.  Search for the highest stable installed Python version (`3.8` to `3.13`) in the Windows registry or via the `py` launcher, completely avoiding compatibility crashes.
2.  Set up the `venv` virtual environment in the destination directory.
3.  Upgrade `pip` and install the correct framework (`delphivcl` or `delphifmx`).
4.  Generate `main.py` with standard imports, window setup, and event templates.
5.  Generate a fully readable and working test form (`MainForm.pydfm` or `MainForm.pyfmx`).
6.  Generate a detailed `INSTRUCTIONS.md` guide explaining the integration steps.

### 3. Explain the Next Steps to the User
Once the project is successfully initialized, do not re-summarize the entire plan. Instead, present the user with the direct path to the generated files:
1.  Guide them to activate the environment and run the test screen:
    ```powershell
    cd {PATH}
    .\venv\Scripts\Activate.ps1
    python main.py
    ```
2.  Explain how they can open the Delphi IDE to start editing the visual design:
    *   Open Delphi IDE -> New Project -> drag-and-drop components.
    *   Match the names of components with the stub declarations in `main.py`.
    *   Right-click -> **Export to Python** -> save over the generated files.

---

## Common Mistakes

*   **Python Version Mismatch:** Running `pip install delphivcl` on incompatible Python versions (like Python 3.14+) will fail to find wheels and crash trying to compile from source. Always use `wizard.py` to automatically choose a compatible version.
*   **Font.Style Assignment:** Assigning font styles as variables (e.g. `Font.Style = {fsBold}`) results in a `NameError`. In Python, Delphi `Sets` are represented as Python `sets` of strings (e.g. `Font.Style = {"fsBold"}`).
*   **VCL Styles Overriding Fonts/Colors:** By default, custom fonts and colors applied to components may be overridden by the active Windows VCL style. Remember to clear the component's `StyleElements` property:
    ```python
    self.myLabel.StyleElements = ""  # Clears VCL theme elements for this label
    self.myLabel.Color = "$00FF0000"
    ```
