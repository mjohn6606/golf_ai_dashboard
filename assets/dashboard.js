document.addEventListener("DOMContentLoaded", async () => {
  try {
    // Example: Load your Rapsodo Excel data that has been converted to JSON via backend or script
    const response = await fetch("scripts/rapsodo_data.json");
    const data = await response.json();

    renderClubAverages(data);
    renderShotDispersion(data);
    renderCarryDistance(data);
    renderConsistency(data);
    renderSwingPosture(data);
    renderMobilityTrends(data);
  } catch (err) {
    console.error("Failed to load data:", err);
  }
});

function renderClubAverages(data) {
  const averagesDiv = document.getElementById("club-averages");
  averagesDiv.innerHTML = "";

  data.clubs.forEach(club => {
    const card = document.createElement("div");
    card.classList.add("average-card");
    card.innerHTML = `
      <h4>${club.name}</h4>
      <p><strong>Carry:</strong> ${club.avgCarry} yds</p>
      <p><strong>Ball Speed:</strong> ${club.avgBallSpeed} mph</p>
      <p><strong>Launch:</strong> ${club.avgLaunch}°</p>
    `;
    averagesDiv.appendChild(card);
  });
}

function renderShotDispersion(data) {
  const ctx = document.getElementById("shot-dispersion");
  new Chart(ctx, {
    type: "scatter",
    data: {
      datasets: data.shotDispersion.map(c => ({
        label: c.club,
        data: c.shots.map(s => ({ x: s.x, y: s.y })),
        pointRadius: 5
      }))
    },
    options: {
      plugins: { legend: { position: "bottom" } },
      scales: { x: { title: { display: true, text: "Left/Right (yds)" } },
                y: { title: { display: true, text: "Carry (yds)" } } }
    }
  });
}

function renderCarryDistance(data) {
  const ctx = document.getElementById("carry-distance");
  new Chart(ctx, {
    type: "bar",
    data: {
      labels: data.clubs.map(c => c.name),
      datasets: [{
        label: "Carry Distance (yds)",
        data: data.clubs.map(c => c.avgCarry)
      }]
    },
    options: { plugins: { legend: { display: false } } }
  });
}

function renderConsistency(data) {
  const ctx = document.getElementById("consistency-chart");
  new Chart(ctx, {
    type: "radar",
    data: {
      labels: data.clubs.map(c => c.name),
      datasets: [{
        label: "Consistency",
        data: data.clubs.map(c => c.consistencyScore)
      }]
    },
    options: { scales: { r: { min: 0, max: 100 } } }
  });
}

function renderSwingPosture(data) {
  const ctx = document.getElementById("swing-posture");
  new Chart(ctx, {
    type: "line",
    data: {
      labels: ["Tempo", "Rotation", "Hand Path"],
      datasets: [{
        label: "Swing Posture",
        data: [data.swingMetrics.tempo, data.swingMetrics.rotation, data.swingMetrics.handPath]
      }]
    }
  });
}

function renderMobilityTrends(data) {
  const ctx = document.getElementById("mobility-trends");
  new Chart(ctx, {
    type: "line",
    data: {
      labels: data.mobility.map(m => m.date),
      datasets: [{
        label: "Mobility Index",
        data: data.mobility.map(m => m.value)
      }]
    }
  });
}
