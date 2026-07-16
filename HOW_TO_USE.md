# How to Use CSM-WA

CSM (Customer Support Management) is a local web tool for technical support teams. It helps you search documented **Work Arounds** (errors and fixes) and **Processes** (operational procedures), and add new entries for future use.

---

## Requirements

- **Python 3.10+** (3.12 recommended)
- **Windows** (setup scripts are provided for PowerShell and CMD)
- Internet is **not** required after installation — the app runs locally

See [requirements.txt](requirements.txt) for Python package dependencies.

---

## Quick Start (Windows)

### 1. Clone the repository

```powershell
git clone https://github.com/alexander-cornejo/csm-wa.git
cd csm-wa
```

### 2. Run setup (first time only)

**PowerShell:**

```powershell
.\setup.ps1
```

**Command Prompt:**

```cmd
setup.bat
```

Setup will:

- Check for Python (and install via `winget` if missing)
- Create a virtual environment in `venv/`
- Install dependencies from `requirements.txt`
- Verify the `data/` folder structure

### 3. Start the application

**PowerShell:**

```powershell
.\start.ps1
```

**Command Prompt:**

```cmd
start.bat
```

### 4. Open in your browser

Go to: **http://127.0.0.1:5000**

Press `Ctrl+C` in the terminal to stop the server.

---

## Manual Setup (any OS)

If you prefer not to use the Windows scripts:

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
python app.py
```

Then open **http://127.0.0.1:5000**.

---

## Using the Web Interface

### Home

From the home page, choose one of two modules:

| Module | URL | Purpose |
|--------|-----|---------|
| **Work Arounds (WAs)** | `/wa` | Search and add error workarounds |
| **Processes** | `/procesos` | Search and add operational procedures |

### Work Arounds

1. Open **WAs** from the home page.
2. Type an error message, keyword, or tag in the search box.
3. Review matching entries (error, description, Tuxedo error, workaround steps).
4. To add a new entry, fill in the form and choose a target `.txt` file under `data/workarounds/`.

Workaround files use this format:

```
[ERROR]
Your error message here

[DESCRIPTION]
What the error means and when it appears

[TUXEDO_ERROR]
Tuxedo or stack trace details (optional)

[WORKAROUND]
1. First step
2. Second step

[TAGS]
keyword1, keyword2

---
```

Each entry is separated by `---`. You can add multiple `.txt` files in `data/workarounds/` — the app indexes all of them automatically.

### Processes

1. Open **Processes** from the home page.
2. Search by process name or step content.
3. To add a new process, provide a name, steps, and target file under `data/procesos/`.

Process files use this format:

```
[NOMBRE]
Process name

[PASOS]
Step-by-step instructions here

---
```

---

## Project Structure

```
csm-wa/
├── app.py                 # Flask web application
├── workaround_parser.py   # Workaround search and file handling
├── process_parser.py      # Process search and file handling
├── requirements.txt       # Python dependencies
├── setup.ps1 / setup.bat  # First-time setup (Windows)
├── start.ps1 / start.bat  # Start the server (Windows)
├── data/
│   ├── workarounds/       # Workaround .txt files
│   └── procesos/          # Process .txt files
├── static/                # CSS and JavaScript
├── templates/             # HTML pages
└── docs/                  # Architecture documentation
```

---

## Optional Utilities

These scripts are **not** required to run the web app:

| Script | Purpose | Extra dependency |
|--------|---------|------------------|
| `generate_architecture_docs.py` | Generate Word architecture docs | `python-docx` |
| `convert_clarify_wa.py` | Convert/clarify workaround data | — |
| `convert_procesos_import.py` | Import raw process data | — |

To install optional dependencies:

```powershell
pip install python-docx
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `Virtual environment not found` | Run `.\setup.ps1` first |
| `Python not found` | Install from [python.org](https://www.python.org/downloads/) and check **Add to PATH** |
| Port 5000 already in use | Stop the other process or change the port in `app.py` |
| PowerShell blocks scripts | Run: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| No search results | Check that `.txt` files exist in `data/workarounds/` or `data/procesos/` |

---

## Sharing with Others

Anyone can view the source code on GitHub:

**https://github.com/alexander-cornejo/csm-wa**

To run the app locally, they need to clone the repo and follow the **Quick Start** steps above. The app does not run on GitHub itself — it runs on each user's machine.
