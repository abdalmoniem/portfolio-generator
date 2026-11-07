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
- `templates/resume_pdf_template.html` → `generated/resume_pdf.html`, then `generated/resume.pdf` and `generated/<First> <Last> Resumé.pdf` (spelling and non-ASCII filename are intentional).
- The PDF source is rendered once with WeasyPrint and both PDF files are written from that document, so the two outputs never drift.
- Assets are copied only from `templates/{css,fonts,img,js}`: CSS `*.css`, JS `*.js`, fonts `*.ttf`, images `*.*`.
- Stylesheets: `templates/css/{fonts,tokens,components,portfolio,resume,resume_pdf}.css` (plus legacy `main.css`, `html5bp.css`, `modern_normalize.css`) → `generated/css/`. Fonts are self-hosted from `templates/fonts/`; `fonts.css` holds the local `@font-face` rules and `google_fonts_css2.css` was renamed to it.
- `templates/img/link.svg`, `linkedin.svg`, `github.svg` are rendered inline through `svg_data` where an icon is needed.

## Design system

- `templates/css/tokens.css` is the single source of colors, spacing, radii, and type scale. Light values live on `:root`; dark values live under `[data-theme="dark"]` plus a `prefers-color-scheme` fallback that is skipped when a theme is explicitly stored.
- `templates/js/theme.js` is the only theme controller. It reads and writes `localStorage["theme"]`, toggles `data-theme` on `<html>`, swaps the toggle icon and label, and updates `meta[name="theme-color"]`.
- Both web templates keep the inline pre-paint snippet in `<head>` so the stored theme is applied before first paint. Do not move that logic into `theme.js` alone and do not duplicate it in `app.js`.
- `templates/css/components.css` holds primitives shared by `index.html` and `resume.html`: `.contact-list` rows, `.chip` and `.contact-location`, the scoped link indicator, and `.theme-toggle`. It must never be loaded by the PDF template.
- The PDF template must load only `css/fonts.css` and `css/resume_pdf.css`.

## Layout patterns

- Portfolio project cards use `.card-grid` with CSS multi-column flow (`column-count`), so cards keep their natural height and a short card never leaves a row-sized hole. `.card-grid > .card` uses `break-inside: avoid`.
- The portfolio `.info-grid` is an aligned two-column grid: row one is Education beside Volunteer, row two is Languages beside Interests. Keep the source order in `index_template.html` unchanged so those pairs stay aligned at desktop widths.
- The portfolio `.gallery` and `.skill-list` use `column-width` masonry. Any new repeating item grid on the web pages should follow the same column and `break-inside: avoid` pattern.
- The web resume keeps `.resume-body` as a two-column grid above 960px (main Work/Projects plus aside Education/Skills/Languages/Interests/extra fields) and collapses to one column below that. `.resume-topbar` is theme aware and never stays white in dark mode.
- The PDF header is plain centered text: name, role, contact records, social links, summary. It must never include a profile picture or a tinted card.
- PDF section order is fixed: summary, then Education beside Volunteer and Languages beside Interests, then Work Experience, then Projects, then Skills, then extra fields. Skills must stay after Projects.
- PDF paired sections use the `.pairs` table with two aligned rows. PDF projects use `.project-columns` (`column-count: 2`) and PDF skills use four compact inline-block columns with 3.5pt bars. Grid layout is unsupported in WeasyPrint, so the PDF only uses tables, inline-block, floats, and multi-column flow.
- PDF `@page` margins are `0.25in` on all sides to maximize the text area. Every entry, project card, and skill sets `break-inside: avoid` so one item is never split across pages.
- Web pages render the literal `🔗` only for links inside the Work Experience, Projects, Skills, Education, and Volunteer sections, via `.link-section a[href]::after`. Keep `.link-section` off nav, hero, contact chips, social links, and the footer.
- The PDF must never contain `🔗` because it pollutes ATS text. The PDF link indicator is `img/link.svg` used as a background image in those same five sections.
- LinkedIn and GitHub in the PDF are real hyperlinks that inline their local SVG plus a text label. Keep them clickable and never add a non-text glyph to the PDF text stream.

## JavaScript behaviors

- `templates/js/app.js` handles the mobile nav toggle, project tool filters, replayable reveal and skill bar animations (they reset when scrolled out and replay when scrolled back in), nav scroll spy, and the floating back-to-top button.
- The back-to-top button appears after 5% of the document height and hides at the top. Its markup lives only in `index_template.html`, starts hidden from tab order and assistive tech, and uses the `.is-visible` state toggled by `app.js`.
- The hero canvas draws the pointer parallax blobs and click particles. It is skipped entirely under `prefers-reduced-motion: reduce` or when the hero markup is absent.
- `theme.js` loads before `app.js` on both web pages. The portfolio page loads both, the web resume loads only `theme.js`.

## Gotchas

- `generated/` is wiped at the start of every build and is gitignored. Never edit it or store sources there.
- The schema is the dataclasses in `scripts/generate_portfolio.py`, loaded with `dacite`. Add a new known field to both the dataclass and the JSON; `dacite` rejects type mismatches and missing required fields. Unknown JSON keys are `setattr`'d onto `portfolio` and exposed as `extra_fields`, which each template renders as a generic section.
- Jinja autoescape is deliberately off and templates use `| safe`; JSON strings contain raw HTML (`<b>`, `<i>`, `<a>`). Do not enable autoescape without auditing all content. All Python builtins are injected as Jinja globals.
- Social icons: `svg_path` is relative to `templates/`; the file is read into `svg_data` before rendering.
- WeasyPrint renders with `media_type="screen"`, so `@media print` rules are ignored. PDF layout and pagination live in `templates/css/resume_pdf.css` (`@page`, break rules).
- Adding a template requires updating `generated_items` in `scripts/generate_portfolio.py` and `watched_paths` in `scripts/watch.py`. Watched paths and asset-copy steps are hardcoded, so new files, directories, or extensions are not picked up automatically.
- `scripts/` modules import each other as top-level modules (e.g. `from logging_setup import ...`). Run them as files, not as `scripts.*` package imports.
- `scripts/watch.py` intentionally overrides LiveReload's `_setup_logging` to avoid a duplicate Tornado handler that breaks Rich log output.
- Keep `prefers-reduced-motion` handling intact in both CSS and `app.js`; animations must degrade to a static page, not disappear.
