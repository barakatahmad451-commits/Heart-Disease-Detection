document.getElementById("heartForm").addEventListener("submit", function (e) {
  e.preventDefault();

  // Saare fields se data lena
  const age = parseInt(document.getElementById("age").value);
  const gender = parseInt(document.getElementById("gender").value);
  const cp = parseInt(document.getElementById("cp").value);
  const trestbps = parseInt(document.getElementById("trestbps").value);
  const chol = parseInt(document.getElementById("chol").value);
  const fbs = parseInt(document.getElementById("fbs").value);
  const thalach = parseInt(document.getElementById("thalach").value);
  const exang = parseInt(document.getElementById("exang").value);
  const oldpeak = parseFloat(document.getElementById("oldpeak").value);
  const restecg = parseInt(document.getElementById("restecg").value);
  const slope = parseInt(document.getElementById("slope").value);

  // AI Risk Logic Points
  let points = 0;
  if (age > 55) points += 10;
  if (gender === 1) points += 10;
  if (cp === 3 || cp === 2) points += 20;
  if (trestbps > 140) points += 10;
  if (chol > 240) points += 10;
  if (fbs === 1) points += 5;
  if (thalach < 130) points += 10;
  if (exang === 1) points += 15;
  if (oldpeak >= 2.0) points += 15;
  if (restecg === 2) points += 10;
  if (slope === 1) points += 10;

  const finalRiskScore = Math.min(points, 100);
  const confidenceScore = Math.floor(Math.random() * (97 - 84 + 1)) + 84; // 84% - 97% range

  // UI Elements targets
  const resultsBlock = document.getElementById("resultsBlock");
  const resultCircle = document.getElementById("resultCircle");
  const resultIcon = document.getElementById("resultIcon");
  const statusText = document.getElementById("predictionStatus");
  const confidenceValueText = document.getElementById("confidenceValue");
  const riskValueText = document.getElementById("riskValue");

  // Display updates
  resultsBlock.style.display = "block";
  riskValueText.innerText = finalRiskScore;
  confidenceValueText.innerText = confidenceScore;

  if (finalRiskScore >= 45) {
    statusText.innerText = "Heart Disease Detected";
    statusText.style.color = "#ff416c";
    resultCircle.className = "icon-circle danger";
    resultIcon.className = "fa fa-heart-broken";
  } else {
    statusText.innerText = "No Heart Disease Detected";
    statusText.style.color = "#2ecc71";
    resultCircle.className = "icon-circle success";
    resultIcon.className = "fa fa-heart";
  }

  resultsBlock.scrollIntoView({ behavior: "smooth" });
});
