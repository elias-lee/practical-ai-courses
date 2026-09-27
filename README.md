# Practical AI

Two free, practical 8-class courses on artificial intelligence:

- **AI Literacy**: for non-technical learners. How AI works, prompting, grounding, checking
  output, agents, and safe and responsible use.
- **AI Engineering**: for technical learners. From computational thinking to an evaluated,
  secured multi-agent system with an orchestration layer, with tested Python labs.

**Read the courses online:** https://elias-lee.github.io/practical-ai-courses/

## Offline use

Download `ai-courses-learner-<version>.zip` from **Releases**, unzip it, and open `index.html`
in any browser. No internet or installation needed. The Engineering lab code is in the `labs/`
folder inside the zip. The instructor edition zip adds facilitation guides.

## For authors

### Layout

| Path | What it is |
|---|---|
| `content/` | Site pages (Markdown). `literacy/`, `engineering/`, shared pages at the top level |
| `content/shared/sidebars/` | "Know the Term" boxes, included with `--8<-- "shared/sidebars/<name>.md"` |
| `content/instructor/` | Instructor-only pages (instructor edition only) |
| `quizzes/<course>/<class>.yml` | Quiz questions; shown where a page contains `<!-- quiz: <course>/<class> -->` |
| `labs/` | Runnable lab code for AI Engineering |
| `hooks/quiz.py` | Build step that turns quiz YAML into HTML |
| `scripts/make_architecture_svg.py` | Regenerates the architecture diagrams |

### Quiz format

```yaml
- id: lit-c3-q1
  question: "Which change most improves a vague prompt?"
  options:
    - text: "Adding 'please'"
      correct: false
      why: "Politeness doesn't add the information the model is missing."
    - text: "Specifying audience, format and an example"
      correct: true
      why: "These tell the model exactly what a good answer looks like."
```

Every question needs exactly one correct option, and every option needs a `why`. The build fails
otherwise.

### Build and preview

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/mkdocs serve                                  # learner edition at http://127.0.0.1:8000
.venv/bin/mkdocs serve -f mkdocs.instructor.yml         # instructor edition
.venv/bin/pytest tests -q && node --test tests/quiz.test.mjs    # site tests
bash scripts/test_labs.sh                                         # every lab, one at a time
.venv/bin/mkdocs build && node scripts/check_site.mjs    # browser check: file://, no network
node scripts/screenshots.mjs index.html literacy/c3.html  # design review: light/dark, desktop/phone
```

`check_site.mjs` opens the built site in headless Chrome the way an offline reader would (from
disk, with the network cut off) and checks quizzes, copy buttons, icons, search and progress
tracking. Screenshots land in `.checks/`.

### Publishing

- **Website:** every push to `main` rebuilds the learner edition and deploys it to GitHub Pages.
- **Offline zips:** push a version tag and GitHub Actions attaches both editions to a Release:

```bash
git tag v0.3.0
git push origin v0.3.0
```

### Content rules

- Fictional or public data only.
- Audience-agnostic: write for professionals in any organization.
- Define every term the first time it is used; prefer analogies to math.
- Mark product, framework and legal facts "as of 2026".
