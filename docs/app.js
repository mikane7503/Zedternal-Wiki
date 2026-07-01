let DATA = null;
let ADV_BY_KEY = {};
let BASE_BY_KEY = {};
let OPEN_BASE_KEY = null;
let SELECTED_ADV_KEY = null;

const LEVELS = [5, 10, 15, 20];

function el(tag, attrs = {}, children = []) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") node.className = v;
    else if (k === "html") node.innerHTML = v;
    else if (k === "text") node.textContent = v;
    else node.setAttribute(k, v);
  }
  for (const c of [].concat(children)) {
    if (c) node.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
  }
  return node;
}

function iconImg(perk, size) {
  return el("img", {
    class: `icon-img ${size || ""}`,
    src: perk.icon,
    alt: perk.name,
    loading: "lazy",
    onerror: "this.style.visibility='hidden'",
  });
}

async function init() {
  const res = await fetch("data/perks.json");
  DATA = await res.json();
  ADV_BY_KEY = Object.fromEntries(DATA.advancedPerks.map(p => [p.key, p]));
  BASE_BY_KEY = Object.fromEntries(DATA.basePerks.map(p => [p.key, p]));

  document.getElementById("meta").textContent =
    `오퍼(기본 퍽) ${DATA.meta.basePerkCount}개 · 커퍼(전직 퍽) ${DATA.meta.advancedPerkCount}개 · 전직 스킬 ${DATA.meta.totalSkills}개 수록`;

  renderSidebar();
  renderMainArea();
  document.getElementById("searchBox").addEventListener("input", onSearch);
}

function showBaseOverview(key) {
  OPEN_BASE_KEY = key;
  SELECTED_ADV_KEY = null;
  renderSidebar();
  renderMainArea();
}

function selectAdv(key) {
  const adv = ADV_BY_KEY[key];
  OPEN_BASE_KEY = adv.parentPerk;
  SELECTED_ADV_KEY = key;
  renderSidebar();
  renderMainArea();
  document.getElementById("mainArea").scrollIntoView({ behavior: "instant", block: "start" });
}

function renderSidebar() {
  const sidebar = document.getElementById("sidebar");
  sidebar.innerHTML = "";
  for (const base of DATA.basePerks) {
    const isOpen = base.key === OPEN_BASE_KEY;
    const item = el("div", { class: `accordion-item ${isOpen ? "open" : ""}`, "data-basekey": base.key });

    const header = el("div", { class: "accordion-header" }, [
      iconImg(base, "sm"),
      el("div", { class: "titles" }, [
        el("h3", { text: base.name }),
        el("div", { class: "grade", html: base.grade ? `등급 ${gradeBadge(base.grade)}` : "" }),
      ]),
      el("span", { class: "chevron", text: "▸" }),
    ]);
    header.addEventListener("click", () => showBaseOverview(base.key));
    item.appendChild(header);

    const body = el("div", { class: "accordion-body" });
    const unlockByLevel = Object.fromEntries(base.unlocks.map(u => [u.level, u]));
    for (const lvl of LEVELS) {
      const u = unlockByLevel[lvl];
      if (!u) continue;
      const adv = ADV_BY_KEY[u.perk];
      const row = el("div", {
        class: `child-row ${adv.key === SELECTED_ADV_KEY ? "active" : ""}`,
        "data-advkey": adv.key,
        "data-search": buildSearchCorpus(adv, base),
      }, [
        iconImg(adv, "sm"),
        el("span", { class: "lvl", text: `Lv${lvl}` }),
        el("span", { class: "name", text: adv.name }),
      ]);
      if (adv.grade) row.appendChild(el("span", { class: "grade-badge-wrap", html: gradeBadge(adv.grade) }));
      row.addEventListener("click", (e) => { e.stopPropagation(); selectAdv(adv.key); });
      body.appendChild(row);
    }
    item.appendChild(body);
    sidebar.appendChild(item);
  }
}

