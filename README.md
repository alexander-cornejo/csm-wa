# CSM-WA

**CSM (Customer Support Management)** — a local web tool for technical support teams to search and manage **Work Arounds** and **Processes**.

[![Repository](https://img.shields.io/badge/GitHub-alexander--cornejo%2Fcsm-wa-blue)](https://github.com/alexander-cornejo/csm-wa)

## Features

- **Work Arounds** — search documented errors, Tuxedo errors, and their fixes
- **Processes** — search and browse operational procedures with step-by-step instructions
- **Add entries** — record new workarounds and processes directly from the web UI
- **Local & offline** — runs on your machine; no cloud dependency

## Quick Start

```powershell
git clone https://github.com/alexander-cornejo/csm-wa.git
cd csm-wa
.\setup.ps1    # first time only
.\start.ps1    # start the server
```

Open **http://127.0.0.1:5000** in your browser.

> On Command Prompt, use `setup.bat` and `start.bat` instead.

## Requirements

| Requirement | Details |
|-------------|---------|
| Python | 3.10 or newer |
| OS | Windows (scripts provided); manual setup works on macOS/Linux |
| Dependencies | Listed in [requirements.txt](requirements.txt) |

**Main dependency:** Flask 3.x

**Optional:** `python-docx` (for generating architecture Word documents)

Install everything:

```powershell
pip install -r requirements.txt
```

## Documentation

| File | Description |
|------|-------------|
| [HOW_TO_USE.md](HOW_TO_USE.md) | Full setup guide, usage instructions, file formats, and troubleshooting |
| [requirements.txt](requirements.txt) | Python package dependencies |
| [docs/hybrid-ai-architecture-EN.md](docs/hybrid-ai-architecture-EN.md) | Hybrid AI architecture (English) |
| [docs/arquitectura-ia-hibrida-ES.md](docs/arquitectura-ia-hibrida-ES.md) | Arquitectura IA híbrida (Español) |

## Project Layout

```
csm-wa/
├── app.py              # Flask application
├── data/workarounds/   # Workaround data (.txt)
├── data/procesos/      # Process data (.txt)
├── static/             # Frontend assets
├── templates/          # HTML templates
├── setup.ps1           # Windows setup script
└── start.ps1           # Windows start script
```

## License

This project is provided as-is for internal support team use. See the repository for details.
