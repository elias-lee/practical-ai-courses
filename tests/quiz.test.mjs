import { test } from "node:test";
import assert from "node:assert/strict";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { scoreText, summaryText, progressKey } = require("../content/assets/js/quiz.js");

test("summaryText with nothing missed", () => {
  assert.equal(summaryText([], 7), "All 7 correct. Well done.");
});

test("summaryText lists missed questions naturally", () => {
  assert.equal(summaryText([3], 7), "Worth another look: question 3. Read the explanation under each answer.");
  assert.equal(summaryText([2, 5, 6], 7), "Worth another look: questions 2, 5 and 6. Read the explanation under each answer.");
});

test("scoreText while in progress", () => {
  assert.equal(scoreText(2, 3, 5), "3 / 5 answered · 2 correct");
});

test("scoreText when complete", () => {
  assert.equal(scoreText(4, 5, 5), "Score: 4 / 5");
});

test("scoreText before any answer is empty", () => {
  assert.equal(scoreText(0, 0, 5), "");
});

test("progressKey namespaces by page", () => {
  assert.equal(progressKey("literacy/c3.html"), "aicourse:done:literacy/c3.html");
});
