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

/** 🧍 Load enriched clan member data */
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
        <div class="role-badge">${member.role}</div>
      </div>
      <div class="card-value">
        Level ${member.expLevel} • ${member.trophies} 🏆<br/>
        Donations: ${member.donations} / ${member.donationsReceived}<br/>
        Arena: ${member.arena?.name || 'Unknown'}<br/>
        ${member.lastSeen ? `Last seen: ${member.lastSeen}` : ''}
      </div>
    `;
    container.appendChild(el);
  });
}

/** 🌊 Load river race summary, fallback refresh if empty */
async function loadRaceSummary() {
  let data = await fetchJSON("/api/summary");
  if (!Array.isArray(data) || data.length === 0) {
    await fetch("/api/refresh-race");
    data = await fetchJSON("/api/summary");
  }

  const container = document.getElementById("raceCompact");
  container.innerHTML = "";

  data.forEach(member => {
    const barWidth = Math.min((member.percent / 100) * 100, 100);
    const el = document.createElement("div");
    el.className = "card";
    el.innerHTML = `
      <div>
        <div class="card-title">${member.name}</div>
        <div class="role-badge">${member.role}</div>
        <div class="card-value">
          ${member.percent}% used (${member.used}/${member.total})<br/>
          Status: <b>${member.status}</b>
        </div>
        <div class="fame-bar-container">
          <div class="fame-bar" style="width:${barWidth}%"></div>
        </div>
      </div>
    `;
    container.appendChild(el);
  });

  document.getElementById("lastUpdated").innerText =
    "Last updated: " + new Date().toLocaleString();

  renderFameChart(data);
}

/** 📈 Render basic Chart.js */
function renderFameChart(data) {
  const ctx = document.getElementById("fameChart").getContext("2d");
  const top5 = data.sort((a, b) => b.used - a.used).slice(0, 5);
  const chartData = {
    labels: top5.map(p => p.name),
    datasets: [{
      label: "Decks Used (Top 5)",
      data: top5.map(p => p.used),
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

/** 🔄 Manual Refresh Button */
function triggerRefresh() {
  fetch("/api/refresh-race").then(() => loadData());
}

/** 🧩 Collapsibles */
function toggleSection(id) {
  const el = document.getElementById(id);
  el.style.display = el.style.display === "none" ? "block" : "none";
}

/** 🎭 Floating character rain animation */
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
