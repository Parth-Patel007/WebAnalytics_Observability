// main.js

// Simple in-memory "curriculum" definition.
// Later, when we build a module fully, we only update this array.
const modules = [
  {
    id: "m0",
    title: "Course Overview",
    part: "Module 0",
    duration: "0.5 hr",
    status: "Ready",
    tags: ["intro", "structure"],
    description:
      "High-level overview of the course, tools required, and how to navigate the modules.",
    // path can be added later when Module 0 exists
    path: "modules/module-00-course-overview/index.html",
  },
  {
    id: "m1",
    title: "Introduction to Web Analytics",
    part: "Module 1 - Foundations",
    duration: "1 hr",
    status: "Ready",
    tags: ["analytics", "basics"],
    description:
      "Learn what web analytics is, why it matters, and understand basic concepts like page views, sessions, and user journeys.",
    path: "modules/module-01-web-analytics/index.html",
  },
  {
    id: "m2",
    title: "Introduction to Observability",
    part: "Module 2 - Foundations",
    duration: "1 hr",
    status: "Ready",
    tags: ["observability", "basics"],
    description:
      "Explore the concept of observability, how it's different from monitoring, and understand metrics, logs, and traces.",
    path: "modules/module-02-observability/index.html",
  },

  {
    id: "m3",
    title: "Telemetry in Web Applications",
    part: "Module 3 - Foundations",
    duration: "1 hr",
    status: "Ready",
    tags: ["telemetry", "frontend", "backend"],
    description:
      "Understand how web apps generate telemetry on the client and server, and how that data flows into your observability stack.",
    path: "modules/module-03-telemetry/index.html",
  },
  {
  id: "m4",
  title: "Prometheus - Metrics & Monitoring",
  part: "Module 4 — Tooling",
  duration: "3 hrs",
  status: "Ready",
  tags: ["prometheus", "metrics"],
  description:
    "Learn how to collect, store, and query time-series metrics using Prometheus.",
  path: "modules/module-04-prometheus/index.html",
},
{
  id: "m5",
  title: "Loki - Logs for Observability",
  part: "Module 5 — Tooling",
  duration: "3 hrs",
  status: "Ready",
  tags: ["loki", "logs"],
  description:
    "Learn how to aggregate and query logs with Loki, and connect it to Grafana.",
  path: "modules/module-05-loki/index.html",
},
{
  id: "m6",
  title: "OpenTelemetry - Unified Telemetry",
  part: "Module 6 — Tooling",
  duration: "3 hrs",
  status: "Ready",
  tags: ["opentelemetry", "traces", "metrics"],
  description:
    "Learn how to instrument services with OpenTelemetry and export metrics and traces.",
  path: "modules/module-06-opentelemetry/index.html",
},
{
  id: "m7",
  title: "Grafana - Dashboards & Visualization",
  part: "Module 7 — Tooling",
  duration: "3 hrs",
  status: "Ready",
  tags: ["grafana", "dashboards"],
  description:
    "Learn how to build dashboards that visualize metrics and logs from Prometheus and Loki.",
  path: "modules/module-07-grafana/index.html",
},
{
  id: "m8",
  title: "Guided Project",
  part: "Module 8 — Project",
  duration: "Self paced",
  status: "Ready",
  tags: ["Prometheus","loki", "Otel","grafana", "dashboards","Self-paced", "Project"],
  description:
    "Working on a self paced guided project.",
  path: "modules/module-08-guided-project/index.html",
},
  // ...
];

let activeModuleId = null;

// DOM helpers
function $(selector) {
  return document.querySelector(selector);
}

function formatStatus(status) {
  // Later we can make this more complex (e.g., "Ready", "In progress", etc.)
  return status;
}

