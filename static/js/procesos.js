document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initSearch();
  initAddForm();
  loadFiles();
});

function initSearch() {
  const input = document.getElementById("search-input");
  const btn = document.getElementById("btn-search");

  btn.addEventListener("click", () => performSearch());
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") performSearch();
  });
}

async function performSearch() {
  const query = document.getElementById("search-input").value.trim();
  const statusEl = document.getElementById("search-status");
  const resultsEl = document.getElementById("search-results");
  const btn = document.getElementById("btn-search");

  if (!query) {
    showStatus(statusEl, "warning", "Enter the process name or keywords.");
    resultsEl.innerHTML = "";
    return;
  }

  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Searching...';
  resultsEl.innerHTML = "";
  statusEl.classList.add("hidden");

  try {
    const res = await fetch("/api/procesos/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });
    const data = await res.json();

    if (data.total === 0) {
      showStatus(
        statusEl,
        "warning",
        `No processes found for "${query}". Try other keywords or add a new one.`
      );
      return;
    }

    showStatus(statusEl, "info", `${data.total} result(s) found for "${query}"`);
    resultsEl.innerHTML = data.results.map(renderResult).join("");
    initResultCards();
  } catch (err) {
    showStatus(statusEl, "error", "Search error. Verify the server is running.");
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<span class="btn-icon">🔍</span> Search';
  }
}

function renderResult(entry) {
  return `
    <article class="result-card collapsed">
      <button type="button" class="result-card-toggle" aria-expanded="false">
        <div class="result-header">
          <div class="result-title process-title">${escapeHtml(entry.nombre)}</div>
          <div class="result-meta">${escapeHtml(entry.source_file)}:${entry.line_number}</div>
        </div>
        <span class="result-expand-icon" aria-hidden="true">▼</span>
      </button>
      <div class="result-card-body collapsed">
        <div class="result-section-label">Procedure steps</div>
        <div class="result-workaround">${escapeHtml(entry.pasos)}</div>
      </div>
    </article>
  `;
}

function initAddForm() {
  const form = document.getElementById("add-form");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const statusEl = document.getElementById("add-status");
    const btn = form.querySelector("button[type=submit]");

    const payload = {
      nombre: document.getElementById("add-nombre").value,
      pasos: document.getElementById("add-pasos").value,
      filename: document.getElementById("add-filename").value,
    };

    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Saving...';

    try {
      const res = await fetch("/api/procesos/add", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();

      if (data.success) {
        showStatus(statusEl, "success", data.message);
        form.reset();
        loadFiles();
      } else {
        showStatus(statusEl, "error", data.message || "Error saving.");
      }
    } catch (err) {
      showStatus(statusEl, "error", "Connection error while saving.");
    } finally {
      btn.disabled = false;
      btn.innerHTML = '<span class="btn-icon">➕</span> Save Process';
    }
  });
}

async function loadFiles() {
  try {
    const res = await fetch("/api/procesos/files");
    const data = await res.json();
    const select = document.getElementById("add-filename");
    const current = select.value;
    select.innerHTML = "";

    const defaultOpt = document.createElement("option");
    defaultOpt.value = "procesos.txt";
    defaultOpt.textContent = "procesos.txt (new)";
    select.appendChild(defaultOpt);

    data.files.forEach((file) => {
      const opt = document.createElement("option");
      opt.value = file;
      opt.textContent = file;
      select.appendChild(opt);
    });

    if ([...select.options].some((o) => o.value === current)) {
      select.value = current;
    }
  } catch {
    /* optional on load */
  }
}