function renderMainArea() {
  const main = document.getElementById("mainArea");
  main.innerHTML = "";

  if (SELECTED_ADV_KEY) {
    main.appendChild(renderAdvDetail(SELECTED_ADV_KEY));
    wireDetailEvents(main);
    return;
  }
  if (OPEN_BASE_KEY) {
    main.appendChild(renderBaseDetail(OPEN_BASE_KEY));
    wireDetailEvents(main);
    return;
  }
  main.appendChild(el("div", { class: "empty-state", text: "왼쪽에서 오퍼(기본 퍽)를 선택하면 전직 트리가 펼쳐집니다." }));
}

function wireDetailEvents(root) {
  root.querySelectorAll(".unlock-chip").forEach(chip => {
    chip.addEventListener("click", () => selectAdv(chip.dataset.advkey));
  });
  root.querySelectorAll(".back-link").forEach(b => {
    b.addEventListener("click", () => showBaseOverview(b.dataset.basekey));
  });
  const slider = root.querySelector("#levelSlider");
  if (slider) slider.addEventListener("input", onLevelSlide);
}

function buildSearchCorpus(adv, base) {
  const parts = [adv.name, adv.key, base.name];
  for (const d of adv.descriptions) parts.push(d.text);
  for (const s of adv.skills) {
    parts.push(s.name, s.key, s.standardDesc || "", s.deluxeDesc || "");
  }
  return parts.join(" ").toLowerCase();
}

function renderBaseDetail(key) {
  const p = BASE_BY_KEY[key];
  const wrap = document.createDocumentFragment();
  const container = el("div", {});

  const strengths = p.strengths.length
    ? `<ul class="strengths">${p.strengths.map(s => `<li>${escapeHtml(s)}</li>`).join("")}</ul>` : "";
  const weaknesses = p.weaknesses.map(w =>
    `<div class="weak-item"><span class="sev-${w.severity}">${escapeHtml(w.skill)}</span> — ${escapeHtml(w.issue)}</div>`
  ).join("");

  const grid = el("div", { class: "adv-grid" });
  const unlockByLevel = Object.fromEntries(p.unlocks.map(u => [u.level, u]));
  for (const lvl of LEVELS) {
    const u = unlockByLevel[lvl];
    if (!u) continue;
    const adv = ADV_BY_KEY[u.perk];
    const card = el("div", {
      class: "adv-card",
      "data-advkey": adv.key,
      "data-search": buildSearchCorpus(adv, p),
    }, [
      iconImg(adv),
      el("div", { class: "adv-body" }, [
        el("div", { class: "lvl", text: `Lv${lvl} 전직` }),
        el("div", { class: "name", text: adv.name }),
        el("div", { class: "skillcount", text: `스킬 ${adv.skillCount}개` }),
      ]),
    ]);
    if (adv.grade) card.appendChild(el("span", { class: "grade-badge-wrap", html: gradeBadge(adv.grade) }));
    card.addEventListener("click", () => selectAdv(adv.key));
    grid.appendChild(card);
  }

  const vClass = gradeToVerdictClass(p.grade);
  const basePatchWarning = p.testWarning ? `<div class="patch-warning">${escapeHtml(p.testWarning)}</div>` : "";

  container.innerHTML = `
    <div class="detail-header">
      <img class="icon-img lg" src="${p.icon}" alt="" onerror="this.style.display='none'">
      <div class="detail-titles">
        <h2>${escapeHtml(p.name)}</h2>
        <div class="subtitle">오퍼(기본 퍽)</div>
      </div>
      <div class="detail-grade">${gradeBadge(p.grade)}</div>
    </div>

    ${basePatchWarning}

    <div class="section-title">설명</div>
    <div class="desc-line">${p.role || ""}</div>
    <div class="desc-line capstone">${p.endgame || ""}</div>

    <div class="section-title">세부 효과 (강점 / 약점)</div>
    ${strengths || '<div class="empty-state" style="padding:10px">기록된 강점 없음</div>'}
    ${weaknesses || '<div class="empty-state" style="padding:10px">특이사항 없음</div>'}

    <div class="section-title">전직 레벨별 수치</div>
    ${renderSliderSection(p.passiveStats, 20)}

    <div class="section-title">밸런스 판정</div>
    <div class="verdict-box v-${vClass}">
      <b>등급 ${escapeHtml(p.grade || "-")}</b>
      ${escapeHtml(p.summary || "")}
    </div>

    <div class="section-title">전직 트리 (클릭해서 상세 보기)</div>
  `;
  container.appendChild(grid);
  wrap.appendChild(container);
  return wrap;
}

