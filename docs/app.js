let DATA = null;
let ADV_BY_KEY = {};
let BASE_BY_KEY = {};
let OPEN_BASE_KEY = null;
let SELECTED_ADV_KEY = null;
let AURORA_VIEW = false;
let AURORA_MODE = null;
let SEARCH_INDEX = [];
let SEARCH_RESULTS = [];
let SEARCH_ACTIVE_IDX = -1;

const LEVELS = [5, 10, 15, 20];

// [ZedternalReborn.Config_Player] 원본 배율 (KFZedternalReborn_Game.ini 기준).
// 표시값 = (실제값 + 1) / 2 로 절반만 반영해 서술합니다.
const DAMAGE_GIVEN_STATS = [
  { label: "화염 피해", real: 0.5 },
  { label: "지면 화염 피해", real: 0.25 },
  { label: "네이팜 피해", real: 0.35 },
  { label: "폭발 피해", real: 0.4 },
  { label: "폭발 파편 피해", real: 0.5 },
  { label: "메딕 수류탄(독성) 피해", real: 0.25 },
  { label: "베기 피해", real: 0.85 },
  { label: "관통 피해", real: 0.85 },
  { label: "둔기 피해", real: 0.85 },
  { label: "샷건 피해", real: 0.6 },
];
const DAMAGE_TAKEN_STATS = [
  { label: "허스크 자폭 피해", real: 1.5 },
  { label: "플레쉬파운드 킹 가슴빔 피해", real: 0.75 },
  { label: "한스 유탄 피해", real: 0.75 },
  { label: "가부장 미사일 피해", real: 0.75 },
  { label: "여장부 플라즈마포 피해", real: 0.6 },
  { label: "소닉 피해", real: 1.5 },
  { label: "독성 피해", real: 2.0 },
  { label: "허스크 화염구 피해", real: 1.25 },
  { label: "허스크 화염방사기 피해", real: 2.0 },
  { label: "근접무기 소지 중 전체 피해", real: 0.75 },
];

const WEAPON_AURORA_STATS = [
  { label: "동결 투척자", value: 1.25 },
  { label: "동결 투척자 얼음 파편", value: 1.75 },
  { label: "RPG-7 탄두", value: 1.5 },
  { label: "RPG-7 후폭발", value: 10.0 },
  { label: "분쇄기 폭발", value: 2.0 },
  { label: "석궁", value: 1.3 },
  { label: "컴파운드 보우", value: 1.5 },
  { label: "M14 EBR", value: 1.3 },
  { label: "FN FAL", value: 1.2 },
  { label: "MG3", value: 1.1 },
  { label: "MG3 변형", value: 1.1 },
  { label: "스토너 63A", value: 1.1 },
  { label: "센터파이어 MB464", value: 0.75 },
  { label: "윈체스터 1894", value: 0.75 },
  { label: "S&W 500", value: 0.8 },
  { label: "M99", value: 0.85 },
  { label: "레일건", value: 0.9 },
  { label: "허스크 캐논", value: 0.8 },
  { label: "HV 스톰 캐논", value: 0.9 },
  { label: "HRG 카붐스틱", value: 0.85 },
  { label: "HRG 메뚜기", value: 0.3 },
];

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
  // no-cache: revalidate with the server every load so a freshly rebuilt
  // perks.json is never masked by a stale browser-cached copy
  const res = await fetch("data/perks.json", { cache: "no-cache" });
  DATA = await res.json();
  ADV_BY_KEY = Object.fromEntries(DATA.advancedPerks.map(p => [p.key, p]));
  BASE_BY_KEY = Object.fromEntries(DATA.basePerks.map(p => [p.key, p]));

  document.getElementById("meta").innerHTML =
    `📢 <b>공지사항</b>: 이 위키에 기재된 수치가 현재 서버에 실제로 적용 중인 값입니다. 게임 클라이언트 내부 스킬 설명에 표시되는 수치는 오리지널 값이라 실제 값과 전혀 다릅니다. 정확한 현재 수치는 반드시 이 위키를 기준으로 확인하세요.
    <div class="meta-patch-row">
      <div class="meta-patch-text">
        <span class="patch-highlight">밸런스 패치 된 수치가 실제 인게임 화면에 적용되기를 바라는 플레이어는 다음 한국어 패치 파일을 다운 받아 해당 경로에 넣어주세요.</span>
        <br>경로: <code>문서\\My Games\\KillingFloor2\\KFGame\\Localization\\KOR</code> 로 들어간 후, 다운로드한 <code>ZedternalRBPerkpackage.KOR</code> 파일을 그대로 덮어쓰기.
        <div class="patch-warning">⚠️ 반드시 Steam 창작마당에서 <b>Zedternal Unlimited 구독을 해제</b>한 상태여야 합니다. 구독 중이면 Steam이 자동 동기화하면서 방금 덮어쓴 패치 파일을 구버전 원본으로 다시 덮어씁니다.</div>
      </div>
      <a class="patch-download-btn" id="korDownloadBtn" href="downloads/ZedternalRBPerkpackage.KOR" download>⬇ 한국어 패치 파일 다운로드</a>
    </div>`;

  document.getElementById("korDownloadBtn").addEventListener("click", (e) => {
    const ok = confirm("Steam 창작마당에서 Zedternal Unlimited 구독을 해제하셨습니까?\n\n구독 중인 상태로 이 파일을 덮어쓰면, Steam이 자동 동기화하면서 방금 받은 패치 파일을 구버전 원본으로 다시 덮어씁니다.\n\n구독 해제를 확인하셨다면 [확인]을 눌러 다운로드를 계속하세요.");
    if (!ok) e.preventDefault();
  });

  renderSidebar();
  renderMainArea();
  buildSearchIndex();
  const searchBox = document.getElementById("searchBox");
  searchBox.addEventListener("input", onSearch);
  searchBox.addEventListener("keydown", onSearchKeydown);
  document.addEventListener("click", (e) => {
    if (!e.target.closest(".search-wrap")) closeSearchResults();
  });
}

