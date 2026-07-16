"""CSM: Customer Support Management — Work Arounds & Processes."""

from __future__ import annotations

from pathlib import Path

from flask import Flask, jsonify, render_template, request

from process_parser import (
    append_process_to_file,
    format_new_process,
    load_all_processes,
    search_processes,
)
from workaround_parser import (
    append_entry_to_file,
    format_new_entry,
    load_all_workarounds,
    search_workarounds,
)

BASE_DIR = Path(__file__).resolve().parent
WA_DIR = BASE_DIR / "data" / "workarounds"
PROCESOS_DIR = BASE_DIR / "data" / "procesos"

app = Flask(__name__)


# ── Pages ──────────────────────────────────────────────────────────────────

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/wa")
def wa():
    return render_template("wa.html")


@app.route("/procesos")
def procesos():
    return render_template("procesos.html")


# ── Work Arounds API ───────────────────────────────────────────────────────

@app.route("/api/wa/search", methods=["POST"])
def api_wa_search():
    data = request.get_json(silent=True) or {}
    query = (data.get("query") or "").strip()

    if not query:
        return jsonify({"results": [], "message": "Enter an error to search."})

    entries = load_all_workarounds(WA_DIR)
    results = search_workarounds(entries, query)

    return jsonify(
        {
            "results": [
                {
                    "error": e.error,
                    "tuxedo_error": e.tuxedo_error,
                    "description": e.description,
                    "workaround": e.workaround,
                    "tags": e.tags,
                    "source_file": e.source_file,
                    "line_number": e.line_number,
                }
                for e in results
            ],
            "total": len(results),
            "query": query,
        }
    )


@app.route("/api/wa/add", methods=["POST"])
def api_wa_add():
    data = request.get_json(silent=True) or {}
    error = (data.get("error") or "").strip()
    tuxedo_error = (data.get("tuxedo_error") or "").strip()
    description = (data.get("description") or "").strip()
    workaround = (data.get("workaround") or "").strip()
    tags = (data.get("tags") or "").strip()
    filename = (data.get("filename") or "workarounds.txt").strip()

    if not error or not workaround:
        return jsonify({"success": False, "message": "Error and Workaround are required."}), 400

    if not filename.endswith(".txt"):
        filename += ".txt"

    entry_text = format_new_entry(error, tuxedo_error, description, workaround, tags)
    target = append_entry_to_file(WA_DIR, filename, entry_text)

    return jsonify(
        {
            "success": True,
            "message": f"Workaround added to {target.name}",
            "filename": target.name,
        }
    )


@app.route("/api/wa/files", methods=["GET"])
def api_wa_files():
    WA_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(p.name for p in WA_DIR.glob("*.txt"))
    return jsonify({"files": files})


# ── Processes API ──────────────────────────────────────────────────────────

@app.route("/api/procesos/search", methods=["POST"])
def api_procesos_search():
    data = request.get_json(silent=True) or {}
    query = (data.get("query") or "").strip()

    if not query:
        return jsonify({"results": [], "message": "Enter a process to search."})

    entries = load_all_processes(PROCESOS_DIR)
    results = search_processes(entries, query)

    return jsonify(
        {
            "results": [
                {
                    "nombre": e.nombre,
                    "pasos": e.pasos,
                    "source_file": e.source_file,
                    "line_number": e.line_number,
                }
                for e in results
            ],
            "total": len(results),
            "query": query,
        }
    )


@app.route("/api/procesos/add", methods=["POST"])
def api_procesos_add():
    data = request.get_json(silent=True) or {}
    nombre = (data.get("nombre") or "").strip()
    pasos = (data.get("pasos") or "").strip()
    filename = (data.get("filename") or "procesos.txt").strip()

    if not nombre or not pasos:
        return jsonify({"success": False, "message": "Name and steps are required."}), 400

    if not filename.endswith(".txt"):
        filename += ".txt"

    entry_text = format_new_process(nombre, pasos)
    target = append_process_to_file(PROCESOS_DIR, filename, entry_text)

    return jsonify(
        {
            "success": True,
            "message": f"Process added to {target.name}",
            "filename": target.name,
        }
    )


@app.route("/api/procesos/files", methods=["GET"])
def api_procesos_files():
    PROCESOS_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(p.name for p in PROCESOS_DIR.glob("*.txt"))
    return jsonify({"files": files})


if __name__ == "__main__":
    WA_DIR.mkdir(parents=True, exist_ok=True)
    PROCESOS_DIR.mkdir(parents=True, exist_ok=True)
    print("CSM started at http://127.0.0.1:5000")
    app.run(debug=True, host="127.0.0.1", port=5000)
