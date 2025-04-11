async function fetchJSON(endpoint) {
  const res = await fetch(endpoint);
  return await res.json();
}

async function loadData() {
  loadMapPins();
  await Promise.all([
    loadMembers(),
    loadRaceSummary()
  ]);
  spawnCharacterRain();
}
async function loadEligibility() {
  const data = await fetchJSON("/api/eligibility-report");
  const table = document.createElement("table");
  table.className = "eligible-table";
  table.innerHTML = `
    <thead>
      <tr>
        <th>Name</th><th>Role</th><th>Weeks</th><th>Status</th>
      </tr>
    </thead>
    <tbody>
      ${data.map(m => `
        <tr>
          <td>${m.name}</td>
          <td>${m.role}</td>
          <td>${m.weeksParticipated}/${m.weeksParticipated + m.weeksMissed}</td>
          <td>
            ${m.excused ? "Excused" : m.promotion ? "🔥 Promote" : m.demotion ? "⚠️ Demote" : "—"}
          </td>
        </tr>
      `).join('')}
    </tbody>
  `;
  document.getElementById("historyTable").appendChild(table);
}

async function loadMembers() {
  const data = await fetchJSON("/api/clan-members");
  const container = document.getElementById("memberContainer");
  container.innerHTML = "";

  data.forEach(member => {
    const el = document.createElement("div");
    el.className = "card";

    const lastSeen = member.lastSeen
      ? new Date(member.lastSeen).toLocaleString("en-US", {
          month: "2-digit",
          day: "2-digit",
          year: "numeric",
          hour: "2-digit",
          minute: "2-digit",
          hour12: false
        })
      : "Unknown";

    el.innerHTML = `
      <div class="toggle-switch">
        <input type="checkbox" class="excuse-toggle" onchange="promptExcusePasscode('${member.tag}', this)" ${member.excused ? "checked" : ""}>
      </div>
      <div>
        <div class="card-title">${member.name}</div>
        <img class="role-badge-img" src="/static/images/${member.role.toLowerCase()}.png" alt="${member.role}">
        <div class="rank-label">${member.role}</div>
      </div>
      <div class="card-value">
        Level ${member.expLevel} • ${member.trophies} 🏆<br/>
        Donations: ${member.donations} / ${member.donationsReceived}<br/>
        Arena: ${member.arena?.name || 'Unknown'}<br/>
        Fame (last war): ${member.fame || 0}<br/>
        Decks used: ${member.decksUsed || 0}<br/>
        Last seen: ${lastSeen}
      </div>
    `;
    container.appendChild(el);
  });
}

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

function renderFameChart(data) {
  const ctx = document.getElementById("fameChart").getContext("2d");

  // For now, mock role logic
  let promotion = 0, demotion = 0, excused = 0, neutral = 0;

  data.forEach(p => {
    if (p.excused) {
      excused++;
    } else if (p.decksUsed === 4) {
      promotion++;
    } else if (p.decksUsed <= 2) {
      demotion++;
    } else {
      neutral++;
    }
  });

  const pieData = {
    labels: ["Promotion Eligible", "Demotion Risk", "Excused", "Neutral"],
    datasets: [{
      data: [promotion, demotion, excused, neutral],
      backgroundColor: ["#28a745", "#dc3545", "#ffc107", "#6c757d"]
    }]
  };

  new Chart(ctx, {
    type: 'pie',
    data: pieData,
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: 'bottom',
          labels: { color: "#fff" }
        }
      }
    }
  });
}

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
            <div class="rank-label">${member.role}</div>
          </div>
          <div class="card-value">
            Fame: ${member.fame}, Decks: ${member.decks_used}/${member.decks_possible}
          </div>
        `;
        container.appendChild(el);
      });
    });
}

function triggerRefresh() {
  fetch("/api/refresh-race").then(() => loadData());
}

function promptExcusePasscode(tag, checkbox) {
  const pass = prompt("Enter 4-digit leader passcode:");
  if (!pass || pass.length !== 4) {
    alert("Invalid passcode.");
    checkbox.checked = !checkbox.checked;
    return;
  }
  fetch(`/api/toggle-excuse/${tag}?code=${pass}`, { method: "POST" })
    .then(() => loadData());
}

function toggleSection(id) {
  const el = document.getElementById(id);
  el.style.display = el.style.display === "none" ? "block" : "none";
}

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


async function loadMapPins() {
  const data = await fetchJSON("/api/member-locations");
  const mapContainer = document.getElementById("mapContainer");
  mapContainer.innerHTML = "";
  const map = L.map(mapContainer).setView([39.8283, -98.5795], 4);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap",
    maxZoom: 18,
  }).addTo(map);

  data.forEach(member => {
    L.marker([member.lat, member.lng])
      .addTo(map)
      .bindPopup(`<b>${member.name}</b>`);
  });
}
