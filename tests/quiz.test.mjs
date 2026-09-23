import { test } from "node:test";
import assert from "node:assert/strict";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { scoreText, progressKey } = require("../content/assets/js/quiz.js");

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
