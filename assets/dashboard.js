// Load JSON Data + Render Charts
async function fetchJSON(path) {
  const res = await fetch(path);
  return await res.json();
}

document.addEventListener("DOMContentLoaded", async () => {
  const rapsodo = await fetchJSON("data/sample_rapsodo.json");
  const swing = await fetchJSON("data/sample_swing_analysis.json");
  const mobility = await fetchJSON("data/sample_mobility.json");

  renderRapsodoCharts(rapsodo);
  renderSwingCharts(swing);
  renderMobilityCharts(mobility);
  setupTabs();
});

function setupTabs() {
  const buttons = document.querySelectorAll(".tab-button");
  const tabs = document.querySelectorAll(".tab");

  buttons.forEach(btn => {
    btn.addEventListener("click", () => {
      buttons.forEach(b => b.classList.remove("active"));
      tabs.forEach(t => t.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById(btn.dataset.tab).classList.add("active");
    });
  });
}

// ---------------------- RAPTODO ----------------------

function renderRapsodoCharts(data) {
  const clubs = [...new Set(data.map(d => d.Club || "Unknown"))];

  const avgPerClub = clubs.map(club => {
    const shots = data.filter(d => d.Club === club);
    return shots.reduce((a, b) => a + (b["Total Distance"] || 0), 0) / shots.length;
  });

  const carryPerClub = clubs.map(club => {
    const shots = data.filter(d => d.Club === club);
    return shots.reduce((a, b) => a + (b["Carry Distance"] || 0), 0) / shots.length;
  });

  const consistency = clubs.map(club => {
    const shots = data.filter(d => d.Club === club).map(s => s["Carry Distance"] || 0);
    const mean = shots.reduce((a, b) => a + b, 0) / shots.length;
    const variance = shots.map(x => (x - mean) ** 2).reduce((a, b) => a + b, 0) / shots.length;
    return Math.sqrt(variance);
  });

  // Dispersion Chart
  new Chart(document.getElementById("dispersionChart"), {
    type: "scatter",
    data: {
      datasets: [{
        label: "Shot Dispersion",
        data: data.map(d => ({x: d["Offline"] || 0, y: d["Carry Distance"] || 0})),
        pointBackgroundColor: "#4CAF50"
      }]
    },
    options: { scales: {x: {title: {text: "Offline (yds)", display: true}}, y: {title: {text: "Carry (yds)", display: true}} } }
  });

  // Bar Charts
  new Chart(document.getElementById("avgClubChart"), {
    type: "bar",
    data: { labels: clubs, datasets: [{ label: "Average Distance", data: avgPerClub, backgroundColor: "#3b82f6" }] },
  });

  new Chart(document.getElementById("carryChart"), {
    type: "bar",
    data: { labels: clubs, datasets: [{ label: "Carry Distance", data: carryPerClub, backgroundColor: "#10b981" }] },
  });

  new Chart(document.getElementById("consistencyChart"), {
    type: "bar",
    data: { labels: clubs, datasets: [{ label: "Std Deviation", data: consistency, backgroundColor: "#f59e0b" }] },
  });
}

// ---------------------- SWING ----------------------

function renderSwingCharts(data) {
  // Simplified — assuming JSON has metrics like tempo, rotation, and hand_path arrays
  const tempo = data.map(d => d.tempo || 0);
  const rotation = data.map(d => d.rotation || 0);
  const handPath = data.map(d => d.hand_path || 0);

  new Chart(document.getElementById("tempoChart"), {
    type: "line",
    data: { labels: tempo.map((_, i) => i + 1), datasets: [{ label: "Tempo Ratio", data: tempo, borderColor: "#2563eb" }] },
  });

  new Chart(document.getElementById("rotationChart"), {
    type: "line",
    data: { labels: rotation.map((_, i) => i + 1), datasets: [{ label: "Rotation", data: rotation, borderColor: "#9333ea" }] },
  });

  new Chart(document.getElementById("handPathChart"), {
    type: "line",
    data: { labels: handPath.map((_, i) => i + 1), datasets: [{ label: "Hand Path", data: handPath, borderColor: "#ef4444" }] },
  });
}

// ---------------------- MOBILITY ----------------------

function renderMobilityCharts(data) {
  const dates = data.map(d => d.date);
  const scores = data.map(d => d.mobility_score || 0);

  new Chart(document.getElementById("mobilityChart"), {
    type: "line",
    data: {
      labels: dates,
      datasets: [{ label: "Mobility Score", data: scores, borderColor: "#14b8a6", tension: 0.3 }]
    },
  });
}