function renderAdvDetail(key) {
  const p = ADV_BY_KEY[key];
  const parent = BASE_BY_KEY[p.parentPerk];

  const descLines = p.descriptions.map(d =>
    `<div class="desc-line ${d.isCapstone ? "capstone" : ""}">${d.raw || escapeHtml(d.text)}</div>`
  ).join("") || '<div class="empty-state" style="padding:10px">등록된 설명 없음 (하드코딩 시스템)</div>';
  const descNote = p.descriptions.length
    ? '<div style="font-size:11px;color:var(--text-dim);margin-bottom:6px">※ 아래 수치는 전직 레벨 20(만렙) 기준입니다.</div>' : "";

  const perkPatchWarning = p.testWarning ? `
    <div class="patch-warning">${escapeHtml(p.testWarning)}
    ${p.isPatched ? '<div style="margin-top:4px">설명 텍스트에 포함된 일부 수치는 패치 이전 값일 수 있으니, 실제 적용 수치는 아래 "전직 레벨별 수치" 표를 기준으로 확인하세요.</div>' : ""}</div>` : "";

  const hasPassive = p.passiveStats.length > 0;

  let verdictBlock = "";
  if (p.verdict) {
    const vClass = gradeToVerdictClass(p.grade);
    verdictBlock = `
      <div class="section-title">밸런스 판정</div>
      <div class="verdict-box v-${vClass}">
        <b>등급 ${escapeHtml(p.grade || "-")} · ${escapeHtml(p.verdict.tag)}</b>
        ${escapeHtml(p.verdict.note)}
      </div>`;
  }

  const skillsHtml = p.skills.map(s => `
    <div class="skill-item">
      <h4>${escapeHtml(s.name)} <span style="color:var(--text-dim);font-weight:400;font-size:11px">(${s.key})</span>${s.isPatched ? '<span class="patch-badge">패치 반영됨</span>' : ""}</h4>
      ${s.isPatched ? `<div style="font-size:11px;color:var(--orange);margin-bottom:4px">⚠️ 아래 표준/디럭스 설명 문구의 수치는 패치 이전 값일 수 있습니다. 실제 현재 수치는 하단 원본값을 확인하세요.</div>` : ""}
      ${s.standardDescRaw ? `<div class="std"><b>표준</b>${s.standardDescRaw}</div>` : ""}
      ${s.deluxeDescRaw ? `<div class="delx"><b>디럭스</b>${s.deluxeDescRaw}</div>` : ""}
      ${s.note ? `<div class="skillnote">${escapeHtml(s.note)}</div>` : ""}
      <div class="rawvals">${s.rawValues.map(v => `${escapeHtml(v.label)}: ${v.display}`).join("  ·  ")}</div>
    </div>
  `).join("") || '<div class="empty-state" style="padding:10px">스킬 데이터 없음 (하드코딩 시스템)</div>';

  const container = el("div", {});
  container.innerHTML = `
    <div class="back-link" data-basekey="${p.parentPerk}">← ${parent ? escapeHtml(parent.name) : "오퍼"} 개요로</div>
    <div class="detail-header">
      <img class="icon-img lg" src="${p.icon}" alt="" onerror="this.style.display='none'">
      <div class="detail-titles">
        <h2>${escapeHtml(p.name)}</h2>
        <div class="subtitle">커퍼(전직 퍽) · ${parent ? escapeHtml(parent.name) : "?"} Lv${p.unlockLevel} 해금 · 스킬 ${p.skillCount}개</div>
      </div>
      <div class="detail-grade">${gradeBadge(p.grade)}</div>
    </div>

    ${perkPatchWarning}

    <div class="section-title">설명</div>
    <div class="desc-line">${p.role || ""}</div>
    <div class="desc-line capstone">${p.endgame || ""}</div>

    <div class="section-title">세부 효과 (게임 내 텍스트)</div>
    ${descNote}
    ${descLines}

    ${hasPassive ? `<div class="section-title">전직 레벨별 수치</div>${renderSliderSection(p.passiveStats, 20)}` : ""}

    ${verdictBlock}

    <div class="section-title">스킬 목록 (표준 / 디럭스)</div>
    <div class="skill-list">${skillsHtml}</div>
  `;
  const wrap = document.createDocumentFragment();
  wrap.appendChild(container);
  return wrap;
}

