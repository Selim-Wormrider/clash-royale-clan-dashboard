async function fetchJSON(endpoint) {
  const res = await fetch(endpoint);
  return await res.json();
}

async function loadData() {
  await Promise.all([
    loadMembers(),
    loadRaceSummary()
  ]);
  spawnCharacterRain();
}

/** Load enriched clan member data */
async function loadMembers() {
  const data = await fetchJSON("/api/clan-members");
  const container = document.getElementById("memberContainer");
  container.innerHTML = "";

  data.forEach(member => {
    const el = document.createElement("div");
    el.className = "card";
    el.innerHTML = `
  <div>
    <div class="card-title">${member.name}</div>
    <img class="role-badge-img" src="/static/images/${member.role.toLowerCase()}.png" alt="${member.role}">
    <div class="rank-label">${member.role}</div>
  </div>
  <div class="card-value">
    Level ${member.expLevel} • ${member.trophies} 🏆<br/>
    Donations: ${member.donations} / ${member.donationsReceived}<br/>
    Arena: ${member.arena?.name || 'Unknown'}<br/>
    ${member.lastSeen ? `Last seen: ${member.lastSeen}` : ''}
  </div>
  <button onclick="promptExcusePasscode('${member.tag}')">Excuse</button>
`;
    container.appendChild(el);
  });
}

/** Load current race or summary data */
async function loadRaceSummary() {
  let data = await fetchJSON("/api/current-riverrace-compact");

  if (!data || !data.clan) {
    document.getElementById("raceCompact").innerHTML = `
      <div class="card">⚠️ River Race data unavailable or failed to load.</div>
    `;
    return;
  }

  const container = document.getElementById("raceCompact");
  container.innerHTML = "";

  const clan = data.clan;
  container.innerHTML = `
    <div class="card">
      <div class="card-title">${clan.name}</div>
      <div class="card-value">
        Fame: ${clan.fame} | Score: ${clan.score} | Repairs: ${clan.repairPoints}
      </div>
    </div>
  `;

  const participants = data.participants || [];
  const top5 = participants.slice(0, 5);
  document.getElementById("topParticipants").innerHTML = `
    <h4>Top Participants</h4>
    ${top5.map(p => `
      <div class="card">
        <div class="card-title">${p.name}</div>
        <div class="card-value">Fame: ${p.fame}, Decks Used: ${p.decksUsed}</div>
        <div class="fame-bar-container">
          <div class="fame-bar" style="width:${(p.fame / 4000) * 100}%"></div>
        </div>
      </div>
    `).join('')}
  `;

  const logs = data.logs || [];
  const logsOut = document.getElementById("logsTimeline");
  logsOut.innerHTML = "<h4>War Log</h4>";
  logs.slice(0, 3).forEach(period => {
    period.items.forEach(entry => {
      const row = document.createElement("div");
      row.className = "card";
      row.innerHTML = `
        <div>Clan Tag: ${entry.clan.tag}</div>
        <div>Points: ${entry.pointsEarned}, Rank: ${entry.endOfDayRank}</div>
      `;
      logsOut.appendChild(row);
    });
  });

  document.getElementById("lastUpdated").innerText =
    "Updated: " + new Date().toLocaleString();

  renderFameChart(top5);
}

/** Chart.js bar chart for top players */
function renderFameChart(data) {
  const ctx = document.getElementById("fameChart").getContext("2d");
  const chartData = {
    labels: data.map(p => p.name),
    datasets: [{
      label: "Decks Used (Top 5)",
      data: data.map(p => p.decksUsed || 0),
      backgroundColor: "#f2c94c"
    }]
  };

  new Chart(ctx, {
    type: 'bar',
    data: chartData,
    options: {
      responsive: true,
      scales: {
        y: { beginAtZero: true }
      }
    }
  });
}

/** Week dropdown handler */
function changeWeek(offset) {
  const week = parseInt(offset);
  if (week === 0) return loadData();

  fetch('/api/summary/week/' + week)
    .then(res => res.json())
    .then(data => {
      const container = document.getElementById("raceCompact");
      container.innerHTML = '';
      data.forEach(member => {
        const el = document.createElement("div");
        el.className = "card";
        el.innerHTML = `
          <div>
            <div class="card-title">${member.name}</div>
            <div class="role-badge">${member.role}</div>
          </div>
          <div class="card-value">
            Fame: ${member.fame}, Decks: ${member.decks_used}/${member.decks_possible}
          </div>
        `;
        container.appendChild(el);
      });
    });
}

/** Excuse logic with 4-digit passcode */
function promptExcusePasscode(tag) {
  const pass = prompt("Enter 4-digit leader passcode:");
  if (!pass || pass.length !== 4) {
    alert("Invalid passcode.");
    return;
  }
  fetch(`/api/toggle-excuse/${tag}?code=${pass}`, { method: "POST" })
    .then(res => res.json())
    .then(() => loadData());
}

/** Manual refresh */
function triggerRefresh() {
  fetch("/api/refresh-race").then(() => loadData());
}

/** Collapse toggles */
function toggleSection(id) {
  const el = document.getElementById(id);
  el.style.display = el.style.display === "none" ? "block" : "none";
}

/** Character rain */
function spawnCharacterRain() {
  const rainLayer = document.getElementById("characterRain");
  rainLayer.innerHTML = "";
  const images = [
    "char1.png", "char2.png", "char3.png", "char4.png",
    "char5.png", "char6.png", "char7.png", "char8.png",
    "char9.png", "char10.png", "char11.png", "char12.png"
  ];
  for (let i = 0; i < 24; i++) {
    const img = document.createElement("img");
    img.src = `/static/images/${images[Math.floor(Math.random() * images.length)]}`;
    img.style.left = Math.random() * 100 + "vw";
    img.style.animationDuration = 10 + Math.random() * 15 + "s";
    img.style.animationDelay = Math.random() * 10 + "s";
    rainLayer.appendChild(img);
  }
}

window.onload = loadData;
