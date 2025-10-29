document.addEventListener("DOMContentLoaded", async () => {
  try {
    // Load data from your repo's data folder (works on GitHub Pages)
    const [rapsodoRes, swingRes, mobilityRes] = await Promise.all([
      fetch("../data/rapsodo.json"),
      fetch("../data/swing_analysis.json"),
      fetch("../data/mobility_data.json")
    ]);

    const rapsodoData = await rapsodoRes.json();
    const swingData = await swingRes.json();
    const mobilityData = await mobilityRes.json();

    renderClubAverages(rapsodoData);
    renderShotDispersion(rapsodoData);
    renderCarryDistance(rapsodoData);
    renderConsistency(rapsodoData);
    renderSwingPosture(swingData);
    renderMobilityTrends(mobilityData);

  } catch (err) {
    console.error("❌ Failed to load data:", err);
  }
});

/* -------------------------------
   📊 CLUB AVERAGE METRICS
--------------------------------*/
function renderClubAverages(data) {
  const container = document.getElementById("clubAverages");
  container.innerHTML = "";

  data.clubs.forEach(club => {
    const div = document.createElement("div");
    div.className = "club-card";
    div.innerHTML = `
      <h3>${club["Club Type"]}</h3>
      <p><strong>Carry:</strong> ${club.Carry_Distance_mean} yds</p>
      <p><strong>Total:</strong> ${club.Total_Distance_mean} yds</p>
      <p><strong>Ball Speed:</strong> ${club.Ball_Speed_mean} mph</p>
      <p><strong>Smash Factor:</strong> ${club.Smash_Factor_mean}</p>
    `;
    container.appendChild(div);
  });
}

/* -------------------------------
   🎯 SHOT DISPERSION
--------------------------------*/
function renderShotDispersion(data) {
  const ctx = document.getElementById("dispersionChart").getContext("2d");
  const datasets = Object.keys(data.dispersion).map((club, i) => ({
    label: club,
    data: data.dispersion[club].map((x, idx) => ({ x, y: idx })),
    showLine: false,
    pointRadius: 4
  }));

  new Chart(ctx, {
    type: "scatter",
    data: { datasets },
    options: {
      responsive: true,
      plugins: { title: { display: true, text: "Shot Dispersion per Club" } },
      scales: { x: { title: { text: "Side Carry (yds)", display: true } } }
    }
  });
}

/* -------------------------------
   🏌️ CARRY DISTANCE
--------------------------------*/
function renderCarryDistance(data) {
  const ctx = document.getElementById("carryChart").getContext("2d");
  const labels = data.clubs.map(c => c["Club Type"]);
  const carry = data.clubs.map(c => c.Carry_Distance_mean);

  new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [{ label: "Avg Carry (yds)", data: carry }]
    },
    options: {
      responsive: true,
      plugins: { title: { display: true, text: "Average Carry by Club" } }
    }
  });
}

/* -------------------------------
   📈 CONSISTENCY (Standard Deviation)
--------------------------------*/
function renderConsistency(data) {
  const ctx = document.getElementById("consistencyChart").getContext("2d");
  const labels = data.clubs.map(c => c["Club Type"]);
  const consistency = data.clubs.map(c => c.Carry_Distance_std);

  new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        { label: "Carry Consistency (Std Dev)", data: consistency, borderWidth: 2 }
      ]
    },
    options: {
      responsive: true,
      plugins: { title: { display: true, text: "Carry Distance Consistency" } }
    }
  });
}

/* -------------------------------
   🧠 SWING POSTURE (AI Insights)
--------------------------------*/
function renderSwingPosture(swing) {
  document.getElementById("swingTempo").innerText = `${swing.tempo}s`;
  document.getElementById("hipRotation").innerText = `${swing.avg_hip_rotation.toFixed(1)}°`;
  document.getElementById("shoulderRotation").innerText = `${swing.avg_shoulder_rotation.toFixed(1)}°`;

  const ctx = document.getElementById("handPathChart").getContext("2d");
  new Chart(ctx, {
    type: "scatter",
    data: {
      datasets: [
        {
          label: "Hand Path",
          data: swing.hand_path.map(([x, y]) => ({ x, y })),
          pointRadius: 3
        }
      ]
    },
    options: {
      responsive: true,
      plugins: { title: { display: true, text: "Hand Path (Swing Plane)" } },
      scales: { x: { min: 0, max: 1 }, y: { min: 0, max: 1, reverse: true } }
    }
  });
}

/* -------------------------------
   🤸 MOBILITY TRENDS
--------------------------------*/
function renderMobilityTrends(data) {
  const ctx = document.getElementById("mobilityChart").getContext("2d");
  const labels = data.map(d => d.date);
  const torso = data.map(d => d.torso_rotation_deg);
  const hip = data.map(d => d.hip_flex_deg);
  const shoulder = data.map(d => d.shoulder_flex_deg);

  new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        { label: "Torso Rotation", data: torso, borderWidth: 2 },
        { label: "Hip Flexibility", data: hip, borderWidth: 2 },
        { label: "Shoulder Flexibility", data: shoulder, borderWidth: 2 }
      ]
    },
    options: {
      responsive: true,
      plugins: { title: { display: true, text: "Mobility Trends Over Time" } }
    }
  });
}
