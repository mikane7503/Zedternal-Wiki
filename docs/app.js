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

// [ZedternalReborn.Config_Player] 원본 배율 (KFZedternalReborn_Game.ini 기준).
// 표시값 = (실제값 + 1) / 2 로 절반만 반영해 서술합니다.
let DAMAGE_GIVEN_STATS = [];
let DAMAGE_TAKEN_STATS = [];
let WEAPON_AURORA_STATS = [];

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

function gradeClass(grade) {
  return `grade-${String(grade || "").toLowerCase()}`;
}

function gradeBadge(grade) {
  return grade ? `<span class="grade-badge ${gradeClass(grade)}">${escapeHtml(grade)}</span>` : "";
}

function gradeBadgeNode(grade) {
  return grade ? el("span", { class: `grade-badge ${gradeClass(grade)}`, text: grade }) : null;
}

function isCombinationUnlocked(perk) {
  return (perk.unlockRequirements || []).length > 1;
}

function requirementSummary(perk) {
  return (perk.unlockRequirements || []).map(req => {
    const required = BASE_BY_KEY[req.perk] || ADV_BY_KEY[req.perk];
    return `${required ? required.name : req.perk} Lv${req.level}`;
  }).join(" + ");
}

async function init() {
  // no-cache: revalidate with the server every load so a freshly rebuilt
  // perks.json is never masked by a stale browser-cached copy
  const res = await fetch("data/perks.json", { cache: "no-cache" });
  DATA = await res.json();
  DAMAGE_GIVEN_STATS = DATA.meta.systems.damageGiven.map(item => ({ label: item.label, real: item.multiplier }));
  DAMAGE_TAKEN_STATS = DATA.meta.systems.damageTaken.map(item => ({ label: item.label, real: item.multiplier }));
  WEAPON_AURORA_STATS = DATA.meta.systems.weaponDamage.map(item => ({ label: item.label, value: item.multiplier }));
  ADV_BY_KEY = Object.fromEntries(DATA.advancedPerks.map(p => [p.key, p]));
  BASE_BY_KEY = Object.fromEntries(DATA.basePerks.map(p => [p.key, p]));

  const version = DATA.meta.version ? `v${DATA.meta.version}` : "버전 정보 없음";
  const asOf = DATA.meta.asOf || "날짜 정보 없음";
  const deluxeUnlockLevels = (DATA.meta.deluxeSkillUnlock || []).map(level => `Lv${level}`).join(", ") || "설정 없음";
  document.getElementById("meta").innerHTML =
    `📘 <b>Zedternal Tempered ${version}</b> · ${asOf} 기준 소스 기본값과 게임 설명을 대조해 표시합니다. 서버 운영자가 별도 INI 값을 사용하면 실제 서버 수치와 다를 수 있습니다.
    <br>스킬 구매: 표준 ${Number(DATA.meta.skillUpgradePrice || 0).toLocaleString()} 도쉬 · 디럭스 ${Number(DATA.meta.deluxeSkillUpgradePrice || 0).toLocaleString()} 도쉬 · 디럭스 해금 레벨 ${escapeHtml(deluxeUnlockLevels)}
    <div class="meta-patch-row">
      <div class="meta-patch-text">
        한국어 로컬라이제이션 파일은 선택적으로 설치할 수 있습니다. 파일을 <code>문서\\My Games\\KillingFloor2\\KFGame\\Localization\\KOR</code>에 넣고 게임을 다시 실행하세요.
      </div>
      <a class="patch-download-btn" href="downloads/ZedternalTempered.kor" download>⬇ 템퍼드 한국어 파일 다운로드</a>
    </div>`;
  document.getElementById("footerVersion").textContent = version;

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
  document.getElementById("mainArea").scrollIntoView({ behavior: "instant", block: "start" });
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
      <div class="ba-row-val" title="이 값은 Config_Player의 현재 INI 배율입니다. 시각화 기준 환산값 ×${trimNum(shown)}">×${trimNum(stat.real)}</div>
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

function weaponAuroraLi(w) {
  let style = "";
  if (w.value > 1.5) style = ' style="color:#00ff00;font-weight:600"';
  else if (w.value <= 0.7) style = ' style="color:crimson;font-weight:600"';
  return `<li${style}>${escapeHtml(w.label)} — ×${trimNum(w.value)}</li>`;
}

function renderWeaponAuroraDetail() {
  const buffList = WEAPON_AURORA_STATS.filter(w => w.value >= 1).map(weaponAuroraLi).join("");
  const nerfList = WEAPON_AURORA_STATS.filter(w => w.value < 1).map(weaponAuroraLi).join("");
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
      <div class="aurora-note-sub">배율은 현재 템퍼드 소스의 <code>Config_Player</code> 설정에서 자동으로 가져옵니다.</div>
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
  const comboPerks = DATA.advancedPerks.filter(isCombinationUnlocked);
  if (comboPerks.length) {
    sidebar.appendChild(el("div", { class: "sidebar-section-label", text: "퍼크 조합 해금" }));
    for (const perk of comboPerks) {
      const row = el("div", { class: "child-row combination-perk-row", "data-advkey": perk.key }, [
        iconImg(perk, "sm"),
        el("span", { class: "name", text: perk.name }),
        gradeBadgeNode(perk.grade),
      ]);
      row.title = requirementSummary(perk);
      row.addEventListener("click", () => selectAdv(perk.key));
      sidebar.appendChild(row);
    }
  }
  for (const base of DATA.basePerks) {
    const isOpen = base.key === OPEN_BASE_KEY;
    const item = el("div", { class: `accordion-item ${isOpen ? "open" : ""}`, "data-basekey": base.key });

    const header = el("div", { class: "accordion-header" }, [
      iconImg(base, "sm"),
      el("div", { class: "titles" }, [
        el("h3", { text: base.name }),
      ]),
      el("span", { class: "chevron", text: "▸" }),
    ]);
    header.addEventListener("click", () => showBaseOverview(base.key));
    item.appendChild(header);

    const body = el("div", { class: "accordion-body" });
    for (const u of base.unlocks.slice().sort((a, b) => (a.level || 0) - (b.level || 0))) {
      const lvl = u.level;
      const adv = ADV_BY_KEY[u.perk];
      if (!adv || isCombinationUnlocked(adv)) continue;
      const row = el("div", {
        class: `child-row ${adv.key === SELECTED_ADV_KEY ? "active" : ""}`,
        "data-advkey": adv.key,
      }, [
        iconImg(adv, "sm"),
        el("span", { class: "lvl", text: `Lv${lvl}` }),
        el("span", { class: "name", text: adv.name }),
        gradeBadgeNode(adv.grade),
      ]);
      row.addEventListener("click", (e) => { e.stopPropagation(); selectAdv(adv.key); });
      body.appendChild(row);
    }
    item.appendChild(body);
    sidebar.appendChild(item);
  }

  const rootPerks = DATA.advancedPerks.filter(perk => !perk.parentPerk);
  if (rootPerks.length) {
    sidebar.appendChild(el("div", { class: "sidebar-section-label", text: "독립 퍼크 및 확장 트리" }));
    for (const perk of rootPerks) {
      const item = el("div", { class: `accordion-item ${perk.key === SELECTED_ADV_KEY ? "open" : ""}` });
      const header = el("div", { class: "accordion-header" }, [
        iconImg(perk, "sm"),
        el("div", { class: "titles" }, [el("h3", { text: perk.name })]),
        gradeBadgeNode(perk.grade),
        el("span", { class: "chevron", text: "▸" }),
      ]);
      header.addEventListener("click", () => selectAdv(perk.key));
      item.appendChild(header);
      const body = el("div", { class: "accordion-body" });
      const row = el("div", { class: `child-row ${perk.key === SELECTED_ADV_KEY ? "active" : ""}` }, [
        el("span", { class: "name", text: `독립 퍼크 · 최대 Lv${perk.maxLevel || 20}` }),
      ]);
      row.addEventListener("click", () => selectAdv(perk.key));
      body.appendChild(row);
      for (const child of DATA.advancedPerks.filter(candidate => candidate.parentPerk === perk.key && !isCombinationUnlocked(candidate))) {
        const childRow = el("div", { class: `child-row ${child.key === SELECTED_ADV_KEY ? "active" : ""}`, "data-advkey": child.key }, [
          iconImg(child, "sm"),
          el("span", { class: "lvl", text: `Lv${child.unlockLevel || "?"}` }),
          el("span", { class: "name", text: child.name }),
          gradeBadgeNode(child.grade),
        ]);
        childRow.addEventListener("click", (event) => { event.stopPropagation(); selectAdv(child.key); });
        body.appendChild(childRow);
      }
      item.appendChild(body);
      sidebar.appendChild(item);
    }
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
  main.appendChild(renderSystemOverview());
}

function renderSystemOverview() {
  const systems = DATA.meta.systems;
  const event = systems.eventWaves;
  const rogue = systems.roguelike;
  const rank = systems.rank;
  const events = event.weightedEvents.map(item => `
    <tr><td>${escapeHtml(item.key)}</td><td>${Number(item.weight).toFixed(2)}</td></tr>
  `).join("");
  const container = el("div", { class: "system-overview" });
  container.innerHTML = `
    <div class="detail-header">
      <div class="detail-titles"><h2>Zedternal Tempered 게임 규칙</h2>
        <div class="subtitle">공식 소스 기본값 · 운영 서버의 별도 INI 설정은 다를 수 있습니다.</div>
      </div>
    </div>
    <div class="overview-grid">
      <section class="system-card"><h3>랭크</h3>
        <p><b>${rank.maxRank}레벨</b> · 칭호 ${rank.titles}개</p>
        <p>최대 누적 경험치 ${Number(rank.maxXp).toLocaleString()} XP</p>
        <p>이전 5개 랭크 구간을 새 랭크 하나로 압축하는 진행도 체계입니다.</p>
      </section>
      <section class="system-card"><h3>로그라이크 업그레이드</h3>
        <p>${rogue.enabled ? `매 ${rogue.waveInterval}웨이브마다 선택` : "비활성화"}</p>
        <p>중도 접속 보충: ${rogue.lateJoinCatchUp ? "활성화" : "비활성화"}${rogue.lateJoinCatchUp && rogue.lateJoinMaxSelections === 0 ? " · 놓친 선택 횟수 제한 없음" : ""}</p>
      </section>
      <section class="system-card"><h3>이벤트 웨이브</h3>
        <p>${event.enabled ? `웨이브 ${event.minWave}부터 · 웨이브당 ${Math.round(event.probability * 100)}% 확률` : "비활성화"}</p>
        <p>매치 최대 횟수: ${event.maxPerMatch === 0 ? "제한 없음" : event.maxPerMatch}</p>
        <p>가중치가 0보다 큰 이벤트 ${event.weightedEvents.length}종이 선택 대상입니다.</p>
      </section>
      <section class="system-card"><h3>퍼크 레벨 캡스톤</h3>
        <p>1차: Lv${systems.capstones.rank1Level} · 2차: Lv${systems.capstones.rank2Level}</p>
        <p>레벨 상한은 퍼크별로 표시합니다. 엔지니어 트리의 일부 퍼크는 최대 Lv10입니다.</p>
      </section>
    </div>
    <div class="section-title">현재 이벤트 웨이브 가중치</div>
    <table class="stat-table"><tr><th>이벤트 키</th><th>가중치</th></tr>${events}</table>
    <div class="section-title">퍼크 및 스킬 수록 범위</div>
    <div class="desc-line">베이스 퍼크 ${DATA.meta.basePerkCount}종 · 등록된 전직/독립 퍼크 ${DATA.meta.advancedPerkCount}종 · 표준/디럭스 스킬 항목 ${DATA.meta.totalSkills}개</div>
  `;
  return container;
}

function wireDetailEvents(root) {
  root.querySelectorAll(".unlock-chip").forEach(chip => {
    chip.addEventListener("click", () => selectAdv(chip.dataset.advkey));
  });
  root.querySelectorAll(".back-link").forEach(b => {
    b.addEventListener("click", () => {
      const parentKey = b.dataset.basekey;
      if (BASE_BY_KEY[parentKey]) showBaseOverview(parentKey);
      else if (ADV_BY_KEY[parentKey]) selectAdv(parentKey);
    });
  });
  root.querySelectorAll(".upper-perk-card[data-advkey]").forEach(card => {
    card.addEventListener("click", () => selectAdv(card.dataset.advkey));
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

  const grid = el("div", { class: "adv-grid" });
  for (const u of p.unlocks.slice().sort((a, b) => (a.level || 0) - (b.level || 0))) {
    const lvl = u.level;
    const adv = ADV_BY_KEY[u.perk];
    if (!adv || isCombinationUnlocked(adv)) continue;
    const requirementLabel = (adv.unlockRequirements || []).map(req => {
      const required = BASE_BY_KEY[req.perk] || ADV_BY_KEY[req.perk];
      return `${required ? required.name : req.perk} Lv${req.level}`;
    }).join(" + ");
    const card = el("div", {
      class: "adv-card",
      "data-advkey": adv.key,
    }, [
      iconImg(adv),
      el("div", { class: "adv-body" }, [
        el("div", { class: "lvl", text: `해금: ${requirementLabel || `Lv${lvl}`}` }),
        el("div", { class: "name", html: `${escapeHtml(adv.name)} ${gradeBadge(adv.grade)}` }),
        el("div", { class: "skillcount", text: `스킬 ${adv.skillCount}개` }),
      ]),
    ]);
    card.addEventListener("click", () => selectAdv(adv.key));
    grid.appendChild(card);
  }

  const skillsHtml = (p.skills || []).map(s => `
    <div class="skill-item ${s.disabled ? "skill-disabled" : ""}" data-skillkey="${escapeHtml(s.key)}">
      ${s.icon ? `<img class="skill-icon" src="${s.icon}" alt="" loading="lazy" onerror="this.style.display='none'">` : ""}
      <div class="skill-item-body">
        <h4>${escapeHtml(s.name)} <span style="color:var(--text-dim);font-weight:400;font-size:11px">(${s.key})</span>${s.disabled ? '<span class="disabled-badge">비활성화</span>' : ""}</h4>
        ${s.disabled ? `<div class="disabled-banner">🚫 이 스킬은 현재 인게임에서 비활성화되어 선택할 수 없습니다.${s.disabledNote ? ` (${escapeHtml(s.disabledNote)})` : ""}</div>` : ""}
        ${s.noData ? `<div class="empty-state" style="padding:10px">이 스킬은 게임 데이터에 설명이 없어 정확한 효과를 표시할 수 없습니다.</div>` : ""}
        ${s.standardDescRaw ? `<div class="std"><b>표준</b>${s.standardDescRaw}</div>` : ""}
        ${s.deluxeDescRaw ? `<div class="delx"><b>디럭스</b>${s.deluxeDescRaw}</div>` : ""}
        ${s.note ? `<div class="skillnote">${escapeHtml(s.note)}</div>` : ""}
      </div>
    </div>
  `).join("") || '<div class="empty-state" style="padding:10px">등록된 스킬 없음</div>';

  container.innerHTML = `
    <div class="detail-header">
      <img class="icon-img lg" src="${p.icon}" alt="" onerror="this.style.display='none'">
      <div class="detail-titles">
        <h2>${escapeHtml(p.name)}</h2>
        <div class="subtitle">베이스 퍼크 · 스킬 ${p.skillCount || 0}개</div>
      </div>
    </div>

    <div class="section-title">레벨별 수치</div>
    ${renderSliderSection(p.passiveStats, 20)}

    <div class="section-title">스킬 목록 (표준 / 디럭스)</div>
    <div class="skill-list">${skillsHtml}</div>

    <div class="section-title">퍼크 트리 (클릭해서 상세 보기)</div>
  `;
  container.appendChild(grid);
  wrap.appendChild(container);
  return wrap;
}

function renderAdvDetail(key) {
  const p = ADV_BY_KEY[key];
  const parent = BASE_BY_KEY[p.parentPerk] || ADV_BY_KEY[p.parentPerk];
  const unlockText = (p.unlockRequirements || []).map(req => {
    const requiredPerk = BASE_BY_KEY[req.perk] || ADV_BY_KEY[req.perk];
    return `${requiredPerk ? requiredPerk.name : req.perk} Lv${req.level}`;
  }).join(" + ");

  const descLines = p.descriptions.map(d =>
    `<div class="desc-line ${d.isCapstone ? "capstone" : ""}">${d.raw || escapeHtml(d.text)}</div>`
  ).join("") || '<div class="empty-state" style="padding:10px">등록된 게임 내 설명이 없습니다 — 아래 시스템 규칙 섹션을 참고하세요.</div>';
  const descNote = p.descriptions.length
    ? `<div style="font-size:11px;color:var(--text-dim);margin-bottom:6px">※ 아래 패시브 수치는 최대 레벨 ${p.maxLevel || 20} 기준입니다.</div>` : "";

  const hasPassive = p.passiveStats.length > 0;
  const upperPerks = p.parentPerk ? [] : DATA.advancedPerks.filter(child => child.parentPerk === p.key && !isCombinationUnlocked(child));
  const upperPerkCards = upperPerks.map(child => `
    <div class="adv-card upper-perk-card" data-advkey="${escapeHtml(child.key)}">
      <img class="icon-img" src="${escapeHtml(child.icon || "")}" alt="" onerror="this.style.display='none'">
      <div class="adv-body">
        <div class="lvl">해금: ${escapeHtml(requirementSummary(child))}</div>
        <div class="name">${escapeHtml(child.name)} ${gradeBadge(child.grade)}</div>
        <div class="skillcount">스킬 ${child.skillCount}개</div>
      </div>
    </div>`).join("");

  const skillsHtml = p.skills.map(s => `
    <div class="skill-item ${s.disabled ? "skill-disabled" : ""}" data-skillkey="${escapeHtml(s.key)}">
      ${s.icon ? `<img class="skill-icon" src="${s.icon}" alt="" loading="lazy" onerror="this.style.display='none'">` : ""}
      <div class="skill-item-body">
        <h4>${escapeHtml(s.name)} <span style="color:var(--text-dim);font-weight:400;font-size:11px">(${s.key})</span>${s.disabled ? '<span class="disabled-badge">비활성화</span>' : ""}</h4>
        ${s.disabled ? `<div class="disabled-banner">🚫 이 스킬은 현재 인게임에서 비활성화되어 선택할 수 없습니다.${s.disabledNote ? ` (${escapeHtml(s.disabledNote)})` : ""}</div>` : ""}
        ${s.noData ? `<div class="empty-state" style="padding:10px">이 스킬은 게임 데이터에 설명이 없어 정확한 효과를 표시할 수 없습니다.</div>` : ""}
        ${s.standardDescRaw ? `<div class="std"><b>표준</b>${s.standardDescRaw}</div>` : ""}
        ${s.deluxeDescRaw ? `<div class="delx"><b>디럭스</b>${s.deluxeDescRaw}</div>` : ""}
        ${s.note ? `<div class="skillnote">${escapeHtml(s.note)}</div>` : ""}
      </div>
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
        <h2>${escapeHtml(p.name)} ${gradeBadge(p.grade)}</h2>
        <div class="subtitle">${unlockText ? `해금 조건: ${escapeHtml(unlockText)}` : (parent ? `${escapeHtml(parent.name)} Lv${p.unlockLevel || "?"} 해금` : "독립 퍼크")} · 최대 Lv${p.maxLevel || 20} · 스킬 ${p.skillCount}개</div>
      </div>
    </div>

    <div class="section-title">세부 효과 (게임 내 텍스트)</div>
    ${descNote}
    ${descLines}

    ${hasPassive ? `<div class="section-title">레벨별 수치</div>${renderSliderSection(p.passiveStats, p.maxLevel || 20, p.valueSourceNote)}` : ""}

    ${renderFixedStatsSection(p.fixedStats, p.key === "Engineer" ? "Engineer 드론 기준 설정" : undefined, p.key === "Engineer" ? "수치는 템퍼드 소스의 ZTConfig_EngineerDrones 기본 설정에서 가져옵니다." : undefined)}

    ${upperPerks.length ? `<div class="section-title">상위 퍼크</div><div class="adv-grid">${upperPerkCards}</div>` : ""}

    <div class="section-title">스킬 목록 (표준 / 디럭스)</div>
    <div class="skill-list">${skillsHtml}</div>
  `;
  const wrap = document.createDocumentFragment();
  wrap.appendChild(container);
  return wrap;
}

function renderFixedStatsSection(fixedStats, title = "고정 효과 (레벨과 무관하게 일정)", note = "⚠ 아래 수치는 레벨업으로 커지지 않는 고정값입니다. \"Lv10/20 캡스톤\"은 해당 레벨에 도달하는 순간 1회 적용되는 효과입니다.") {
  if (!fixedStats || !fixedStats.length) return "";
  const rows = fixedStats.map(s => `
    <div class="fixed-stat-row">
      <span class="fixed-stat-label">${escapeHtml(s.label)}</span>
      <span class="fixed-stat-val">${s.display}</span>
      ${s.capstoneLevel ? `<span class="capstone-badge">Lv${s.capstoneLevel} 캡스톤</span>` : ""}
    </div>`).join("");
  return `
    <div class="section-title">${escapeHtml(title)}</div>
    <div style="font-size:11px;color:var(--text-dim);margin-bottom:6px">${escapeHtml(note)}</div>
    <div class="fixed-stat-list">${rows}</div>
  `;
}

function renderSliderSection(passiveStats, maxLevel, sourceNote = "") {
  if (!passiveStats.length) return '<div class="empty-state" style="padding:10px">등록된 패시브 수치 없음</div>';
  const rows = passiveStats.map(s => {
    const signClass = s.value < 0 ? "stat-neg" : s.value > 0 ? "stat-pos" : "";
    return `<tr data-perlevel="${s.value}" data-unit="${s.unit}" data-cap="${s.cap ?? ""}"><td>${escapeHtml(s.label)}</td><td class="${signClass}">${s.display}</td><td class="live-val ${signClass}">${formatStat(s.value * maxLevel, s.unit, s.cap)}</td></tr>`;
  }).join("");
  return `
    <div style="font-size:11px;color:var(--text-dim);margin-bottom:2px">${escapeHtml(sourceNote || "⚠ 게임 내 상한(클램프)이 적용되는 항목이 있어 아래 수치는 단순 계산 참고값입니다. 수치는 KFZedternalUnlimited.ini의 현재(패치 반영) 값 기준입니다.")}</div>
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
    const cap = row.dataset.cap === "" ? null : Number(row.dataset.cap);
    row.querySelector(".live-val").textContent = formatStat(perLevel * lvl, row.dataset.unit, cap);
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
  if (unit === "health") return `${trimNum(value)} HP`;
  if (Number.isInteger(value)) return value.toLocaleString();
  return trimNum(value);
}

function formatStat(value, unit, cap = null) {
  if (cap != null && Number.isFinite(cap)) value = value >= 0 ? Math.min(value, cap) : Math.max(value, cap);
  return formatByUnit(value, unit);
}

function trimNum(n) {
  return (Math.round(n * 100) / 100).toString();
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
    for (const s of base.skills || []) {
      SEARCH_INDEX.push({
        type: "base",
        navKey: base.key,
        ownKey: s.key,
        name: s.name,
        sub: `스킬 · ${base.name}`,
        search: `${s.name} ${s.key} ${s.standardDesc || ""} ${s.deluxeDesc || ""}`.toLowerCase(),
      });
    }
  }
  for (const adv of DATA.advancedPerks) {
    const parent = BASE_BY_KEY[adv.parentPerk];
    SEARCH_INDEX.push({
      type: "adv",
      navKey: adv.key,
      ownKey: adv.key,
      name: adv.name,
      sub: `전직 퍼크 · ${parent ? parent.name : ""}`,
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
  if (item.ownKey !== item.navKey) {
    requestAnimationFrame(() => {
      const el = document.querySelector(`.skill-item[data-skillkey="${CSS.escape(item.ownKey)}"]`);
      if (el) {
        el.scrollIntoView({ behavior: "instant", block: "center" });
        el.classList.add("skill-highlight");
        setTimeout(() => el.classList.remove("skill-highlight"), 1600);
      }
    });
  }
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
