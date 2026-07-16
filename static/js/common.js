function showStatus(el, type, message) {
  el.className = `status ${type}`;
  el.textContent = message;
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function initResultCards() {
  document.querySelectorAll(".result-card-toggle").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const card = btn.closest(".result-card");
      const isExpanded = btn.getAttribute("aria-expanded") === "true";

      if (isExpanded) {
        collapseResultCard(card);
        return;
      }

      document.querySelectorAll(".result-card.expanded").forEach((openCard) => {
        if (openCard !== card) collapseResultCard(openCard);
      });
      expandResultCard(card);
    });
  });

  initTuxedoToggles();
}

function expandResultCard(card) {
  const btn = card.querySelector(".result-card-toggle");
  const body = card.querySelector(".result-card-body");
  const icon = btn.querySelector(".result-expand-icon");

  card.classList.remove("collapsed");
  card.classList.add("expanded");
  btn.setAttribute("aria-expanded", "true");
  body.classList.remove("collapsed");
  body.classList.add("expanded");
  if (icon) icon.textContent = "▲";
}

function collapseResultCard(card) {
  const btn = card.querySelector(".result-card-toggle");
  const body = card.querySelector(".result-card-body");
  const icon = btn.querySelector(".result-expand-icon");

  card.classList.add("collapsed");
  card.classList.remove("expanded");
  btn.setAttribute("aria-expanded", "false");
  body.classList.add("collapsed");
  body.classList.remove("expanded");
  if (icon) icon.textContent = "▼";
}

function initTuxedoToggles() {
  document.querySelectorAll(".tuxedo-toggle").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const panel = btn.nextElementSibling;
      const expanded = btn.getAttribute("aria-expanded") === "true";
      const willExpand = !expanded;

      btn.setAttribute("aria-expanded", String(willExpand));
      btn.classList.toggle("expanded", willExpand);
      panel.classList.toggle("collapsed", !willExpand);
      panel.classList.toggle("expanded", willExpand);

      const action = btn.querySelector(".tuxedo-toggle-action");
      if (action) {
        action.textContent = willExpand ? "Collapse ▲" : "Expand ▼";
      }
    });
  });
}

function initTabs() {
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");
      document.querySelectorAll(".panel").forEach((p) => p.classList.remove("active"));
      document.getElementById(`panel-${tab.dataset.tab}`).classList.add("active");
    });
  });
}