function showBaseOverview(key) {
  OPEN_BASE_KEY = key;
  SELECTED_ADV_KEY = null;
  AURORA_VIEW = false;
  renderSidebar();
  renderMainArea();
}

function selectAdv(key) {
  const adv = ADV_BY_KEY[key];
  OPEN_BASE_KEY = adv.parentPerk;
  SELECTED_ADV_KEY = key;
  AURORA_VIEW = false;
  renderSidebar();
  renderMainArea();
  document.getElementById("mainArea").scrollIntoView({ behavior: "instant", block: "start" });
}

function showAurora(mode) {
  AURORA_VIEW = true;
  AURORA_MODE = mode;
  OPEN_BASE_KEY = null;
  SELECTED_ADV_KEY = null;
  renderSidebar();
  renderMainArea();
  document.getElementById("mainArea").scrollIntoView({ behavior: "instant", block: "start" });
}

function auroraBarRow(stat, invert) {
  const shown = (stat.real + 1) / 2;
  const deviation = shown - 1;
  const halfWidth = Math.min(50, (Math.abs(deviation) / 2) * 100);
  const left = deviation >= 0 ? 50 : 50 - halfWidth;
  // 기븐(내가 주는 피해)은 수치가 높을수록 버프, 테이큰(내가 받는 피해)은 수치가 낮을수록 버프 — 방향이 반대.
  const isBuff = invert ? deviation < 0 : deviation > 0;
  const color = Math.abs(deviation) < 0.001 ? "var(--text-dim)" : (isBuff ? "var(--green)" : "var(--red)");
  return `
    <div class="ba-row">
      <div class="ba-row-label">${escapeHtml(stat.label)}</div>
      <div class="ba-bar-track">
        <div class="ba-bar-center"></div>
        <div class="ba-bar-fill" style="left:${left}%;width:${halfWidth}%;background:${color}"></div>
      </div>
      <div class="ba-row-val">×${trimNum(shown)}</div>
    </div>`;
}

function renderBalanceAuroraBox() {
  const item = el("div", { class: `accordion-item balance-aurora-item ${AURORA_VIEW && AURORA_MODE === "perk" ? "open" : ""}` });

  const header = el("div", { class: "accordion-header" }, [
    el("span", { class: "ba-icon", text: "⚠️" }),
    el("div", { class: "titles" }, [
      el("h3", { text: "퍼크 밸런스 오로라" }),
    ]),
    el("span", { class: "chevron", text: "▸" }),
  ]);
  header.addEventListener("click", () => showAurora("perk"));
  item.appendChild(header);
  return item;
}

