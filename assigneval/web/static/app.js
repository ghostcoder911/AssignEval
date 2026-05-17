const form = document.getElementById("eval-form");
const repoInput = document.getElementById("repo");
const submitBtn = document.getElementById("submit-btn");
const errorBanner = document.getElementById("error");
const resultsSection = document.getElementById("results");
const overlay = document.getElementById("loading");
const downloadBar = document.getElementById("download-bar");
const trackInput = document.getElementById("track");
const hintC = document.getElementById("hint-c");
const hintAvr = document.getElementById("hint-avr");
const loadingMsg = document.getElementById("loading-msg");
const sessionTabs = document.querySelectorAll(".session-tab");
let lastReport = null;
let currentTrack = "c";

const TRACK_META = {
  c: { max: 270, loading: "Cloning repository, compiling & running C tests…" },
  avr: {
    max: 150,
    loading: "Cloning repository, cross-compiling AVR & checking registers…",
  },
};

sessionTabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    currentTrack = tab.dataset.track;
    trackInput.value = currentTrack;
    sessionTabs.forEach((t) => {
      const on = t === tab;
      t.classList.toggle("active", on);
      t.setAttribute("aria-selected", on ? "true" : "false");
    });
    hintC.hidden = currentTrack !== "c";
    hintAvr.hidden = currentTrack !== "avr";
    document.getElementById("score-max").textContent =
      `/ ${TRACK_META[currentTrack].max}`;
    resultsSection.classList.remove("visible");
    downloadBar.hidden = true;
    hideError();
  });
});

function showError(msg) {
  errorBanner.textContent = msg;
  errorBanner.classList.add("visible");
}

function hideError() {
  errorBanner.classList.remove("visible");
}

function setLoading(on) {
  overlay.classList.toggle("visible", on);
  submitBtn.disabled = on;
  repoInput.disabled = on;
}

function statusBadge(score, hasSource, compileOk) {
  if (!hasSource) return '<span class="badge badge-missing">Missing</span>';
  if (!compileOk) return '<span class="badge badge-fail">Compile error</span>';
  if (score >= 10) return '<span class="badge badge-pass">Full marks</span>';
  if (score > 0) return '<span class="badge badge-partial">Partial</span>';
  return '<span class="badge badge-fail">Failed</span>';
}

function renderResults(report) {
  const pct = (report.total_score / report.max_total) * 100;
  document.getElementById("score-pct").style.setProperty("--pct", pct);
  document.getElementById("score-total").textContent = report.total_score.toFixed(1);
  document.getElementById("score-max").textContent = `/ ${report.max_total}`;
  if (report.track_label) {
    const hdr = document.querySelector("header p");
    const src = report.questions_source ? ` · ${report.questions_source}` : "";
    if (hdr) hdr.textContent = `Results: ${report.track_label}${src}`;
  }
  document.getElementById("stat-full").textContent = report.summary.full_marks;
  document.getElementById("stat-partial").textContent = report.summary.partial;
  document.getElementById("stat-missing").textContent = report.summary.missing;
  document.getElementById("stat-compile").textContent = report.summary.compile_fail;
  document.getElementById("stat-matched").textContent = `${report.matched_count}/${report.questions_parsed}`;
  const repoLine = document.getElementById("repo-display");
  let label = report.repo_label || report.repo;
  if (report.search_path) {
    label += `  →  folder: ${report.search_path}`;
  }
  repoLine.textContent = label;

  const tbody = document.getElementById("results-body");
  tbody.innerHTML = "";

  report.questions.forEach((q) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>Q${String(q.number).padStart(2, "0")}</td>
      <td><strong>${q.score.toFixed(1)}</strong> / ${q.max_score}</td>
      <td>${statusBadge(q.score, !!q.source, q.compile_ok)}</td>
      <td>${q.tests_passed}/${q.tests_total || "—"}</td>
      <td title="${escapeAttr(q.source || "Not found")}">${escapeHtml(shorten(q.source || "—", 28))}</td>
      <td><button type="button" class="row-toggle" data-q="${q.number}">Details</button></td>
    `;
    tbody.appendChild(tr);

    const detail = document.createElement("tr");
    detail.className = "detail-row";
    detail.id = `detail-${q.number}`;
    detail.innerHTML = `<td colspan="6"><div class="detail-content">${buildDetail(q)}</div></td>`;
    tbody.appendChild(detail);
  });

  tbody.querySelectorAll(".row-toggle").forEach((btn) => {
    btn.addEventListener("click", () => {
      const row = document.getElementById(`detail-${btn.dataset.q}`);
      const open = row.classList.toggle("open");
      btn.textContent = open ? "Hide" : "Details";
    });
  });

  lastReport = report;
  downloadBar.hidden = false;

  resultsSection.classList.add("visible");
  resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
}

async function downloadReport(format) {
  if (!lastReport) return;
  const btn = downloadBar.querySelector(`[data-format="${format}"]`);
  if (btn) btn.disabled = true;
  try {
    const res = await fetch("/api/download", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ report: lastReport, format }),
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      showError(data.error || "Download failed.");
      return;
    }
    const blob = await res.blob();
    const disposition = res.headers.get("Content-Disposition") || "";
    const match = disposition.match(/filename="?([^";\n]+)"?/);
    const filename = match ? match[1] : `assigneval_report.${format}`;
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
    hideError();
  } catch (err) {
    showError("Could not download report.");
  } finally {
    if (btn) btn.disabled = false;
  }
}

if (downloadBar) {
  downloadBar.querySelectorAll(".btn-download").forEach((btn) => {
    btn.addEventListener("click", () => downloadReport(btn.dataset.format));
  });
}

function buildDetail(q) {
  let html = `<p style="color:var(--text);margin-bottom:0.5rem">${escapeHtml(q.title)}</p>`;
  html += "<ul>";
  q.review_comments.forEach((c) => {
    html += `<li>${escapeHtml(c)}</li>`;
  });
  html += "</ul>";
  if (q.tests && q.tests.length) {
    html += '<div class="test-list">';
    q.tests.forEach((t) => {
      const cls = t.passed ? "pass" : "fail";
      const icon = t.passed ? "✓" : "✗";
      html += `<div class="test-item ${cls}">${icon} ${escapeHtml(t.name)}: ${escapeHtml(t.detail)}</div>`;
    });
    html += "</div>";
  }
  if (!q.compile_ok && q.compile_message) {
    html += `<pre style="margin-top:0.75rem;font-size:0.75rem;overflow:auto;color:var(--fail)">${escapeHtml(q.compile_message)}</pre>`;
  }
  return html;
}

function escapeHtml(s) {
  const d = document.createElement("div");
  d.textContent = s;
  return d.innerHTML;
}

function escapeAttr(s) {
  return s.replace(/"/g, "&quot;");
}

function shorten(s, n) {
  return s.length > n ? s.slice(0, n) + "…" : s;
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  hideError();
  const repo = repoInput.value.trim();
  if (!repo) {
    showError("Please paste a Git repository URL.");
    return;
  }

  setLoading(true);
  loadingMsg.textContent = TRACK_META[currentTrack].loading;
  try {
    const res = await fetch("/api/evaluate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ repo, track: currentTrack }),
    });
    const data = await res.json();
    if (!res.ok) {
      showError(data.error || "Evaluation failed.");
      return;
    }
    renderResults(data.report);
  } catch (err) {
    showError("Could not reach the server. Is the UI running?");
  } finally {
    setLoading(false);
  }
});
