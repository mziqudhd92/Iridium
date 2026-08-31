(function () {
  const board = document.querySelector("[data-findings-board]");
  const modal = document.getElementById("term-modal");
  if (!board || !modal) return;

  const titleEl = modal.querySelector("[data-crt-title]");
  const screenEl = modal.querySelector("[data-crt-screen]");
  const closeEls = modal.querySelectorAll("[data-crt-close]");
  let lastFocus = null;

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

  function statusClass(status) {
    const value = String(status || "").toUpperCase();
    if (value === "VERIFIED" || value === "OUT_OF_BOX") return "ok";
    if (value === "SUBMISSION_READY") return "accent";
    return "";
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

  function renderBlock(block) {
    const type = block.type || "p";
    if (type === "banner") return `<div class="crt-banner">${esc(block.text)}</div>`;
    if (type === "kv") {
      return `<div class="crt-kv"><span>${esc(block.k)}</span>${esc(block.v)}</div>`;
    }
    if (type === "cmd") {
      return `<div class="crt-line"><span class="crt-prompt">sysop@iridium:~$</span> ${esc(block.text)}</div>`;
    }
    if (type === "out") return `<div class="crt-line crt-dim">${esc(block.text)}</div>`;
    if (type === "ok") return `<div class="crt-line crt-ok">✔ ${esc(block.text)}</div>`;
    if (type === "warn") return `<div class="crt-line crt-warn">! ${esc(block.text)}</div>`;
    return `<div class="crt-p">${esc(block.text)}</div>`;
  }

  function openTerminal(doc) {
    lastFocus = document.activeElement;
    titleEl.textContent = doc.title || "SYSOP TTY";
    const blocks = doc.blocks || [];
    const skipPrompt = blocks[0] && blocks[0].type === "cmd";
    const prompt = !skipPrompt && doc.prompt
      ? `<div class="crt-line"><span class="crt-prompt">sysop@iridium:~$</span> ${esc(doc.prompt)}</div>`
      : "";
    const body = blocks.map(renderBlock).join("");
    screenEl.innerHTML = `${prompt}${body}<div class="crt-line"><span class="crt-cursor" aria-hidden="true"></span></div>`;
    modal.hidden = false;
    document.body.classList.add("modal-open");
    modal.querySelector("[data-crt-close]").focus();
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

  function renderRow(entry) {
    const status = String(entry.verification_status || "").replaceAll("_", " ");
    return `<tr>
      <td>
        <div class="board-app">${esc(entry.app_name)}</div>
        <div class="board-repo">${repoCell(entry)}</div>
        <span class="board-status ${statusClass(entry.verification_status)}">${esc(status)}</span>
      </td>
      <td class="board-stars">${formatStars(entry.stars)}</td>
      <td>
        <div class="board-title">${esc(entry.finding_title)}</div>
        <div class="board-sev">${esc(entry.severity)}</div>
        <div class="board-meta">${esc(loc(entry))} · ${esc(entry.scanner_name)}</div>
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
      tbody.innerHTML = entries.map(renderRow).join("");
      tbody.querySelectorAll("[data-open]").forEach((btn) => {
        btn.addEventListener("click", () => {
          const entry = entries.find((item) => item.id === btn.getAttribute("data-id"));
          const kind = btn.getAttribute("data-open");
          if (entry && entry[kind]) openTerminal(entry[kind]);
        });
      });
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
