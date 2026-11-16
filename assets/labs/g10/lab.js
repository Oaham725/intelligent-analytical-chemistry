"use strict";

const form = document.getElementById("settings");
const sampleSelect = document.getElementById("sample");
const useRiInput = document.getElementById("use-ri");
const sigmaInput = document.getElementById("sigma");
const decisionBox = document.getElementById("decision");
const transferChoice = document.getElementById("transfer-choice");
const transferFeedback = document.getElementById("transfer-feedback");

function rankCandidates(sample, useRi, sigma) {
  return sample.candidates.map((candidate) => {
    const delta = Math.abs(candidate.delta_ri);
    const retention = Math.exp(-0.5 * (delta / sigma) ** 2);
    const score = useRi ? 0.7 * candidate.cosine + 0.3 * retention : candidate.cosine;
    return { ...candidate, delta, score };
  }).sort((a, b) => b.score - a.score || a.candidate.localeCompare(b.candidate));
}

function describeDecision(sample, rows, useRi) {
  const [first, second] = rows;
  const gap = first.score - second.score;
  if (sample.rs < 1) {
    return ["拒判 · 共洗脱风险", "Rs 低于 1.0。先检查提取离子流图与纯度，必要时改善分离或重新采集。", true];
  }
  if (!useRi) {
    return [`谱图首选 ${first.candidate}`, "当前仅展示谱图候选。核对 RI 条件并补充可比的保留或独立结构证据。", true];
  }
  if (first.score < 0.8 || gap < 0.05) {
    return ["拒判 · 证据不足或候选过近", `前两名分差为 ${gap.toFixed(4)}。最高分与分差须同时达到 0.80 和 0.05，建议补测标准品或 NMR。`, true];
  }
  return [`优先验证候选 ${first.candidate}`, `前两名分差为 ${gap.toFixed(4)}。下一步用同条件标准品或独立结构证据验证。`, false];
}

function render() {
  const sample = G10_DATA[sampleSelect.value];
  const useRi = useRiInput.checked;
  const sigma = Number(sigmaInput.value);
  const rows = rankCandidates(sample, useRi, sigma);
  document.getElementById("sigma-value").textContent = sigma;
  sigmaInput.disabled = !useRi;
  document.getElementById("metrics").innerHTML =
    `<span>LRI ${sample.ri.toFixed(1)}</span><span>Rs ${sample.rs.toFixed(2)}</span><span>前两名分差 ${(rows[0].score - rows[1].score).toFixed(4)}</span>`;
  document.getElementById("scores").innerHTML = rows.map((row) =>
    `<tr><th scope="row">${row.candidate}</th><td>${row.cosine.toFixed(4)}</td><td>${row.delta.toFixed(1)}</td><td>${row.score.toFixed(4)}</td></tr>`
  ).join("");
  const chart = document.getElementById("bars");
  chart.setAttribute("aria-label", rows.map((row) =>
    `${row.candidate} 余弦 ${row.cosine.toFixed(4)}${useRi ? `，融合 ${row.score.toFixed(4)}` : ""}`
  ).join("。"));
  chart.innerHTML = rows.map((row) => `<div class="bar-row"><strong>${row.candidate}</strong><div>
    <div class="track"><span class="spectral" style="width:${100 * row.cosine}%"></span></div>
    ${useRi ? `<div class="track"><span class="fused" style="width:${100 * row.score}%"></span></div>` : ""}
    </div></div>`).join("");
  const [title, explanation, pending] = describeDecision(sample, rows, useRi);
  decisionBox.classList.toggle("pending", pending);
  decisionBox.innerHTML = `<strong>${title}</strong><p>${explanation}</p>`;
}

const feedback = {
  "": "选择后查看原因。",
  apply: "需要先核对固定相和方法条件。不同固定相会改变相互作用及洗脱次序，当前 RI 差不能作为同方法分数使用。",
  check: "应暂停 RI 融合。选择同固定相和可比方法下的参照，或用标准品重测，并保留当前谱图候选。",
  confirm: "质谱相似度支持候选排序。结构接近或谱库缺失时仍可能误配，应补充可区分候选的证据。"
};

form.addEventListener("input", render);
form.addEventListener("reset", () => {
  transferChoice.value = "";
  transferFeedback.textContent = feedback[""];
  setTimeout(render, 0);
});
transferChoice.addEventListener("change", () => {
  transferFeedback.textContent = feedback[transferChoice.value];
});
render();