function renderWeaponAuroraBox() {
  const item = el("div", { class: `accordion-item weapon-aurora-item ${AURORA_VIEW && AURORA_MODE === "weapon" ? "open" : ""}` });

  const header = el("div", { class: "accordion-header" }, [
    el("span", { class: "ba-icon", text: "⚔️" }),
    el("div", { class: "titles" }, [
      el("h3", { text: "무기 밸런스 오로라" }),
    ]),
    el("span", { class: "chevron", text: "▸" }),
  ]);
  header.addEventListener("click", () => showAurora("weapon"));
  item.appendChild(header);
  return item;
}

function renderWeaponAuroraDetail() {
  const buffList = WEAPON_AURORA_STATS.filter(w => w.value >= 1).map(w => `<li>${escapeHtml(w.label)}</li>`).join("");
  const nerfList = WEAPON_AURORA_STATS.filter(w => w.value < 1).map(w => `<li>${escapeHtml(w.label)}</li>`).join("");
  return `
    <div class="detail-header">
      <div class="ba-icon lg">⚔️</div>
      <div class="detail-titles">
        <h2>무기 밸런스 오로라</h2>
      </div>
    </div>

    <div class="section-title">기준</div>
    <div class="aurora-note">
      <div class="aurora-note-main"> 제드터널 모드의 특성상 너무 강하거나 약한 무기를 밸런싱한, 버프 / 너프된 무기 리스트 입니다. <code>소스: [ZedternalReborn.Config_Player]</code></div>
      <div class="aurora-note-sub">해당 값은 추후 밸런싱을 통해 언제나 바뀔 수 있으며 배율 값은 비공개 입니다.</div>
    </div>

    <div class="aurora-grid">
      <div class="aurora-col buff-col">
        <div class="section-title"><font color=\"#00ff00\">버프</font></div>
        <ul class="strengths">${buffList}</ul>
      </div>
      <div class="aurora-col nerf-col">
        <div class="section-title"><font color=\"#ff0000\">너프</font></div>
        <ul class="strengths">${nerfList}</ul>
      </div>
    </div>
  `;
}

function renderBalanceAuroraDetail() {
  return `
    <div class="detail-header">
      <div class="ba-icon lg">⚠️</div>
      <div class="detail-titles">
        <h2>퍼크 밸런스 오로라</h2>
      </div>
    </div>
    <div class="section-title">설명</div>
    <div class="desc-line">
      속성별로 내가 주는 피해와 받는 피해가 평소보다 얼마나 세거나 약한지 한눈에 볼 수 있는 표입니다.
    </div>

    <div class="section-title"><font color=\"#00ff00\">대미지 기븐 (내가 주는 피해 증폭 배율)</font></div>
    ${DAMAGE_GIVEN_STATS.map(s => auroraBarRow(s, false)).join("")}

    <div class="section-title"><font color=\"#00ff00\">대미지 테이큰 (내가 받는 피해 증폭 배율)</font></div>
    ${DAMAGE_TAKEN_STATS.map(s => auroraBarRow(s, true)).join("")}
  `;
}

