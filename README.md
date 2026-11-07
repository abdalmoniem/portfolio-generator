# Resume and Portfolio Generator

This project is a collection of tools and scripts that generate a portfolio page, a web resume, and an ATS friendly PDF resume from a single JSON data file and a set of Jinja templates.

The project consists of the following parts:

- A JSON data file that contains information about the person, their education, work experience, skills, and projects. The data is organized as a nested dictionary, with each key corresponding to a section of the resume or portfolio.
- A set of Jinja templates that define the structure and layout of the portfolio, the web resume, and the PDF resume.
- A Python script that reads the JSON data file, parses it into a Python object, renders the Jinja templates, and converts the PDF template with WeasyPrint.

The project is designed to be easy to use and customize. Edit the JSON data file to add or change information, then run the script. You can also customize the templates and design tokens to change the layout and look of every output.

## What gets generated

| Source | Output |
| --- | --- |
| `templates/index_template.html` | `generated/index.html` |
| `templates/resume_template.html` | `generated/resume.html` |
| `templates/resume_pdf_template.html` | `generated/resume_pdf.html` |
| `generated/resume_pdf.html` | `generated/resume.pdf` |
| `generated/resume_pdf.html` | `generated/<First> <Last> Resumé.pdf` |

The two PDF files are written from a single rendered WeasyPrint document, so they always contain the same content. The accented file name uses `Resumé` on the final syllable rather than `Résumé`.

## Features

### Portfolio page

- Light and dark themes with a persistent toggle. The chosen theme is stored in `localStorage` and applied before first paint to avoid a flash.
- Hero section with avatar, name, role, contact rows, social icon links, and calls to action. The primary button jumps to Work Experience and the nav About link jumps to the summary.
- Animated hero background with pointer parallax, drifting blobs, and click particles. The canvas is skipped when reduced motion is requested.
- Reveal and skill bar animations that replay every time an element scrolls back into view.
- Project cards with tool filters and staggered masonry columns, so short cards never leave row sized holes.
- Aligned lower information grid. Education sits beside Volunteer and Languages sits beside Interests.
- Staggered galleries and skill lists built with CSS columns.
- Floating back to top button that appears after five percent of the document height.
- Responsive navigation, scroll spy, and a skip link for keyboard users.
- Link indicators only inside Work Experience, Projects, Skills, Education, and Volunteer.

### Web resume

- Matching light and dark themes with the same toggle controller as the portfolio.
- Theme aware top bar that never stays white in dark mode.
- Contact chips and social links that match the portfolio hero.
- Two column layout above 960px with Work Experience and Projects in the main column and Education, Skills, Languages, Interests, and extra fields in the aside. It collapses to one column on small screens.
- Print styles that drop the chrome and keep each entry together.

### PDF resume

- Plain text header with name, role, and contact records. There is no profile picture and no tinted card.
- LinkedIn and GitHub are real hyperlinks that render their local SVG plus a text label.
- Fixed section order: summary, then Education beside Volunteer and Languages beside Interests, then Work Experience, then Projects, then Skills, then any extra fields.
- Projects use two staggered masonry columns and skills use four compact columns with slim progress bars.
- `break-inside` rules keep every entry, project card, and skill on one page.
- Very small `0.25in` page margins to fit more content per page.
- No emoji or decorative glyphs in the text stream. The link hint is drawn from `templates/img/link.svg` as a background image so ATS parsers see clean text.

## Getting Started

To use this project, follow these steps:

1. Clone the repository to a local directory.
2. Edit `templates/portfolio.json` to add or change information about the person, their education, work experience, skills, and projects.
3. Run `just generate` or `uv run scripts/generate_portfolio.py` to build every output. The script creates the HTML pages, both PDF files, and copies the local CSS, JavaScript, fonts, and images into `generated/`.
4. Open `generated/index.html` in a web browser to view the portfolio.

`just watch` serves `generated/` at `http://localhost:8000` with LiveReload while you edit templates, styles, data, or scripts.

## Customizing the Templates

The templates are written in HTML and use Jinja syntax to access the data in the JSON file. The templates are organized into the following files:

- `templates/index_template.html`: The portfolio page with the hero, timeline, project filters, staggered card grids, and lower information grid.
- `templates/resume_template.html`: The web resume with the theme aware top bar and two column body.
- `templates/resume_pdf_template.html`: The ATS PDF source with the plain text header, paired information sections, projects, and compact skills.

Stylesheets live under `templates/css/`:

- `templates/css/fonts.css`: Self hosted local font faces (Montserrat, Nunito) served from `templates/fonts/`.
- `templates/css/tokens.css`: Shared design tokens for light and dark themes, spacing, radii, and typography.
- `templates/css/components.css`: Shared primitives used by both web pages, including contact chips, the scoped link indicator, and the theme toggle.
- `templates/css/portfolio.css`: Styles for the portfolio site (`index.html`), including the hero, staggered card grids, aligned info grid, galleries, and back to top button.
- `templates/css/resume.css`: Styles for the web resume (`resume.html`), including the two column body and top bar.
- `templates/css/resume_pdf.css`: Styles for the ATS PDF resume only (`resume_pdf.html`), including page margins, paired tables, project columns, and compact skills.
- `templates/css/main.css`: Legacy shared stylesheet that is no longer loaded by the templates.
- `templates/css/html5bp.css`, `templates/css/modern_normalize.css`: Base and normalization styles.

JavaScript lives under `templates/js/`:

- `templates/js/theme.js`: Shared light and dark theme controller used by `index.html` and `resume.html`.
- `templates/js/app.js`: Portfolio interactions, including the mobile nav, project filters, replayable reveal and skill animations, scroll spy, floating back to top button, and the hero canvas parallax and click particles.

## Theming

All colors, spacing, radii, and type sizes are defined in `templates/css/tokens.css`. Light values live on `:root` and dark values live under `[data-theme="dark"]`, with a `prefers-color-scheme` fallback when no theme has been stored. To change the palette, edit the tokens instead of individual component styles.

The theme is applied through `data-theme` on the `<html>` element. Each web template keeps a small inline pre-paint snippet in `<head>` so the stored theme is active before the page renders, and `theme.js` handles the toggle, the icon, and the browser theme color. If you add a page, include the same snippet and load `theme.js`.

## Generated assets and privacy

All fonts, CSS, JavaScript, and images are local to the project. Generation does not fetch any network resources: templates reference only relative paths under `templates/`, and WeasyPrint renders with `media_type="screen"` from the locally generated HTML. The former `google_fonts_css2.css` file was renamed to `fonts.css` and holds only local `@font-face` rules, so every build works offline.

The PDF link indicator uses `templates/img/link.svg` so the PDF text stream stays clean for ATS parsing. The web pages use a literal link glyph that is scoped to the five content sections where a link hint is useful.

To customize the templates, edit the HTML, CSS, and JavaScript files in the `templates` directory. The changes will be reflected in the generated portfolio, web resume, and PDF.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
