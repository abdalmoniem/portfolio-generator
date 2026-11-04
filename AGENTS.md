# AGENTS.md

Static portfolio/resume generator: Python scripts render Jinja templates from a JSON5 data file into `generated/`, plus PDFs via WeasyPrint. No web framework, package, tests, or CI.

## Commands

- `just generate` (`just g`) — sync deps, regenerate everything, print output file info.
- `just watch` (`just w`) — build once, then serve `generated/` at `http://localhost:8000` with LiveReload.
- `just sync` (`just s`) — only `uv sync`; run after dependency changes.
- Fast rebuild without syncing deps: `uv run scripts/generate_portfolio.py`.
- Requires Python 3.14 (see `pyproject.toml`), `uv`, and `just`. The venv is `.venv`.
- There is no test/lint/typecheck suite. Verify by regenerating and inspecting `generated/` HTML and PDF.

## Data and outputs

- Data lives at `templates/portfolio.json` (JSON5: comments, trailing commas, and unquoted keys are accepted), not at the repo root.
- `templates/index_template.html` → `generated/index.html`.
- `templates/resume_template.html` → `generated/resume.html`.
- `templates/resume_pdf_template.html` → `generated/resume_pdf.html`, then `generated/resume.pdf` and `generated/<First> <Last> Resumé.pdf` (non-ASCII filename is intentional).
- Assets are copied only from `templates/{css,fonts,img,js}`: CSS `*.css`, JS `*.js`, fonts `*.ttf`, images `*.*`.
- Stylesheets: `templates/css/{fonts,tokens,components,portfolio,resume,resume_pdf}.css` (plus legacy `main.css`, `html5bp.css`, `modern_normalize.css`) → `generated/css/`.

## Gotchas

- `generated/` is wiped at the start of every build and is gitignored. Never edit it or store sources there.
- The schema is the dataclasses in `scripts/generate_portfolio.py`, loaded with `dacite`. Add a new known field to both the dataclass and the JSON; `dacite` rejects type mismatches and missing required fields. Unknown JSON keys are `setattr`'d onto `portfolio` and exposed as `extra_fields`, which each template renders as a generic section.
- Jinja autoescape is deliberately off and templates use `| safe`; JSON strings contain raw HTML (`<b>`, `<i>`, `<a>`). Do not enable autoescape without auditing all content. All Python builtins are injected as Jinja globals.
- Social icons: `svg_path` is relative to `templates/`; the file is read into `svg_data` before rendering.
- WeasyPrint renders with `media_type="screen"`, so `@media print` rules are ignored. PDF layout/pagination lives in `templates/css/resume_pdf.css` (`@page`, break rules). `templates/resume_pdf_template.html` must load only `css/fonts.css` and `css/resume_pdf.css`; `main.css`, `html5bp.css`, and `portfolio.css` must not be loaded there.
- Adding a template requires updating `generated_items` in `scripts/generate_portfolio.py` and `watched_paths` in `scripts/watch.py`. Watched paths and asset-copy steps are hardcoded, so new files, directories, or extensions are not picked up automatically.
- `scripts/` modules import each other as top-level modules (e.g. `from logging_setup import ...`). Run them as files, not as `scripts.*` package imports.
- `scripts/watch.py` intentionally overrides LiveReload's `_setup_logging` to avoid a duplicate Tornado handler that breaks Rich log output.
- Shared web primitives:
  - `components.css` is shared by `index_template.html` and `resume_template.html` (contact chips, link indicator, theme toggle). It must NOT be loaded by `resume_pdf_template.html`.
  - `theme.js` is the single theme controller for both web pages; keep the inline pre-paint snippet in both templates to avoid a flash, and do not duplicate theme logic in `app.js`.
  - Web pages render the literal `🔗` only for links inside the Work Experience, Projects, Skills, Education, and Volunteer sections, via `.link-section a[href]::after`; the PDF must never contain that character because it pollutes ATS text, so the PDF uses `img/link.svg` in those same sections.
  - The back-to-top button appears at 5% of document height and hides at the top; its behavior lives in `app.js`.
