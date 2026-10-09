let DATA = null;
let ADV_BY_KEY = {};
let BASE_BY_KEY = {};
let OPEN_BASE_KEY = null;
let SELECTED_ADV_KEY = null;
let AURORA_VIEW = false;
let AURORA_MODE = null;
let PATCH_NOTES_VIEW = false;
let SEARCH_INDEX = [];
let SEARCH_RESULTS = [];
let SEARCH_ACTIVE_IDX = -1;

// 표시값은 빌드 시 운영 폴더의 KFZedternalReborn_Game.ini에서 읽습니다.
// 표시값 = (실제값 + 1) / 2 로 절반만 반영해 서술합니다.
const DAMAGE_GIVEN_STATS = [
  { label: "화염 피해", real: 0.5 },
  { label: "지면 화염 피해", real: 0.4 },
  { label: "네이팜 피해", real: 0.4 },
  { label: "폭발 피해", real: 0.4 },
  { label: "폭발 파편 피해", real: 0.5 },
  { label: "메딕 수류탄(독성) 피해", real: 0.25 },
  { label: "베기 피해", real: 0.85 },
  { label: "관통 피해", real: 0.85 },
  { label: "둔기 피해", real: 0.85 },
  { label: "샷건 피해", real: 0.6 },
];
const DAMAGE_TAKEN_STATS = [
  { label: "허스크 자폭 피해", real: 1.2 },
  { label: "플레쉬파운드 킹 가슴빔 피해", real: 0.75 },
  { label: "한스 유탄 피해", real: 0.75 },
  { label: "가부장 미사일 피해", real: 0.75 },
  { label: "여장부 플라즈마포 피해", real: 0.75 },
  { label: "허스크 화염방사기 피해", real: 1.25 },
  { label: "근접무기 소지 중 전체 피해", real: 0.75 },
];

const WEAPON_AURORA_STATS = [
  { label: "동결 투척자", value: 1.25 },
  { label: "동결 투척자 얼음 파편", value: 1.75 },
  { label: "센터파이어 MB464", value: 0.75 },
  { label: "윈체스터 1894", value: 0.75 },
  { label: "S&W 500", value: 0.8 },
  { label: "M99", value: 0.85 },
  { label: "레일건", value: 0.9 },
  { label: "허스크 캐논", value: 0.8 },
  { label: "RPG-7 탄두", value: 1.5 },
  { label: "RPG-7 후폭발", value: 10.0 },
  { label: "분쇄기 폭발", value: 2.5 },
  { label: "HV 스톰 캐논", value: 0.85 },
  { label: "HRG 카붐스틱", value: 0.85 },
  { label: "석궁", value: 1.3 },
  { label: "컴파운드 보우", value: 1.5 },
  { label: "M14 EBR", value: 1.3 },
  { label: "FN FAL", value: 1.2 },
  { label: "MG3", value: 1.1 },
  { label: "MG3 변형", value: 1.1 },
  { label: "스토너 63A", value: 1.1 },
  { label: "미니건", value: 1.1 },
  { label: "MKB42", value: 1.2 },
  { label: "모신나강", value: 1.1 },
  { label: "모신나강 관통(스코프)", value: 1.4 },
  { label: "HRG 탄도 바운서", value: 0.6 },
  { label: "M4 샷건", value: 1.2 },
  { label: "네일건", value: 1.3 },
  { label: "기생충 이식기", value: 1.2 },
  { label: "C4", value: 2.0 },
  { label: "씰스퀄 폭발", value: 1.3 },
  { label: "씰스퀄 직격", value: 2.0 },
  { label: "중력폭구 폭발", value: 1.3 },
  { label: "중력폭구 대체 직격", value: 3.0 },
  { label: "마이크로웨이브 라이플", value: 1.4 },
  { label: "G18", value: 1.25 },
  { label: "G18 실드", value: 4.0 },
  { label: "G18 실드(임펄스)", value: 4.0 },
];