// Rendering module list
function renderModuleList() {
  const listEl = $("#module-list");
  listEl.innerHTML = "";

  modules.forEach((mod) => {
    const item = document.createElement("button");
    item.type = "button";
    item.className = "module-list-item";
    item.dataset.id = mod.id;

    item.innerHTML = `
      <div class="module-main">
        <div class="module-title-small">${mod.title}</div>
        <div class="module-meta">
          ${mod.part} • ${mod.duration}
        </div>
      </div>
      <span class="module-status">${formatStatus(mod.status)}</span>
    `;

    item.addEventListener("click", () => {
      setActiveModule(mod.id);
    });

    listEl.appendChild(item);
  });

  // Once we know how many modules we have, update progress total
  const totalLabel = $("#progress-total");
  if (totalLabel) {
    totalLabel.textContent = modules.length;
  }
}

// Progress logic (placeholder for now)
function setActiveModule(id) {
  activeModuleId = id;
  const mod = modules.find((m) => m.id === id);
  if (!mod) return;

  // Highlight selection in list
  document
    .querySelectorAll(".module-list-item")
    .forEach((el) => el.classList.remove("active"));
  const activeButton = document.querySelector(
    `.module-list-item[data-id="${id}"]`
  );
  if (activeButton) {
    activeButton.classList.add("active");
  }

  // Update detail panel
  $("#module-title").textContent = mod.title;
  $("#module-duration").textContent = `${mod.part} • ${mod.duration}`;
  $("#module-description").textContent = mod.description;

  const tagsContainer = $("#module-tags");
  tagsContainer.innerHTML = "";
  (mod.tags || []).forEach((tag) => {
    const span = document.createElement("span");
    span.className = "module-tag";
    span.textContent = tag;
    tagsContainer.appendChild(span);
  });

  const openBtn = $("#btn-open-module");
  openBtn.disabled = false;
  openBtn.textContent = "Open Module";
}

function getCompletedModuleCount() {
  let count = 0;

  // There are modules 0 to 9 (10 modules total)
  for (let i = 0; i <= 9; i++) {
    const key = `wao_module_${i}_complete`;
    const value = localStorage.getItem(key);

    if (value === "true") {
      count++;
    }
  }

  return count;
}

function updateProgressUI() {
  const completed = getCompletedModuleCount();
  const total = modules.length;

  const countLabel = $("#progress-count");
  const totalLabel = $("#progress-total");
  const barFill = $("#progress-bar-fill");
  const note = $("#progress-note");

  if (countLabel) countLabel.textContent = completed;
  if (totalLabel) totalLabel.textContent = total;

  const percent = total > 0 ? (completed / total) * 100 : 0;
  if (barFill) {
    barFill.style.width = `${percent}%`;
  }

  if (note) {
    if (completed === 0) {
      note.textContent =
        "You haven't started yet. Begin with Module 1: Introduction to Web Analytics.";
    } else {
      note.textContent = `You have completed ${completed} out of ${total} modules.`;
    }
  }
}

// ----- Button events -----
function setupButtons() {
  const startBtn = $("#btn-start");
  const continueBtn = $("#btn-continue");
  const openModuleBtn = $("#btn-open-module");

  if (startBtn) {
    startBtn.addEventListener("click", () => {
      // Scroll to modules and select the first one
      document.getElementById("modules").scrollIntoView({ behavior: "smooth" });
      if (modules.length > 0) {
        setTimeout(() => setActiveModule(modules[0].id), 200);
      }
    });
  }

  if (continueBtn) {
    continueBtn.addEventListener("click", () => {
      // Later we can look up the last visited module (from localStorage).
      // For now, just scroll to modules.
      document.getElementById("modules").scrollIntoView({ behavior: "smooth" });
    });
  }

  if (openModuleBtn) {
    openModuleBtn.addEventListener("click", () => {
      if (!activeModuleId) return;
      const mod = modules.find((m) => m.id === activeModuleId);
      if (!mod) return;

      if (mod.path) {
        window.location.href = mod.path;
      } else {
        alert(
          `Module "${mod.title}" doesn't have a page yet. It will be added soon.`
        );
      }
    });
  }
}

// Init
document.addEventListener("DOMContentLoaded", () => {
  renderModuleList();
  updateProgressUI();
  setupButtons();
});
