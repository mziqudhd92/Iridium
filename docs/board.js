(function () {
  const board = document.querySelector("[data-findings-board]");
  const modal = document.getElementById("term-modal");
  if (!board || !modal) return;

  const titleEl = modal.querySelector("[data-crt-title]");
  const screenEl = modal.querySelector("[data-crt-screen]");
  const closeEls = modal.querySelectorAll("[data-crt-close]");
  let lastFocus = null;
  const fileCache = new Map();

  function esc(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  function formatStars(stars) {
    if (stars == null) return "—";
    return Number(stars).toLocaleString("en-US");
  }

  function repoCell(entry) {
    const url = entry.repo_url || "";
    if (url.startsWith("http")) {
      return `<a href="${esc(url)}" target="_blank" rel="noopener noreferrer">${esc(url)}</a>`;
    }
    return `<span>${esc(url)}</span>`;
  }

  function loc(entry) {
    const file = entry.file_path || "";
    const line = entry.line_number ? `:${entry.line_number}` : "";
    return file ? `${file}${line}` : "—";
  }

  function inlineFmt(text) {
    return esc(text)
      .replace(/`([^`]+)`/g, "<code>$1</code>")
      .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  }

  function promptLine(command) {
    return `<div class="crt-line"><span class="crt-prompt">sysop@iridium:~$</span> ${esc(command)}</div>`;
  }

  function cursorLine() {
    return `<div class="crt-line"><span class="crt-cursor" aria-hidden="true"></span></div>`;
  }

  function renderCode(src) {
    const lines = String(src).replace(/\n$/, "").split("\n");
    const body = lines
      .map((line, i) => {
        const n = String(i + 1).padStart(3, " ");
        return `<div class="crt-code-line"><span class="n">${n}</span><span class="src">${esc(line) || " "}</span></div>`;
      })
      .join("");
    return `<pre class="crt-code">${body}</pre>`;
  }

  function renderMdText(text) {
    const chunks = String(text).trim().split(/\n{2,}/);
    return chunks
      .map((chunk) => {
        const lines = chunk.split("\n");
        const first = lines[0] || "";
        if (first.startsWith("# ")) {
          return `<div class="crt-banner">${inlineFmt(first.replace(/^#\s+/, ""))}</div>`;
        }
        if (first.startsWith("## ")) {
          const rest = lines.slice(1).join("\n");
          const head = `<div class="crt-h">${inlineFmt(first.replace(/^##\s+/, ""))}</div>`;
          return rest ? `${head}<div class="crt-p">${rest.split("\n").map(inlineFmt).join("<br>")}</div>` : head;
        }
        if (lines.every((line) => /^[-*]\s+/.test(line))) {
          const items = lines
            .map((line) => `<li>${inlineFmt(line.replace(/^[-*]\s+/, ""))}</li>`)
            .join("");
          return `<ul class="crt-list">${items}</ul>`;
        }
        return `<div class="crt-p">${lines.map(inlineFmt).join("<br>")}</div>`;
      })
      .join("");
  }

  function stripReportSections(md) {
    return String(md).replace(
      /\n## Standalone Proof of Concept[^\n]*[\s\S]*?(?=\n## |\s*$)/i,
      "",
    ).replace(
      /\n## AddressSanitizer Backtrace[^\n]*[\s\S]*?(?=\n## |\s*$)/i,
      "",
    ).trim();
  }

  function renderMarkdown(md) {
    const parts = [];
    const re = /```[^\n]*\n([\s\S]*?)```/g;
    let last = 0;
    let match;
    while ((match = re.exec(md))) {
      parts.push(renderMdText(md.slice(last, match.index)));
      parts.push(renderCode(match[1]));
      last = match.index + match[0].length;
    }
    parts.push(renderMdText(md.slice(last)));
    return parts.join("");
  }

  function renderBlock(block) {
    const type = block.type || "p";
    if (type === "banner") return `<div class="crt-banner">${esc(block.text)}</div>`;
    if (type === "kv") {
      return `<div class="crt-kv"><span>${esc(block.k)}</span>${esc(block.v)}</div>`;
    }
    if (type === "cmd") {
      return promptLine(block.text);
    }
    if (type === "out") return `<div class="crt-line crt-dim">${esc(block.text)}</div>`;
    if (type === "ok") return `<div class="crt-line crt-ok">✔ ${esc(block.text)}</div>`;
    if (type === "warn") return `<div class="crt-line crt-warn">! ${esc(block.text)}</div>`;
    return `<div class="crt-p">${esc(block.text)}</div>`;
  }

  async function loadFile(path) {
    if (fileCache.has(path)) return fileCache.get(path);
    const response = await fetch(path);
    if (!response.ok) throw new Error(`failed to load ${path}`);
    const text = await response.text();
    fileCache.set(path, text);
    return text;
  }

  async function openTerminal(doc) {
    lastFocus = document.activeElement;
    titleEl.textContent = doc.title || "SYSOP TTY";
    screenEl.innerHTML = `<div class="crt-line crt-dim">loading…</div>`;
    modal.hidden = false;
    document.body.classList.add("modal-open");
    modal.querySelector("[data-crt-close]").focus();

    try {
      if (doc.file) {
        const raw = await loadFile(doc.file);
        const text = doc.kind === "code" ? raw : stripReportSections(raw);
        const name = doc.file.split("/").pop();
        const command = doc.kind === "code" ? `cat ${name}` : `less ${name}`;
        const body = doc.kind === "code" ? renderCode(text) : renderMarkdown(text);
        screenEl.innerHTML = `${promptLine(command)}${body}${cursorLine()}`;
        return;
      }
      const blocks = doc.blocks || [];
      const skipPrompt = blocks[0] && blocks[0].type === "cmd";
      const prompt = !skipPrompt && doc.prompt ? promptLine(doc.prompt) : "";
      screenEl.innerHTML = `${prompt}${blocks.map(renderBlock).join("")}${cursorLine()}`;
    } catch (err) {
      screenEl.innerHTML = `<div class="crt-line crt-warn">! ${esc(err.message || err)}</div>${cursorLine()}`;
    }
  }

  function closeTerminal() {
    modal.hidden = true;
    document.body.classList.remove("modal-open");
    screenEl.innerHTML = "";
    if (lastFocus && typeof lastFocus.focus === "function") lastFocus.focus();
  }

  function actionButton(kind, entry) {
    if (kind === "report") {
      if (!entry.report) return "";
      return `<button type="button" class="btn board-btn" data-open="report" data-id="${esc(entry.id)}">View Report</button>`;
    }
    if (!entry.poc) return "";
    return `<button type="button" class="btn ghost board-btn" data-open="poc" data-id="${esc(entry.id)}">Get PoC</button>`;
  }

  function extractCves(entry) {
    const text = `${entry.finding_title || ""} ${entry.finding_summary || ""}`;
    const matches = text.match(/CVE-\d{4}-\d{4,}/g) || [];
    return Array.from(new Set(matches));
  }

  function inferEcosystem(entry) {
    const rule = String(entry.scanner_name || "").toLowerCase();
    const repo = String(entry.repo_url || "").toLowerCase();
    const file = String(entry.file_path || "").toLowerCase();
    if (
      rule.startsWith("wp.") ||
      repo.includes("wordpress") ||
      file.endsWith(".php")
    ) {
      return "wordpress";
    }
    if (
      rule.startsWith("native.") ||
      rule.startsWith("evm.") ||
      file.endsWith(".c") ||
      file.endsWith(".cpp") ||
      file.endsWith(".sol")
    ) {
      return "native";
    }
    return "python";
  }

  function renderRow(entry) {
    const cves = extractCves(entry);
    const cveBadges = cves
      .map(
        (cve) =>
          `<button type="button" class="board-cve-pill" data-open="report" data-id="${esc(entry.id)}" title="Open briefing for ${esc(cve)}">${esc(cve)}</button>`
      )
      .join("");
    const statusBadge = entry.verification_status
      ? `<span class="board-status ${entry.verification_status === "SUBMISSION_READY" ? "accent" : ""}">${esc(entry.verification_status)}</span>`
      : "";
    return `<tr>
      <td>
        <div class="board-app">${esc(entry.app_name)}</div>
        <div class="board-repo">${repoCell(entry)}</div>
        ${statusBadge}
      </td>
      <td class="board-stars">${formatStars(entry.stars)}</td>
      <td>
        <div class="board-title">${esc(entry.finding_title)}</div>
        <div class="board-badges-row">
          <span class="board-sev sev-${esc(String(entry.severity || "high").toLowerCase())}">${esc(entry.severity)}</span>
          ${cveBadges}
        </div>
        <div class="board-meta">${esc(loc(entry))} · <code>${esc(entry.scanner_name)}</code></div>
        <p class="board-sum">${esc(entry.finding_summary)}</p>
      </td>
      <td>${actionButton("report", entry)}</td>
      <td>${actionButton("poc", entry)}</td>
    </tr>`;
  }

  async function loadBoard() {
    const tbody = board.querySelector("[data-findings-rows]");
    try {
      const response = await fetch("findings.json", { headers: { Accept: "application/json" } });
      if (!response.ok) throw new Error(`status ${response.status}`);
      const payload = await response.json();
      const entries = Array.isArray(payload.entries) ? payload.entries : [];

      const allCves = new Set();
      entries.forEach((e) => extractCves(e).forEach((c) => allCves.add(c)));
      const critCount = entries.filter((e) => String(e.severity).toLowerCase() === "critical").length;
      const highCount = entries.filter((e) => String(e.severity).toLowerCase() === "high").length;

      let activeFilter = "all";
      let searchQuery = "";
      let showAll = false;
      const INITIAL_LIMIT = 25;

      const toolbar = document.createElement("div");
      toolbar.className = "board-toolbar";
      toolbar.innerHTML = `
        <div class="board-kpis">
          <span class="board-kpi"><strong>${entries.length}</strong> Verified Findings</span>
          <span class="board-kpi"><strong>${allCves.size}</strong> Unique CVEs Indexed</span>
          <span class="board-kpi"><strong>${critCount}</strong> Critical · <strong>${highCount}</strong> High</span>
          <span class="board-kpi ok">100% Report + PoC Artifacts</span>
        </div>
        <div class="board-controls">
          <input
            type="search"
            class="board-search"
            placeholder="Search CVE (e.g. CVE-2026-75816), app, plugin, rule, or file path…"
            aria-label="Filter verified findings and CVEs"
            data-board-search
          />
          <div class="board-filters" role="group" aria-label="Filter by severity or ecosystem">
            <button type="button" class="board-filter active" data-filter="all">All (${entries.length})</button>
            <button type="button" class="board-filter" data-filter="critical">Critical (${critCount})</button>
            <button type="button" class="board-filter" data-filter="high">High (${highCount})</button>
            <button type="button" class="board-filter" data-filter="wordpress">WordPress</button>
            <button type="button" class="board-filter" data-filter="python">Python / AI</button>
            <button type="button" class="board-filter" data-filter="native">Native C / EVM</button>
          </div>
        </div>
      `;
      board.parentNode.insertBefore(toolbar, board);

      const footerWrap = document.createElement("div");
      footerWrap.className = "board-footer";
      board.parentNode.insertBefore(footerWrap, board.nextSibling);

      function bindOpenButtons() {
        tbody.querySelectorAll("[data-open]").forEach((btn) => {
          btn.addEventListener("click", () => {
            const entry = entries.find((item) => item.id === btn.getAttribute("data-id"));
            const kind = btn.getAttribute("data-open");
            if (entry && entry[kind]) void openTerminal(entry[kind]);
          });
        });
      }

      function updateView() {
        const q = searchQuery.trim().toLowerCase();
        const filtered = entries.filter((entry) => {
          const sev = String(entry.severity || "").toLowerCase();
          const eco = inferEcosystem(entry);
          if (activeFilter === "critical" && sev !== "critical") return false;
          if (activeFilter === "high" && sev !== "high") return false;
          if (activeFilter === "wordpress" && eco !== "wordpress") return false;
          if (activeFilter === "python" && eco !== "python") return false;
          if (activeFilter === "native" && eco !== "native") return false;
          if (!q) return true;
          const hay = `${entry.app_name} ${entry.finding_title} ${entry.finding_summary} ${entry.file_path} ${entry.scanner_name} ${entry.repo_url}`.toLowerCase();
          return hay.includes(q);
        });

        const isFiltering = Boolean(q) || activeFilter !== "all";
        const visible = isFiltering || showAll ? filtered : filtered.slice(0, INITIAL_LIMIT);

        if (!visible.length) {
          tbody.innerHTML = `<tr><td colspan="5" class="board-empty">No findings match "${esc(searchQuery)}".</td></tr>`;
        } else {
          tbody.innerHTML = visible.map(renderRow).join("");
          bindOpenButtons();
        }

        if (!isFiltering && filtered.length > INITIAL_LIMIT) {
          footerWrap.innerHTML = `
            <button type="button" class="btn ghost board-more-btn" data-board-toggle>
              ${showAll ? `Show Featured Top ${INITIAL_LIMIT}` : `Show All ${filtered.length} Verified Findings (${allCves.size} CVEs)`}
            </button>
          `;
          const toggleBtn = footerWrap.querySelector("[data-board-toggle]");
          if (toggleBtn) {
            toggleBtn.addEventListener("click", () => {
              showAll = !showAll;
              updateView();
            });
          }
        } else {
          footerWrap.innerHTML = `<span class="board-count-note">Showing ${visible.length} of ${entries.length} verified findings (${allCves.size} unique CVEs)</span>`;
        }
      }

      const searchInput = toolbar.querySelector("[data-board-search]");
      if (searchInput) {
        searchInput.addEventListener("input", (e) => {
          searchQuery = e.target.value || "";
          updateView();
        });
      }

      toolbar.querySelectorAll("[data-filter]").forEach((btn) => {
        btn.addEventListener("click", () => {
          activeFilter = btn.getAttribute("data-filter") || "all";
          toolbar.querySelectorAll("[data-filter]").forEach((b) => b.classList.remove("active"));
          btn.classList.add("active");
          updateView();
        });
      });

      updateView();
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="5" class="board-empty">Unable to load findings board. ${esc(err.message || err)}</td></tr>`;
    }
  }

  closeEls.forEach((el) => el.addEventListener("click", closeTerminal));
  modal.addEventListener("click", (event) => {
    if (event.target === modal) closeTerminal();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !modal.hidden) closeTerminal();
  });

  loadBoard();
})();