// 지금까지의 주요 패치 내역 요약 (최신순). 모든 커밋을 나열하진 않고,
// 플레이어가 체감할 만한 굵직한 변경사항만 추립니다.
const PATCH_NOTES = [
  {
    date: "2026-10-07",
    items: [
      "서포트 전직에 뱅가드 추가, 기술자 해금을 Support 5로 옮기고 뱅가드 10·히드라 15 순으로 정렬",
      "뱅가드 기본 효과·10/20레벨 캡스톤과 7종 스킬을 최신 소스 기준으로 등록",
      "자본가 전직 표시명을 도박꾼/딜러/타이쿤으로 정리하고, 5/10/15레벨 해금 설명을 갱신",
      "유령 감시자 이미지 예고를 재앙 발동 10초 전부터 시작하도록 수정",
    ],
  },
  {
    date: "2026-10-05",
    items: [
      "퍼크 트리를 운영 서버 KFZedternalUnlimited.ini의 활성 PerkUnlockRules 43개 기준으로 재작성",
      "자본가 전직을 도박꾼 Lv10, 웨이브 도박꾼 Lv5, 타이쿤 Lv15로 동기화하고 비활성 규칙 퍼크를 목록에서 제외",
      "유령·지킬 & 하이드의 숨겨진 퍼크 해금 조건을 운영 INI에 맞춤",
      "자본가와 엔지니어를 베이스 퍼크와 같은 목록 형식으로 표시하고 정적 퍼크 문구 제거",
      "현재 장착 무기에 적용 중인 보너스 요약과 전체 누적 능력치 패널 추가 (ToggleStats 또는 mutate stats)",
      "지킬 & 하이드의 이동·재장전 패시브를 레벨당 +1%, Lv20 +20%로 수정",
      "기술자(아티피서)를 서포트 무기별 숙련 단계와 현재 6종 스킬 기준으로 갱신",
      "웬디고의 첫 사격·레벨 10/20 매복 보너스, 격리, 트로피 사냥 수치를 최신 구현과 동기화",
    ],
  },
  {
    date: "2026-10-01",
    items: [
      "사이트 데이터 기준을 ZedternalTempered 소스와 SV_Zedternal_Tempered 운영 설정으로 전환",
      "퍼크, 스킬, 피해 오로라 수치를 운영 INI에서 생성하도록 변경",
    ],
  },
  {
    date: "2026-07-10",
    items: [
      "베이스 퍼크(10종)에도 전직 퍼크와 동일한 스킬 목록(표준/디럭스 설명, 비활성화 스킬 표시) 추가",
      "전직 퍼크 상세페이지에 잘못 표시되던 '베이스 퍼크' 라벨을 '전직 퍼크'로 수정",
      "무기 밸런스 오로라에 신규 무기 다수 반영, 강한 버프/너프 항목 색상 강조",
      "제드 웨이브 스폰 비율 조정 — 30웨이브까지 잡제드:중보스 비율이 점진적으로 8:2에 수렴하도록 튜닝",
      "어고니 / 버서커 / 프로스트 너프, 웬디고 버프 반영",
    ],
  },
  {
    date: "2026-07-07",
    items: [
      "모든 퍼크 설명란을 정체성 중심의 짧고 명확한 문구로 전면 간소화 (레벨20 풀스킬 장문 설명 삭제)",
      "최근 버프/너프 태그 위치를 등급 배지 옆으로 이동",
      "메트로놈 · 심비오트 심화 매커니즘 상세 설명 추가",
      "방어구/저항력 용어 통일, 대규모 밸런스 패치 반영",
      "손상/반동/탄퍼짐 마스터 상한 완화 및 서버 사이드 ini 동기화",
    ],
  },
  {
    date: "2026-07-06",
    items: [
      "패시브 수치 표시 회귀 버그 수정, 파이어버그·데몰리션리스트 등급 조정",
      "매니악 재장전 속도 너프, 갬블러·타이쿤 밸런스 조정",
    ],
  },
  {
    date: "2026-07-05",
    items: [
      "밸런스 오로라(피해량 배율) 수치를 서버 최신값으로 동기화",
      "ZED타임 연장 계열 스킬 전반 너프",
      "4개 베이스 퍼크의 Lv15/20 전직 퍼크 슬롯 재배치",
    ],
  },
  {
    date: "2026-07-04",
    items: [
      "초반(1~3웨이브)이 쉽고 11~25웨이브가 밋밋했던 난이도 곡선 개선, 26웨이브 이후 급격한 난이도 상승 완화",
    ],
  },
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
  applyLiveAuroraData();
  ADV_BY_KEY = Object.fromEntries(DATA.advancedPerks.map(p => [p.key, p]));
  BASE_BY_KEY = Object.fromEntries(DATA.basePerks.map(p => [p.key, p]));

  document.getElementById("patchNotesBtn").addEventListener("click", showPatchNotes);

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

function applyLiveAuroraData() {
  const aurora = DATA.aurora;
  if (!aurora) return;
  if (aurora.damageGiven.length !== DAMAGE_GIVEN_STATS.length + WEAPON_AURORA_STATS.length ||
      aurora.damageTaken.length !== DAMAGE_TAKEN_STATS.length - 1) {
    console.error("Aurora labels do not match the server damage config.");
    return;
  }
  DAMAGE_GIVEN_STATS.forEach((stat, index) => { stat.real = aurora.damageGiven[index]; });
  DAMAGE_TAKEN_STATS.forEach((stat, index) => {
    stat.real = index === DAMAGE_TAKEN_STATS.length - 1
      ? aurora.holdingMelee
      : aurora.damageTaken[index];
  });
  WEAPON_AURORA_STATS.forEach((stat, index) => {
    stat.value = aurora.damageGiven[DAMAGE_GIVEN_STATS.length + index];
  });
}

function showBaseOverview(key) {
  OPEN_BASE_KEY = key;
  SELECTED_ADV_KEY = null;
  AURORA_VIEW = false;
  PATCH_NOTES_VIEW = false;
  renderSidebar();
  renderMainArea();
  document.getElementById("mainArea").scrollIntoView({ behavior: "instant", block: "start" });
}

function selectAdv(key) {
  const adv = ADV_BY_KEY[key];
  OPEN_BASE_KEY = adv.parentPerk;
  SELECTED_ADV_KEY = key;
  AURORA_VIEW = false;
  PATCH_NOTES_VIEW = false;
  renderSidebar();
  renderMainArea();
  document.getElementById("mainArea").scrollIntoView({ behavior: "instant", block: "start" });
}

function showAurora(mode) {
  AURORA_VIEW = true;
  AURORA_MODE = mode;
  PATCH_NOTES_VIEW = false;
  OPEN_BASE_KEY = null;
  SELECTED_ADV_KEY = null;
  renderSidebar();
  renderMainArea();
  document.getElementById("mainArea").scrollIntoView({ behavior: "instant", block: "start" });
}

function showPatchNotes() {
  PATCH_NOTES_VIEW = true;
  AURORA_VIEW = false;
  OPEN_BASE_KEY = null;
  SELECTED_ADV_KEY = null;
  renderSidebar();
  renderMainArea();
  document.getElementById("mainArea").scrollIntoView({ behavior: "instant", block: "start" });
}

function renderPatchNotesDetail() {
  const groups = PATCH_NOTES.map(g => `
    <div class="patch-note-group">
      <div class="patch-note-date">${g.date}</div>
      <ul class="strengths">${g.items.map(i => `<li>${escapeHtml(i)}</li>`).join("")}</ul>
    </div>
  `).join("");
  return `
    <div class="detail-header">
      <div class="ba-icon lg">🧾</div>
      <div class="detail-titles">
        <h2>패치 노트</h2>
      </div>
    </div>
    <div class="aurora-note">
      <div class="aurora-note-main">지금까지의 주요 변경사항을 최신순으로 정리했습니다. 사소한 수치 조정까지 전부 담지는 않았습니다.</div>
    </div>
    ${groups}
  `;
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

function weaponAuroraLi(w) {
  let style = "";
  if (w.value > 1.5) style = ' style="color:#00ff00;font-weight:600"';
  else if (w.value <= 0.7) style = ' style="color:crimson;font-weight:600"';
  return `<li${style}>${escapeHtml(w.label)}</li>`;
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
      <div class="aurora-note-main"> 제드터널 모드의 특성상 너무 강하거나 약한 무기를 밸런싱한, 버프 / 너프된 무기 리스트 입니다. <code>소스: KFZedternalReborn_Game.ini</code></div>
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
  const combinationPerks = DATA.advancedPerks.filter(isCombinationUnlocked);
  if (combinationPerks.length) sidebar.appendChild(renderCombinationPerksBox(combinationPerks));
  const baseDisplayKeys = new Set(["Capitalist", "Engineer"]);
  const baseDisplayPerks = [
    ...DATA.basePerks,
    ...["Capitalist", "Engineer"]
      .map(key => ADV_BY_KEY[key])
      .filter(Boolean),
  ];
  for (const base of baseDisplayPerks) {
    const isOriginalBase = Boolean(BASE_BY_KEY[base.key]);
    const children = isOriginalBase
      ? base.unlocks.map(unlock => ({ ...unlock, perkData: ADV_BY_KEY[unlock.perk] }))
      : DATA.advancedPerks
          .filter(perk => perk.parentPerk === base.key && !baseDisplayKeys.has(perk.key))
          .sort((a, b) => (a.unlockLevel || 0) - (b.unlockLevel || 0))
          .map(perk => ({ level: perk.unlockLevel, perk: perk.key, perkData: perk }));
    const isOpen = base.key === OPEN_BASE_KEY || base.key === SELECTED_ADV_KEY
      || children.some(child => child.perk === SELECTED_ADV_KEY);
    const item = el("div", { class: `accordion-item ${isOpen ? "open" : ""}`, "data-basekey": base.key });

    const header = el("div", { class: "accordion-header" }, [
      iconImg(base, "sm"),
      el("div", { class: "titles" }, [
        el("h3", { text: base.name }),
        el("div", { class: "grade", html: base.grade ? `등급 ${gradeBadge(base.grade)}` : "" }),
      ]),
      el("span", { class: "chevron", text: "▸" }),
    ]);
    header.addEventListener("click", () => isOriginalBase ? showBaseOverview(base.key) : selectAdv(base.key));
    item.appendChild(header);

    const body = el("div", { class: "accordion-body" });
    for (const u of children) {
      const adv = u.perkData;
      if (!adv) continue;
      const row = el("div", {
        class: `child-row ${adv.key === SELECTED_ADV_KEY ? "active" : ""}`,
        "data-advkey": adv.key,
      }, [
        iconImg(adv, "sm"),
        el("span", { class: "lvl", text: `Lv${u.level}` }),
        el("span", { class: "name", text: adv.name }),
      ]);
      if (adv.grade) row.appendChild(el("span", { class: "grade-badge-wrap", html: gradeBadge(adv.grade) }));
      row.addEventListener("click", (e) => { e.stopPropagation(); selectAdv(adv.key); });
      body.appendChild(row);
    }
    item.appendChild(body);
    sidebar.appendChild(item);
  }

  const independentPerks = DATA.advancedPerks.filter(perk =>
    !BASE_BY_KEY[perk.parentPerk] && !ADV_BY_KEY[perk.parentPerk]
    && !baseDisplayKeys.has(perk.key)
  );
  for (const perk of independentPerks) {
    const children = DATA.advancedPerks
      .filter(child => child.parentPerk === perk.key)
      .sort((a, b) => (a.unlockLevel || 0) - (b.unlockLevel || 0));
    const isOpen = perk.key === SELECTED_ADV_KEY || children.some(child => child.key === SELECTED_ADV_KEY);
    const item = el("div", { class: `accordion-item ${isOpen ? "open" : ""}` });
    const header = el("div", { class: "accordion-header" }, [
      iconImg(perk, "sm"),
      el("div", { class: "titles" }, [
        el("h3", { html: `${escapeHtml(perk.name)} ${gradeBadge(perk.grade)}` }),
        el("div", { class: "grade", text: perk.isStatic ? "정적 퍼크" : "독립 퍼크" }),
      ]),
      el("span", { class: "chevron", text: "▸" }),
    ]);
    header.addEventListener("click", () => selectAdv(perk.key));
    item.appendChild(header);

    const body = el("div", { class: "accordion-body" });
    for (const child of children) {
      const row = el("div", {
        class: `child-row ${child.key === SELECTED_ADV_KEY ? "active" : ""}`,
        "data-advkey": child.key,
      }, [
        iconImg(child, "sm"),
        el("span", { class: "lvl", text: `Lv${child.unlockLevel}` }),
        el("span", { class: "name", text: child.name }),
      ]);
      if (child.grade) row.appendChild(el("span", { class: "grade-badge-wrap", html: gradeBadge(child.grade) }));
      row.addEventListener("click", event => { event.stopPropagation(); selectAdv(child.key); });
      body.appendChild(row);
    }
    item.appendChild(body);
    sidebar.appendChild(item);
  }
}

function renderCombinationPerksBox(perks) {
  const item = el("div", {
    class: `accordion-item combination-perks-item ${perks.some(perk => perk.key === SELECTED_ADV_KEY) ? "open" : ""}`,
  });
  const header = el("div", { class: "accordion-header" }, [
    el("span", { class: "ba-icon", text: "🔗" }),
    el("div", { class: "titles" }, [
      el("h3", { text: "히든 퍼크" }),
      el("div", { class: "grade", text: `${perks.length}개 퍼크` }),
    ]),
    el("span", { class: "chevron", text: "▸" }),
  ]);
  header.addEventListener("click", () => item.classList.toggle("open"));
  item.appendChild(header);

  const body = el("div", { class: "accordion-body" });
  for (const perk of perks) {
    const row = el("div", {
      class: `child-row combination-perk-row ${perk.key === SELECTED_ADV_KEY ? "active" : ""}`,
      "data-advkey": perk.key,
    }, [
      iconImg(perk, "sm"),
      el("div", { class: "combination-perk-info" }, [
        el("div", { class: "combination-perk-heading" }, [
          el("span", { class: "name", text: perk.name }),
          el("span", { class: "grade-badge-wrap", html: gradeBadge("?") }),
        ]),
      ]),
    ]);
    row.addEventListener("click", event => { event.stopPropagation(); selectAdv(perk.key); });
    body.appendChild(row);
  }
  item.appendChild(body);
  return item;
}

function renderMainArea() {
  const main = document.getElementById("mainArea");
  main.innerHTML = "";

  if (PATCH_NOTES_VIEW) {
    main.innerHTML = renderPatchNotesDetail();
    wireDetailEvents(main);
    return;
  }
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
  root.querySelectorAll(".upper-perk-card[data-advkey]").forEach(card => {
    card.addEventListener("click", () => selectAdv(card.dataset.advkey));
  });
  root.querySelectorAll(".back-link").forEach(link => {
    link.addEventListener("click", () => {
      if (link.dataset.advkey) selectAdv(link.dataset.advkey);
      else showBaseOverview(link.dataset.basekey);
    });
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
  for (const u of p.unlocks) {
    const adv = ADV_BY_KEY[u.perk];
    if (!adv) continue;
    const card = el("div", {
      class: "adv-card",
      "data-advkey": adv.key,
    }, [
      iconImg(adv),
      el("div", { class: "adv-body" }, [
        el("div", { class: "lvl", text: `Lv${u.level} 해금` }),
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
        <div class="subtitle">베이스 퍼크 · 스킬 ${p.skillCount || 0}개</div>
      </div>
      ${recentChangeBadge}
      <div class="detail-grade">${gradeBadge(p.grade)}</div>
    </div>

    ${renderPerkSummarySection(p)}
    ${renderPassiveSection(p)}
    ${renderCapstoneSection(p)}
    ${renderSkillsSection(p.skills || [])}
    <div class="section-title perk-section-title">5. 상위 퍼크 트리</div>
    <div class="tree-hint">퍼크를 선택하면 상세 정보를 엽니다.</div>
  `;
  container.appendChild(grid);
  container.insertAdjacentHTML("beforeend", renderFullInfoSection(p, true));
  wrap.appendChild(container);
  return wrap;
}

function renderAdvDetail(key) {
  const p = ADV_BY_KEY[key];
  const parent = BASE_BY_KEY[p.parentPerk];
  const parentAdv = ADV_BY_KEY[p.parentPerk];
  const parentName = parent?.name || parentAdv?.name;
  const combination = isCombinationUnlocked(p);
  const unlockText = (p.unlockRequirements || []).map(unlockRequirementLabel).join(" + ");
  const achievementUnlockText = p.unlockAchievement === "NoTrader5Waves"
    ? " + 도쉬 지출 없이 5웨이브 연속 완료 업적" : "";
  const backLink = parent
    ? `<div class="back-link" data-basekey="${escapeHtml(parent.key)}">← ${escapeHtml(parent.name)} 개요로</div>`
    : parentAdv
      ? `<div class="back-link" data-advkey="${escapeHtml(parentAdv.key)}">← ${escapeHtml(parentAdv.name)} 개요로</div>`
      : "";
  const subtitle = combination
    ? `히든 퍼크 · <strong class="hidden-unlock-emphasis">${escapeHtml(unlockText)}</strong> · 스킬 ${p.skillCount}개`
    : p.baseDisplay || p.key === "Capitalist" || p.key === "Engineer"
    ? `베이스 퍼크 · 스킬 ${p.skillCount}개`
    : p.isStatic
    ? `정적 퍼크 · 최대 Lv20 · 스킬 ${p.skillCount}개`
    : parentName
      ? `${escapeHtml(parentName)} Lv${p.unlockLevel ?? "?"} 해금${achievementUnlockText} · 스킬 ${p.skillCount}개`
      : `독립 퍼크 · 스킬 ${p.skillCount}개`;

  const recentChangeBadge = renderRecentChangeBadge(p.recentChangeTag);
  const isBaseLikeRoot = p.key === "Capitalist" || p.key === "Engineer";
  const upperPerks = isBaseLikeRoot
    ? DATA.advancedPerks
        .filter(child => child.parentPerk === p.key && !isCombinationUnlocked(child))
        .sort((a, b) => (a.unlockLevel || 0) - (b.unlockLevel || 0))
    : [];
  const upperPerkCards = upperPerks.map(child => `
    <div class="adv-card upper-perk-card" data-advkey="${escapeHtml(child.key)}">
      <img class="icon-img" src="${escapeHtml(child.icon || "")}" alt="" loading="lazy" onerror="this.style.visibility='hidden'">
      <div class="adv-body">
        <div class="lvl">${escapeHtml(p.name)} Lv${child.unlockLevel} 해금</div>
        <div class="name">${escapeHtml(child.name)}</div>
        <div class="skillcount">스킬 ${child.skillCount}개</div>
      </div>
      ${child.grade ? `<span class="grade-badge-wrap">${gradeBadge(child.grade)}</span>` : ""}
    </div>`).join("");

  const container = el("div", {});
  container.innerHTML = `
    ${backLink}
    <div class="detail-header">
      <img class="icon-img lg" src="${p.icon}" alt="" onerror="this.style.display='none'">
      <div class="detail-titles">
        <h2>${escapeHtml(p.name)}</h2>
        <div class="subtitle">${subtitle}</div>
      </div>
      ${recentChangeBadge}
      <div class="detail-grade">${gradeBadge(p.grade)}</div>
    </div>

    ${renderPerkSummarySection(p)}
    ${renderPassiveSection(p)}
    ${renderCapstoneSection(p)}
    ${renderSkillsSection(p.skills || [])}
    ${isBaseLikeRoot ? `
      <div class="section-title perk-section-title">5. 상위 퍼크 트리</div>
      <div class="tree-hint">퍼크를 선택하면 상세 정보를 엽니다.</div>
      <div class="adv-grid">${upperPerkCards || '<div class="empty-state perk-empty">현재 활성화된 상위 퍼크가 없습니다.</div>'}</div>
    ` : ""}
  `;
  if (p.key !== "WaveGambler") container.insertAdjacentHTML("beforeend", renderFullInfoSection(p));
  const wrap = document.createDocumentFragment();
  wrap.appendChild(container);
  return wrap;
}

function renderPerkSummarySection(perk) {
  return `
    <div class="section-title perk-section-title">1. 설명</div>
    <div class="perk-role-summary">${escapeHtml(perk.role || perk.summary || "설명이 등록되지 않았습니다.")}</div>
    ${perk.summaryHtml ? `<div class="perk-explanation-detail">${perk.summaryHtml}</div>` : ""}
  `;
}

function renderPassiveSection(perk) {
  const stats = perk.passiveStats || [];
  const maxLevel = perk.maxLevel || 20;
  return `
    <div class="section-title perk-section-title">2. 패시브</div>
    ${renderSliderSection(stats, maxLevel, perk.valueSourceNote || "")}
  `;
}

function renderCapstoneSection(perk) {
  const descriptions = perk.capstoneDescriptions || (perk.descriptions || []).filter(description => description.isCapstone);
  const fixedCapstones = (perk.fixedStats || []).filter(stat => stat.capstoneLevel);
  if (!descriptions.length && !fixedCapstones.length) return "";
  const descriptionRows = descriptions.map(description =>
    `<div class="desc-line capstone">${description.raw || escapeHtml(description.text || "")}</div>`
  ).join("");
  const statRows = !descriptions.length ? fixedCapstones.map(stat => `
    <div class="capstone-stat-row"><span>${escapeHtml(stat.label)}</span><b>${escapeHtml(stat.display)}</b><small>Lv${stat.capstoneLevel}</small></div>
  `).join("") : "";
  return `
    <div class="section-title perk-section-title">3. 캡스톤</div>
    <div class="capstone-list">${descriptionRows}${statRows}</div>
  `;
}

function renderSkillsSection(skills) {
  const skillsHtml = skills.map(skill => `
    <div class="skill-item ${skill.disabled ? "skill-disabled" : ""}" data-skillkey="${escapeHtml(skill.key)}">
      ${skill.icon ? `<img class="skill-icon" src="${escapeHtml(skill.icon)}" alt="" loading="lazy" onerror="this.style.display='none'">` : ""}
      <div class="skill-item-body">
        <h4>${escapeHtml(skill.name)} <span class="skill-key">(${escapeHtml(skill.key)})</span>${skill.disabled ? '<span class="disabled-badge">비활성화</span>' : ""}</h4>
        ${skill.disabled ? `<div class="disabled-banner">🚫 현재 인게임에서 선택할 수 없습니다.${skill.disabledNote ? ` (${escapeHtml(skill.disabledNote)})` : ""}</div>` : ""}
        ${skill.noData ? '<div class="empty-state perk-empty">게임 설명과 수치 자료가 등록되지 않았습니다.</div>' : ""}
        ${skill.standardDescRaw ? `<div class="std"><b>표준</b>${skill.standardDescRaw}</div>` : ""}
        ${skill.deluxeDescRaw ? `<div class="delx"><b>디럭스</b>${skill.deluxeDescRaw}</div>` : ""}
        ${skill.note ? `<div class="skillnote">${escapeHtml(skill.note)}</div>` : ""}
      </div>
    </div>
  `).join("");
  return `
    <div class="section-title perk-section-title">4. 스킬 목록 (표준 / 디럭스)</div>
    <div class="skill-list">${skillsHtml || '<div class="empty-state perk-empty">별도 구매 스킬이 없습니다. 퍼크의 자동 효과와 규칙은 상세 정보에 정리했습니다.</div>'}</div>
  `;
}

function renderFullInfoSection(perk, isBase = false) {
  const passiveStats = perk.passiveStats || [];
  const fixedStats = perk.fixedStats || [];
  const descriptions = perk.descriptions || [];
  const maxLevel = perk.maxLevel || 20;
  const detailLevels = maxLevel > 10 ? [10, maxLevel] : [maxLevel];
  const detailLevelHeaders = detailLevels.map(level => `<th>${level === maxLevel ? `만렙 Lv${level}` : `Lv${level}`}</th>`).join("");
  const passiveRows = passiveStats.map(stat => `
    <tr><td>${escapeHtml(stat.label)}</td><td>${escapeHtml(stat.display)} / 레벨</td>${detailLevels.map(level => `<td>${escapeHtml(formatByUnit(stat.value * level, stat.unit))}</td>`).join("")}</tr>
  `).join("");
  const fixedRows = fixedStats.map(stat => `
    <tr><td>${escapeHtml(stat.label)}</td><td>${escapeHtml(stat.display)}</td><td>${stat.capstoneLevel ? `Lv${stat.capstoneLevel} 도달 시` : "고정 / 조건부"}</td></tr>
  `).join("");
  const descriptionHtml = descriptions.map(description => `
    <div class="desc-line ${description.isCapstone ? "capstone" : ""}">${description.raw || escapeHtml(description.text || "")}</div>
  `).join("");
  const detailSkillRows = (perk.skills || []).flatMap(skill => {
    const byKey = new Map();
    for (const stat of skill.rawValues || []) {
      const values = byKey.get(stat.key) || [];
      values.push(stat);
      byKey.set(stat.key, values);
    }
    return [...byKey.entries()].map(([key, values]) => `
      <tr><td>${escapeHtml(skill.name)} · ${escapeHtml(values[0].label || key)}</td><td>${escapeHtml(values[0].display)}</td><td>${escapeHtml(values[1]?.display || values[0].display)}</td></tr>
    `);
  }).join("");
  const extraSections = (perk.extraSections || []).map(section => `
    <div class="full-info-subtitle">${escapeHtml(section.title)}</div>
    ${section.note ? `<div class="full-info-note">${escapeHtml(section.note)}</div>` : ""}
    ${section.html}
  `).join("");
  const strengths = isBase && perk.strengths?.length
    ? `<div class="full-info-subtitle">강점</div><ul class="strengths">${perk.strengths.map(item => `<li>${escapeHtml(item)}</li>`).join("")}</ul>` : "";
  const weaknesses = isBase && perk.weaknesses?.length
    ? `<div class="full-info-subtitle">약점</div>${perk.weaknesses.map(item => `<div class="weak-item"><span class="sev-${escapeHtml(item.severity || "normal")}">${escapeHtml(item.label || item.skill || "")}</span> — ${escapeHtml(item.issue || "")}</div>`).join("")}` : "";
  return `
    <div class="section-title perk-section-title">6. 전체 상세 정보</div>
    <details class="perk-full-details">
      <summary>더 깊게 보기 · 세부 수치와 모든 작동 규칙</summary>
      <div class="perk-full-body">
        ${passiveRows ? `<div class="full-info-subtitle">레벨당 패시브 전체 수치</div><div class="table-scroll"><table class="stat-table compact-stat-table"><tr><th>항목</th><th>레벨당</th>${detailLevelHeaders}</tr>${passiveRows}</table></div>` : ""}
        ${fixedRows ? `<div class="full-info-subtitle">고정·조건부 수치 전체</div><div class="table-scroll"><table class="stat-table compact-stat-table"><tr><th>항목</th><th>수치</th><th>적용</th></tr>${fixedRows}</table></div>` : ""}
        ${detailSkillRows ? `<div class="full-info-subtitle">스킬 설정 수치 (표준 / 디럭스)</div><div class="table-scroll"><table class="stat-table compact-stat-table"><tr><th>스킬 / 항목</th><th>표준</th><th>디럭스</th></tr>${detailSkillRows}</table></div>` : ""}
        ${descriptions.length ? `<div class="full-info-subtitle">게임 내 퍼크 설명 원문</div>${descriptionHtml}` : ""}
        ${strengths}${weaknesses}${extraSections}
        ${!passiveRows && !fixedRows && !detailSkillRows && !descriptions.length && !strengths && !weaknesses && !extraSections
          ? '<div class="empty-state perk-empty">현재 공개할 추가 수치가 없습니다.</div>' : ""}
      </div>
    </details>
  `;
}

function renderSliderSection(passiveStats, maxLevel, sourceNote = "") {
  if (!passiveStats.length) return '<div class="empty-state" style="padding:10px">등록된 패시브 수치 없음</div>';
  const rows = passiveStats.map(s => {
    const signClass = s.value < 0 ? "stat-neg" : s.value > 0 ? "stat-pos" : "";
    return `<tr data-perlevel="${s.value}" data-unit="${s.unit}"><td>${escapeHtml(s.label)}</td><td class="${signClass}">${s.display}</td><td class="live-val ${signClass}">${formatByUnit(s.value * maxLevel, s.unit)}</td></tr>`;
  }).join("");
  return `
    <div style="font-size:11px;color:var(--text-dim);margin-bottom:2px">레벨 슬라이더에서 선택한 단계의 누적 수치를 표시합니다. ${sourceNote ? escapeHtml(sourceNote) : "수치는 운영 INI와 퍼크 구현 기준입니다."}</div>
    <div class="level-slider-row">
      <label for="levelSlider">퍼크 레벨</label>
      <input id="levelSlider" type="range" min="1" max="${maxLevel}" value="${maxLevel}">
      <span class="lvl-val" id="lvlValLabel">Lv ${maxLevel}</span>
    </div>
    <div class="table-scroll level-stat-scroll"><table class="stat-table">
      <tr><th>항목</th><th>레벨당</th><th>선택 레벨 값</th></tr>
      ${rows}
    </table></div>
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
  if (unit === "armor") {
    const sign = value >= 0 ? "+" : "";
    return `${sign}${trimNum(value)} AP`;
  }
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

function isCombinationUnlocked(perk) {
  return perk.isCombinationUnlocked === true || new Set((perk.unlockRequirements || []).map(req => req.perk)).size > 1;
}

function unlockRequirementLabel(requirement) {
  const source = BASE_BY_KEY[requirement.perk] || ADV_BY_KEY[requirement.perk];
  return `${source ? source.name : requirement.perk} Lv${requirement.level}`;
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
    const parent = BASE_BY_KEY[adv.parentPerk] || ADV_BY_KEY[adv.parentPerk];
    SEARCH_INDEX.push({
      type: "adv",
      navKey: adv.key,
      ownKey: adv.key,
      name: adv.name,
      sub: adv.baseDisplay ? "베이스 퍼크" : adv.isStatic ? "정적 퍼크" : `전직 퍼크 · ${parent ? parent.name : "독립"}`,
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
