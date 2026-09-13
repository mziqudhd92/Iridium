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
    return `<div class="crt-line"><span class="crt-prompt">C:\\DIGGER&gt;</span> ${esc(command)}</div>`;
  }

  function cursorLine() {
    return `<div class="crt-line"><span class="crt-cursor arcade-blink" aria-hidden="true">█</span></div>`;
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

  function resolvePath(filePath) {
    if (!filePath) return filePath;
    if (filePath.startsWith("http://") || filePath.startsWith("https://") || filePath.startsWith("/")) {
      return filePath;
    }
    // Since digger is in a subfolder, relative path to findings is ../findings
    return filePath.startsWith("../") ? filePath : "../" + filePath;
  }

  async function loadFile(rawPath) {
    const path = resolvePath(rawPath);
    if (fileCache.has(path)) return fileCache.get(path);
    const response = await fetch(path);
    if (!response.ok) throw new Error(`failed to load ${path}`);
    const text = await response.text();
    fileCache.set(path, text);
    return text;
  }

  function addScore(points) {
    const scoreEl = document.getElementById("hud-score");
    if (!scoreEl) return;
    const current = parseInt(scoreEl.textContent.replace(/\D/g, ""), 10) || 84620;
    const updated = current + points;
    scoreEl.textContent = String(updated).padStart(6, "0");
    scoreEl.classList.add("score-pop");
    setTimeout(() => scoreEl.classList.remove("score-pop"), 400);
  }

  async function openTerminal(doc) {
    lastFocus = document.activeElement;
    titleEl.textContent = doc.title || "DIGGER TTY // 1983 IBM-PC";
    screenEl.innerHTML = `<div class="crt-line crt-dim"><span class="arcade-blink">READING SECTOR DISK…</span></div>`;
    modal.hidden = false;
    document.body.classList.add("modal-open");
    const closeBtn = modal.querySelector("[data-crt-close]");
    if (closeBtn) closeBtn.focus();

    if (window.DiggerAudio) window.DiggerAudio.playTerminal();
    addScore(250);

    try {
      if (doc.file) {
        const raw = await loadFile(doc.file);
        const text = doc.kind === "code" ? raw : stripReportSections(raw);
        const name = doc.file.split("/").pop();
        const command = doc.kind === "code" ? `TYPE ${name}` : `MORE < ${name}`;
        const body = doc.kind === "code" ? renderCode(text) : renderMarkdown(text);
        screenEl.innerHTML = `${promptLine(command)}${body}${cursorLine()}`;
        return;
      }
      const blocks = doc.blocks || [];
      const skipPrompt = blocks[0] && blocks[0].type === "cmd";
      const prompt = !skipPrompt && doc.prompt ? promptLine(doc.prompt) : "";
      screenEl.innerHTML = `${prompt}${blocks.map(renderBlock).join("")}${cursorLine()}`;
    } catch (err) {
      screenEl.innerHTML = `<div class="crt-line crt-warn">! DISK ERROR: ${esc(err.message || err)}</div>${cursorLine()}`;
    }
  }

  function closeTerminal() {
    modal.hidden = true;
    document.body.classList.remove("modal-open");
    screenEl.innerHTML = "";
    if (window.DiggerAudio) window.DiggerAudio.playBlip();
    if (lastFocus && typeof lastFocus.focus === "function") lastFocus.focus();
  }

  function actionButton(kind, entry) {
    if (kind === "report") {
      if (!entry.report) return `<span class="board-na">—</span>`;
      return `<a href="#" class="btn board-btn btn-report" data-open="report" data-id="${esc(entry.id)}" role="button"><span class="btn-icon">📜</span> VIEW REPORT</a>`;
    }
    if (!entry.poc) return `<span class="board-na">—</span>`;
    return `<a href="#" class="btn ghost board-btn btn-poc" data-open="poc" data-id="${esc(entry.id)}" role="button"><span class="btn-icon">⛏️</span> GET POC</a>`;
  }

  function renderSevBadge(sev) {
    const s = String(sev || "").toLowerCase();
    let badgeClass = "sev-low";
    let icon = "🍒";
    if (s.includes("crit")) {
      badgeClass = "sev-critical";
      icon = "👾";
    } else if (s.includes("high")) {
      badgeClass = "sev-high";
      icon = "💰";
    } else if (s.includes("med")) {
      badgeClass = "sev-medium";
      icon = "💎";
    }
    return `<div class="board-sev ${badgeClass}"><span class="sev-icon">${icon}</span> ${esc(sev)}</div>`;
  }

  function renderRankBadge(idx) {
    const rank = idx + 1;
    let rankClass = "rank-other";
    let icon = "⛏️";
    if (rank === 1) { rankClass = "rank-1st"; icon = "👑"; }
    else if (rank === 2) { rankClass = "rank-2nd"; icon = "🥈"; }
    else if (rank === 3) { rankClass = "rank-3rd"; icon = "🥉"; }
    return `<span class="board-rank ${rankClass}"><span class="rank-ico">${icon}</span> #${String(rank).padStart(2, "0")}</span>`;
  }

  function renderRow(entry, idx) {
    const pocFileName = entry.poc && entry.poc.file ? entry.poc.file.split("/").pop() : "";
    const pocLinkHtml = entry.poc ? `
      <div class="board-poc-row">
        <a href="#" class="board-poc-link" data-open="poc" data-id="${esc(entry.id)}" title="View Proof of Concept">
          <span>⛏️</span> PROOF OF CONCEPT: <code>${esc(pocFileName)}</code>
        </a>
      </div>` : "";

    return `<tr>
      <td>
        <div class="board-app-row">
          ${renderRankBadge(idx)}
          <span class="board-app">${esc(entry.app_name)}</span>
        </div>
        <div class="board-repo">${repoCell(entry)}</div>
      </td>
      <td class="board-stars">
        <span class="gem-sparkle">💎</span> ${formatStars(entry.stars)}
      </td>
      <td>
        <div class="board-title">${esc(entry.finding_title)}</div>
        ${renderSevBadge(entry.severity)}
        <div class="board-meta">${esc(loc(entry))} · ${esc(entry.scanner_name)}</div>
        <p class="board-sum">${esc(entry.finding_summary)}</p>
        ${pocLinkHtml}
      </td>
      <td>${actionButton("report", entry)}</td>
      <td>${actionButton("poc", entry)}</td>
    </tr>`;
  }

  async function loadBoard() {
    const tbody = board.querySelector("[data-findings-rows]");
    try {
      const candidates = ["../findings.json", "findings.json", "/findings.json"];
      let payload = null;
      for (const url of candidates) {
        try {
          const res = await fetch(url, { headers: { Accept: "application/json" } });
          if (res.ok) {
            payload = await res.json();
            break;
          }
        } catch (_) {}
      }
      if (!payload) throw new Error("Could not load findings.json");
      const entries = Array.isArray(payload.entries) ? payload.entries : [];
      tbody.innerHTML = entries.map((entry, idx) => renderRow(entry, idx)).join("");
      tbody.querySelectorAll("[data-open]").forEach((btn) => {
        btn.addEventListener("click", (e) => {
          e.preventDefault();
          if (window.DiggerAudio) window.DiggerAudio.playBlip();
          const entry = entries.find((item) => item.id === btn.getAttribute("data-id"));
          const kind = btn.getAttribute("data-open");
          if (entry && entry[kind]) void openTerminal(entry[kind]);
        });
      });
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="5" class="board-empty"><span class="arcade-blink">UNABLE TO LOAD FINDINGS TABLE.</span> ${esc(err.message || err)}</td></tr>`;
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

  // Audio Toggle Button logic
  const soundBtn = document.getElementById("sound-toggle");
  if (soundBtn) {
    soundBtn.addEventListener("click", () => {
      if (window.DiggerAudio) {
        const on = window.DiggerAudio.toggle();
        soundBtn.textContent = on ? "🔊 SFX: ON" : "🔈 SFX: OFF";
        soundBtn.classList.toggle("sfx-active", on);
      }
    });
  }

  // Copy button hook with audio & score
  document.querySelectorAll(".copy").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const raw = btn.getAttribute("data-copy") || "";
      const text = raw.replaceAll("&lt;", "<").replaceAll("&gt;", ">");
      if (window.DiggerAudio) window.DiggerAudio.playGold();
      addScore(100);
      try {
        await navigator.clipboard.writeText(text);
        btn.textContent = "COPIED!";
      } catch {
        btn.textContent = "DONE";
      }
      setTimeout(() => { btn.textContent = "COPY"; }, 1600);
    });
  });
})();
