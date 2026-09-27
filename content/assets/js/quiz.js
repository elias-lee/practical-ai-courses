/* Interactive quizzes and class-completion tracking.
 * The quiz HTML is generated at build time by hooks/quiz.py.
 * No dependencies; works when the site is opened from file://.
 */
(function () {
  "use strict";

  function scoreText(correct, answered, total) {
    if (answered === 0) return "";
    if (answered < total) return answered + " / " + total + " answered · " + correct + " correct";
    return "Score: " + correct + " / " + total;
  }

  // Shown once every question is answered: which questions to revisit.
  function summaryText(missed, total) {
    if (missed.length === 0) return "All " + total + " correct. Well done.";
    var list = missed.length === 1 ? "question " + missed[0] : "questions " + missed.slice(0, -1).join(", ") + " and " + missed[missed.length - 1];
    return "Worth another look: " + list + ". Read the explanation under each answer.";
  }

  function progressKey(pagePath) {
    return "aicourse:done:" + pagePath;
  }

  if (typeof module !== "undefined" && module.exports) {
    module.exports = { scoreText: scoreText, summaryText: summaryText, progressKey: progressKey };
    return;
  }

  // localStorage can be missing or throw (private windows, blocked storage).
  var store = {
    get: function (k) { try { return window.localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { window.localStorage.setItem(k, v); } catch (e) { /* ignore */ } },
    remove: function (k) { try { window.localStorage.removeItem(k); } catch (e) { /* ignore */ } }
  };

  // "literacy/c3.html" — the last two path segments, stable across file:// and http(s)://
  function currentPage() {
    var parts = window.location.pathname.split("/").filter(Boolean);
    return parts.slice(-2).join("/");
  }

  function initQuiz(quiz) {
    var questions = quiz.querySelectorAll(".quiz-q");
    var scoreEl = quiz.querySelector(".quiz-score");
    var total = questions.length;
    var reset = document.createElement("button");
    reset.type = "button";
    reset.className = "quiz-reset";
    reset.textContent = "Try again";
    reset.hidden = true;
    scoreEl.after(reset);
    var summary = document.createElement("div");
    summary.className = "quiz-summary";
    summary.hidden = true;
    summary.setAttribute("aria-live", "polite");
    scoreEl.after(summary);

    function update() {
      var answered = quiz.querySelectorAll(".quiz-q.is-answered").length;
      var correct = quiz.querySelectorAll(".quiz-option.is-correct").length;
      scoreEl.textContent = scoreText(correct, answered, total);
      reset.hidden = answered === 0;
      summary.hidden = answered < total;
      if (answered === total) {
        var missed = [];
        questions.forEach(function (q, i) { if (!q.querySelector(".quiz-option.is-correct")) missed.push(i + 1); });
        summary.textContent = "";
        var p = document.createElement("p");
        p.textContent = summaryText(missed, total);
        summary.appendChild(p);
        if (missed.length) {
          var ul = document.createElement("ul");
          missed.forEach(function (n) {
            var q = questions[n - 1], li = document.createElement("li"), a = document.createElement("a");
            a.href = "#" + q.id;
            a.textContent = "Question " + n + ": " + q.querySelector(".quiz-question").textContent.replace(/^\s*\d+\s*/, "").slice(0, 90);
            li.appendChild(a);
            ul.appendChild(li);
          });
          summary.appendChild(ul);
        }
      }
    }

    questions.forEach(function (q) {
      q.querySelectorAll(".quiz-option").forEach(function (btn) {
        btn.addEventListener("click", function () {
          if (q.classList.contains("is-answered")) return;
          q.classList.add("is-answered");
          var right = btn.dataset.correct === "true";
          btn.classList.add(right ? "is-correct" : "is-wrong");
          q.querySelectorAll(".quiz-option").forEach(function (b) {
            b.disabled = true;
            if (b.dataset.correct === "true") b.classList.add("is-answer");
          });
          q.querySelectorAll(".quiz-why").forEach(function (w) { w.hidden = false; });
          update();
        });
      });
    });

    reset.addEventListener("click", function () {
      questions.forEach(function (q) {
        q.classList.remove("is-answered");
        q.querySelectorAll(".quiz-option").forEach(function (b) {
          b.disabled = false;
          b.classList.remove("is-correct", "is-wrong", "is-answer");
        });
        q.querySelectorAll(".quiz-why").forEach(function (w) { w.hidden = true; });
      });
      update();
    });
  }

  function initCompleteToggle(el) {
    var key = progressKey(currentPage());
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "complete-btn";
    function render() {
      var done = store.get(key) === "1";
      btn.textContent = done ? "✓ Class completed — click to undo" : "Mark class complete";
      btn.classList.toggle("is-done", done);
    }
    btn.addEventListener("click", function () {
      if (store.get(key) === "1") store.remove(key); else store.set(key, "1");
      render();
    });
    render();
    el.appendChild(btn);
  }

  // Course hub pages: <span data-progress-for="literacy/c3.html"></span> gets "✓ done".
  // Class steppers (links) keep their number and are only marked as done.
  function initProgressBadge(el) {
    if (store.get(progressKey(el.dataset.progressFor)) === "1") {
      if (el.tagName !== "A") el.textContent = "✓ done";
      el.classList.add("is-done");
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".quiz").forEach(initQuiz);
    document.querySelectorAll(".complete-toggle").forEach(initCompleteToggle);
    document.querySelectorAll("[data-progress-for]").forEach(initProgressBadge);
  });
})();
