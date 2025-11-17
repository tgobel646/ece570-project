const SHOW_ONLY_UNRATED = true;

let all = [];
let queue = [];
let idx = 0;

const elModel      = document.getElementById("model");
const elPrompt     = document.getElementById("prompt");
const elResponse   = document.getElementById("response");
const elCounter    = document.getElementById("counter");
const elUnrated    = document.getElementById("unratedCount");
const elIdBadge    = document.getElementById("idBadge");
const elRatingPill = document.getElementById("ratingPill");
const btnGood      = document.getElementById("btnGood");
const btnBad       = document.getElementById("btnBad");
const btnSkip      = document.getElementById("btnSkip");
const emptyMsg     = document.getElementById("emptyMsg");
const card         = document.getElementById("card");
const elCorrect      = document.getElementById("correctAnswer");

init();

async function init() {
  lockButtons(true);
  const res = await fetch("/responses");
  all = await res.json();

  queue = SHOW_ONLY_UNRATED
    ? all.filter(x => x.rating === null || x.rating === undefined)
    : all.slice();

  idx = 0;
  elUnrated.textContent = `unrated: ${queue.length}`;
  elCounter.textContent = `${queue.length ? 1 : 0} / ${queue.length}`;

  if (!queue.length) {
    card.classList.add("hidden");
    emptyMsg.classList.remove("hidden");
    return;
  }
  renderCurrent();
  lockButtons(false);
}

function current() {
  return queue[idx];
}

function renderCurrent() {
  const item = current();
  if (!item) return;
  elModel.textContent    = item.model ?? "—";
  elPrompt.textContent   = item.prompt ?? "—";
  elResponse.textContent = item.response ?? "—";
  elCorrect.textContent  = item.correct_answer ?? "—";
  elIdBadge.textContent  = `ID: ${item.id}`;
  elRatingPill.textContent =
    item.rating == null ? "unrated" :
    item.rating > 0 ? "rated: 👍" : "rated: 👎";
  elCounter.textContent = `${idx + 1} / ${queue.length}`;
}

async function rateAndNext(score) {
  const item = current();
  if (!item) return;
  lockButtons(true);
  try {
    await fetch(`/rate/${item.id}/${score}`, { method: "POST" });
  } catch (e) {
    alert("Rating failed. Is the backend running?");
  }
  idx++;
  if (idx >= queue.length) {
    done();
  } else {
    renderCurrent();
    lockButtons(false);
  }
}

function skip() {
  idx++;
  if (idx >= queue.length) {
    done();
  } else {
    renderCurrent();
  }
}

function done() {
  elCounter.textContent = `${queue.length} / ${queue.length}`;
  elRatingPill.textContent = "done";
  lockButtons(true);
  alert("All done. Thank you!");
}

btnGood.addEventListener("click", () => rateAndNext(1));
btnBad.addEventListener("click",  () => rateAndNext(-1));
btnSkip.addEventListener("click", skip);

document.addEventListener("keydown", (e) => {
  if (btnGood.disabled) return;
  if (e.key === "ArrowUp")   rateAndNext(1);
  if (e.key === "ArrowLeft") rateAndNext(-1);
  if (e.key === "ArrowRight") skip();
});

function lockButtons(locked) {
  btnGood.disabled = btnBad.disabled = btnSkip.disabled = locked;
}