function renderSidebar() {
  const sidebar = document.getElementById("sidebar");
  sidebar.innerHTML = "";
  sidebar.appendChild(renderBalanceAuroraBox());
  sidebar.appendChild(renderWeaponAuroraBox());
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

  if (AURORA_VIEW) {
    main.innerHTML = AURORA_MODE === "weapon" ? renderWeaponAuroraDetail() : renderBalanceAuroraDetail();
    wireDetailEvents(main);
    return;
  }
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
  main.appendChild(el("div", { class: "empty-state", text: "왼쪽에서 베이스 퍼크를 선택하면 베이스 퍼크 트리가 펼쳐집니다." }));
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
  const weaknesses = p.weaknesses.length
    ? p.weaknesses.map(w =>
        `<div class="weak-item"><span class="sev-${w.severity}">${escapeHtml(w.label || w.skill)}</span> — ${escapeHtml(w.issue)}</div>`
      ).join("")
    : "";

  const grid = el("div", { class: "adv-grid" });
  const unlockByLevel = Object.fromEntries(p.unlocks.map(u => [u.level, u]));
  for (const lvl of LEVELS) {
    const u = unlockByLevel[lvl];
    if (!u) continue;
    const adv = ADV_BY_KEY[u.perk];
    const card = el("div", {
      class: "adv-card",
      "data-advkey": adv.key,
    }, [
      iconImg(adv),
      el("div", { class: "adv-body" }, [
        el("div", { class: "lvl", text: `Lv${lvl} 해금` }),
        el("div", { class: "name", text: adv.name }),
        el("div", { class: "skillcount", text: `스킬 ${adv.skillCount}개` }),
      ]),
    ]);
    if (adv.grade) card.appendChild(el("span", { class: "grade-badge-wrap", html: gradeBadge(adv.grade) }));
    card.addEventListener("click", () => selectAdv(adv.key));
    grid.appendChild(card);
  }

  const recentChangeBadge = renderRecentChangeBadge(p.recentChangeTag);

  container.innerHTML = `
    <div class="detail-header">
      <img class="icon-img lg" src="${p.icon}" alt="" onerror="this.style.display='none'">
      <div class="detail-titles">
        <h2>${escapeHtml(p.name)}</h2>
        <div class="subtitle">베이스 퍼크</div>
      </div>
      ${recentChangeBadge}
      <div class="detail-grade">${gradeBadge(p.grade)}</div>
    </div>

    <div class="section-title">설명</div>
    <div class="desc-line">${p.role || ""}</div>

    <div class="section-title">세부 효과 (강점)</div>
    ${strengths || '<div class="empty-state" style="padding:10px">기록된 강점 없음</div>'}
    ${weaknesses ? `<div class="section-title" style="margin-top:14px">세부 효과 (약점)</div>${weaknesses}` : ""}

    <div class="section-title">레벨별 수치</div>
    ${renderSliderSection(p.passiveStats, 20)}

    <div class="section-title">퍼크 트리 (클릭해서 상세 보기)</div>
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
  ).join("") || '<div class="empty-state" style="padding:10px">등록된 게임 내 설명이 없습니다 — 아래 시스템 규칙 섹션을 참고하세요.</div>';
  const descNote = p.descriptions.length
    ? '<div style="font-size:11px;color:var(--text-dim);margin-bottom:6px">※ 아래 수치는 레벨 20(만렙) 기준입니다.</div>' : "";

  const recentChangeBadge = renderRecentChangeBadge(p.recentChangeTag);

  const hasPassive = p.passiveStats.length > 0;

  const skillsHtml = p.skills.map(s => `
    <div class="skill-item ${s.disabled ? "skill-disabled" : ""}">
      <h4>${escapeHtml(s.name)} <span style="color:var(--text-dim);font-weight:400;font-size:11px">(${s.key})</span>${s.disabled ? '<span class="disabled-badge">비활성화</span>' : ""}</h4>
      ${s.disabled ? `<div class="disabled-banner">🚫 이 스킬은 현재 인게임에서 비활성화되어 선택할 수 없습니다.${s.disabledNote ? ` (${escapeHtml(s.disabledNote)})` : ""}</div>` : ""}
      ${s.noData ? `<div class="empty-state" style="padding:10px">이 스킬은 게임 데이터에 설명이 없어 정확한 효과를 표시할 수 없습니다.</div>` : ""}
      ${s.standardDescRaw ? `<div class="std"><b>표준</b>${s.standardDescRaw}</div>` : ""}
      ${s.deluxeDescRaw ? `<div class="delx"><b>디럭스</b>${s.deluxeDescRaw}</div>` : ""}
      ${s.note ? `<div class="skillnote">${escapeHtml(s.note)}</div>` : ""}
    </div>
  `).join("") || (p.key === "Haunted"
    ? '<div class="empty-state mystery" style="padding:10px">🌫️ 그 어떤 기록에도 남아있지 않다 — 이 존재의 진짜 힘을 알고 싶다면, 직접 웨이브 속에서 마주하는 수밖에 없다.</div>'
    : '<div class="empty-state" style="padding:10px">이 퍼크는 구매형 스킬 없이 시스템 자체로 작동합니다 — 위의 설명과 규칙 섹션을 참고하세요.</div>');

  const container = el("div", {});
  container.innerHTML = `
    <div class="back-link" data-basekey="${p.parentPerk}">← ${parent ? escapeHtml(parent.name) : "베이스 퍼크"} 개요로</div>
    <div class="detail-header">
      <img class="icon-img lg" src="${p.icon}" alt="" onerror="this.style.display='none'">
      <div class="detail-titles">
        <h2>${escapeHtml(p.name)}</h2>
        <div class="subtitle">베이스 퍼크 · ${parent ? escapeHtml(parent.name) : "?"} Lv${p.unlockLevel} 해금 · 스킬 ${p.skillCount}개</div>
      </div>
      ${recentChangeBadge}
      <div class="detail-grade">${gradeBadge(p.grade)}</div>
    </div>

    <div class="section-title">설명</div>
    <div class="desc-line">${p.role || ""}</div>

    <div class="section-title">세부 효과 (게임 내 텍스트)</div>
    ${descNote}
    ${descLines}

    ${(p.extraSections || []).map(sec => `
      <div class="section-title">${escapeHtml(sec.title)}</div>
      ${sec.note ? `<div style="font-size:11px;color:var(--text-dim);margin-bottom:6px">${escapeHtml(sec.note)}</div>` : ""}
      ${sec.html}
    `).join("")}

    ${hasPassive ? `<div class="section-title">레벨별 수치</div>${renderSliderSection(p.passiveStats, 20)}` : ""}

    ${renderFixedStatsSection(p.fixedStats)}

    <div class="section-title">스킬 목록 (표준 / 디럭스)</div>
    <div class="skill-list">${skillsHtml}</div>
  `;
  const wrap = document.createDocumentFragment();
  wrap.appendChild(container);
  return wrap;
}

function renderFixedStatsSection(fixedStats) {
  if (!fixedStats || !fixedStats.length) return "";
  const rows = fixedStats.map(s => `
    <div class="fixed-stat-row">
      <span class="fixed-stat-label">${escapeHtml(s.label)}</span>
      <span class="fixed-stat-val">${s.display}</span>
      ${s.capstoneLevel ? `<span class="capstone-badge">Lv${s.capstoneLevel} 캡스톤</span>` : ""}
    </div>`).join("");
  return `
    <div class="section-title">고정 효과 (레벨과 무관하게 일정)</div>
    <div style="font-size:11px;color:var(--text-dim);margin-bottom:6px">⚠ 아래 수치는 레벨업으로 커지지 않는 고정값입니다. "Lv10/20 캡스톤"은 해당 레벨에 도달하는 순간 1회 적용되는 효과입니다.</div>
    <div class="fixed-stat-list">${rows}</div>
  `;
}

function renderSliderSection(passiveStats, maxLevel) {
  if (!passiveStats.length) return '<div class="empty-state" style="padding:10px">등록된 패시브 수치 없음</div>';
  const rows = passiveStats.map(s => {
    const signClass = s.value < 0 ? "stat-neg" : s.value > 0 ? "stat-pos" : "";
    return `<tr data-perlevel="${s.value}" data-unit="${s.unit}"><td>${escapeHtml(s.label)}</td><td class="${signClass}">${s.display}</td><td class="live-val ${signClass}">${formatByUnit(s.value * maxLevel, s.unit)}</td></tr>`;
  }).join("");
  return `
    <div style="font-size:11px;color:var(--text-dim);margin-bottom:2px">⚠ 게임 내 상한(클램프)이 적용되는 항목이 있어 아래 수치는 단순 계산 참고값입니다. 수치는 KFZedternalUnlimited.ini의 현재(패치 반영) 값 기준입니다.</div>
    <div class="level-slider-row">
      <label for="levelSlider">퍼크 레벨</label>
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

function renderRecentChangeBadge(tag) {
  if (!tag) return "";
  const isBuff = tag.type === "buff";
  const label = isBuff ? "🔺 최근 버프됨" : "🔻 최근 너프됨";
  const cls = isBuff ? "recent-change-buff" : "recent-change-nerf";
  return `<div class="recent-change-badge ${cls}">${label} <span class="recent-change-date">(${escapeHtml(tag.date)})</span></div>`;
}

function escapeHtml(s) {
  if (s == null) return "";
  return String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function buildSearchIndex() {
  SEARCH_INDEX = [];
  for (const base of DATA.basePerks) {
    SEARCH_INDEX.push({
      type: "base",
      navKey: base.key,
      ownKey: base.key,
      name: base.name,
      sub: "베이스 퍼크",
      search: `${base.name} ${base.key}`.toLowerCase(),
    });
  }
  for (const adv of DATA.advancedPerks) {
    const parent = BASE_BY_KEY[adv.parentPerk];
    SEARCH_INDEX.push({
      type: "adv",
      navKey: adv.key,
      ownKey: adv.key,
      name: adv.name,
      sub: `베이스 퍼크 · ${parent ? parent.name : ""}`,
      search: buildSearchCorpus(adv, parent || { name: "" }),
    });
    for (const s of adv.skills) {
      SEARCH_INDEX.push({
        type: "skill",
        navKey: adv.key,
        ownKey: s.key,
        name: s.name,
        sub: `스킬 · ${adv.name}`,
        search: `${s.name} ${s.key} ${s.standardDesc || ""} ${s.deluxeDesc || ""}`.toLowerCase(),
      });
    }
  }
}

// Ranked so an exact/prefix match on the item's own name or key (e.g. typing
// "Predator") always outranks an incidental substring hit inside some other
// perk's skill key (e.g. "ApexPredator" belongs to Hydra, not Predator).
function searchMatches(query) {
  const q = query.trim().toLowerCase();
  if (!q) return [];
  const tiers = [[], [], [], [], []];
  for (const item of SEARCH_INDEX) {
    const nameLower = item.name.toLowerCase();
    const ownKeyLower = item.ownKey.toLowerCase();
    if (nameLower === q || ownKeyLower === q) tiers[0].push(item);
    else if (nameLower.startsWith(q)) tiers[1].push(item);
    else if (ownKeyLower.startsWith(q)) tiers[2].push(item);
    else if (ownKeyLower.includes(q)) tiers[3].push(item);
    else if (item.search.includes(q)) tiers[4].push(item);
  }
  return tiers.flat().slice(0, 8);
}

function goToSearchResult(item) {
  if (!item) return;
  if (item.type === "base") showBaseOverview(item.navKey);
  else selectAdv(item.navKey);
  closeSearchResults();
  document.getElementById("searchBox").blur();
}

function closeSearchResults() {
  SEARCH_RESULTS = [];
  SEARCH_ACTIVE_IDX = -1;
  const box = document.getElementById("searchResults");
  box.classList.remove("open");
  box.innerHTML = "";
}

function renderSearchResults() {
  const box = document.getElementById("searchResults");
  if (!SEARCH_RESULTS.length) {
    closeSearchResults();
    return;
  }
  box.innerHTML = SEARCH_RESULTS.map((item, i) => `
    <div class="search-result-item ${i === SEARCH_ACTIVE_IDX ? "active" : ""}" data-idx="${i}">
      <span class="sr-name">${escapeHtml(item.name)}</span>
      <span class="sr-sub">${escapeHtml(item.sub)}</span>
    </div>
  `).join("");
  box.classList.add("open");
  box.querySelectorAll(".search-result-item").forEach(el => {
    el.addEventListener("click", () => goToSearchResult(SEARCH_RESULTS[Number(el.dataset.idx)]));
  });
}

function onSearch(e) {
  SEARCH_RESULTS = searchMatches(e.target.value);
  SEARCH_ACTIVE_IDX = SEARCH_RESULTS.length ? 0 : -1;
  renderSearchResults();
}

function onSearchKeydown(e) {
  if (e.key === "ArrowDown") {
    if (!SEARCH_RESULTS.length) return;
    e.preventDefault();
    SEARCH_ACTIVE_IDX = (SEARCH_ACTIVE_IDX + 1) % SEARCH_RESULTS.length;
    renderSearchResults();
  } else if (e.key === "ArrowUp") {
    if (!SEARCH_RESULTS.length) return;
    e.preventDefault();
    SEARCH_ACTIVE_IDX = (SEARCH_ACTIVE_IDX - 1 + SEARCH_RESULTS.length) % SEARCH_RESULTS.length;
    renderSearchResults();
  } else if (e.key === "Enter") {
    if (!SEARCH_RESULTS.length) return;
    e.preventDefault();
    goToSearchResult(SEARCH_RESULTS[Math.max(0, SEARCH_ACTIVE_IDX)]);
  } else if (e.key === "Escape") {
    closeSearchResults();
  }
}

init();
