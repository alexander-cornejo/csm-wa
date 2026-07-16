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
    showStatus(statusEl, "warning", "Enter an error or keywords to search.");
    resultsEl.innerHTML = "";
    return;
  }

  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Searching...';
  resultsEl.innerHTML = "";
  statusEl.classList.add("hidden");

  try {
    const res = await fetch("/api/wa/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });
    const data = await res.json();

    if (data.total === 0) {
      showStatus(
        statusEl,
        "warning",
        `No workarounds found for "${query}". Try other keywords or add a new one.`
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
  const tags = entry.tags.map((t) => `<span class="tag">${escapeHtml(t)}</span>`).join("");

  const tuxedoBlock = entry.tuxedo_error
    ? `
      <div class="result-section tuxedo-section">
        <button type="button" class="tuxedo-toggle" aria-expanded="false">
          <span class="tuxedo-toggle-label">Tuxedo Error</span>
          <span class="tuxedo-toggle-action">Expand ▼</span>
        </button>
        <div class="result-tuxedo-error collapsed">${escapeHtml(entry.tuxedo_error)}</div>
      </div>`
    : "";

  return `
    <article class="result-card collapsed">
      <button type="button" class="result-card-toggle" aria-expanded="false">
        <div class="result-header">
          <div class="result-error">${escapeHtml(entry.error)}</div>
          <div class="result-meta">${escapeHtml(entry.source_file)}:${entry.line_number}</div>
        </div>
        <span class="result-expand-icon" aria-hidden="true">▼</span>
      </button>
      <div class="result-card-body collapsed">
        ${entry.description ? `<p class="result-description"><strong>Description:</strong> ${escapeHtml(entry.description)}</p>` : ""}
        ${tuxedoBlock}
        <div class="result-section-label">Work Around</div>
        <div class="result-workaround">${escapeHtml(entry.workaround)}</div>
        ${tags ? `<div class="result-tags">${tags}</div>` : ""}
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
      error: document.getElementById("add-error").value,
      tuxedo_error: document.getElementById("add-tuxedo-error").value,
      description: document.getElementById("add-description").value,
      workaround: document.getElementById("add-workaround").value,
      tags: document.getElementById("add-tags").value,
      filename: document.getElementById("add-filename").value,
    };

    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Saving...';

    try {
      const res = await fetch("/api/wa/add", {
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
      btn.innerHTML = '<span class="btn-icon">➕</span> Save Work Around';
    }
  });
}

async function loadFiles() {
  try {
    const res = await fetch("/api/wa/files");
    const data = await res.json();
    const select = document.getElementById("add-filename");
    const current = select.value;
    select.innerHTML = "";

    const defaultOpt = document.createElement("option");
    defaultOpt.value = "workarounds.txt";
    defaultOpt.textContent = "workarounds.txt (new)";
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