function renderSliderSection(passiveStats, maxLevel) {
  if (!passiveStats.length) return '<div class="empty-state" style="padding:10px">등록된 패시브 수치 없음</div>';
  const rows = passiveStats.map(s =>
    `<tr data-perlevel="${s.value}" data-unit="${s.unit}"><td>${escapeHtml(s.label)}</td><td>${s.display}</td><td class="live-val">${formatByUnit(s.value * maxLevel, s.unit)}</td></tr>`
  ).join("");
  return `
    <div style="font-size:11px;color:var(--text-dim);margin-bottom:2px">⚠ 게임 내 상한(클램프)이 적용되는 항목이 있어 아래 수치는 단순 계산 참고값입니다. 수치는 KFZedternalUnlimited.ini의 현재(패치 반영) 값 기준입니다.</div>
    <div class="level-slider-row">
      <label for="levelSlider">퍽 레벨</label>
      <input id="levelSlider" type="range" min="1" max="${maxLevel}" value="${maxLevel}">
      <span class="lvl-val" id="lvlValLabel">Lv ${maxLevel}</span>
    </div>
    <table class="stat-table">
      <tr><th>항목</th><th>레벨당</th><th>선택 레벨 값</th></tr>
      ${rows}
    </table>
  `;
}

function onLevelSlide(e) {
  const lvl = Number(e.target.value);
  document.getElementById("lvlValLabel").textContent = `Lv ${lvl}`;
  document.querySelectorAll("#mainArea table tr[data-perlevel]").forEach(row => {
    const perLevel = Number(row.dataset.perlevel);
    row.querySelector(".live-val").textContent = formatByUnit(perLevel * lvl, row.dataset.unit);
  });
}

function formatByUnit(value, unit) {
  if (typeof value !== "number" || Number.isNaN(value)) return String(value);
  if (unit === "percent") {
    const pct = value * 100;
    const s = trimNum(pct);
    const sign = value >= 0 ? "+" : "";
    return `${sign}${s}%`;
  }
  if (unit === "multiplier") return `×${trimNum(value)}`;
  if (unit === "seconds") return `${trimNum(value)}초`;
  if (unit === "currency") return `${Math.round(value).toLocaleString()} 도쉬`;
  if (Number.isInteger(value)) return value.toLocaleString();
  return trimNum(value);
}

function trimNum(n) {
  return (Math.round(n * 100) / 100).toString();
}

function gradeClass(grade) {
  if (!grade) return "";
  const g = grade.trim();
  if (g === "SS") return "grade-ss";
  if (g === "S") return "grade-s";
  if (g === "A") return "grade-a";
  if (g === "B") return "grade-b";
  if (g === "C") return "grade-c";
  if (g === "?") return "grade-mystery";
  return "grade-b";
}

function gradeBadge(grade) {
  if (!grade) return "";
  return `<span class="grade-badge ${gradeClass(grade)}">${escapeHtml(grade)}</span>`;
}

function gradeToVerdictClass(grade) {
  if (!grade) return "ok";
  const g = grade.trim();
  if (g === "SS" || g === "S") return "op";
  if (g === "C") return "trash";
  if (g === "?") return "mystery";
  return "ok";
}

function escapeHtml(s) {
  if (s == null) return "";
  return String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function onSearch(e) {
  const q = e.target.value.trim().toLowerCase();
  const cards = document.querySelectorAll("[data-advkey]");
  if (!q) {
    cards.forEach(c => c.classList.remove("dim", "hl"));
    return;
  }
  cards.forEach(c => {
    const match = c.dataset.search && c.dataset.search.includes(q);
    c.classList.toggle("hl", match);
    c.classList.toggle("dim", !match);
  });
}

init();
