# Resume and Portfolio Generator

This project is a collection of tools and scripts that generate a resume and portfolio based on a JSON data file and a set of Jinja templates.

The project consists of the following parts:

- A JSON data file that contains information about the person, their education, work experience, skills, and projects. The data is organized as a nested dictionary, with each key corresponding to a section of the resume or portfolio.
- A set of Jinja templates that define the structure and layout of the resume and portfolio. The templates are written in HTML and use Jinja syntax to access the data in the JSON file.
- A Python script that reads the JSON data file, parses it into a Python object, and renders the Jinja templates using the data. The script generates an HTML file for the resume and portfolio, and also generates a PDF version of the resume.

The project is designed to be easy to use and customize. The user can simply edit the JSON data file to add or change information, and then run the script to generate the resume and portfolio. The user can also customize the templates to change the layout and design of the resume and portfolio.

## Getting Started

To use this project, follow these steps:

1. Clone the repository to a local directory.
2. Edit the `portfolio.json` file to add or change information about the person, their education, work experience, skills, and projects.
3. Run the `generate_portfolio.py` script to generate the resume and portfolio. The script will create an HTML file for the resume and portfolio, and also generate a PDF version of the resume.
4. Open the HTML file in a web browser to view the resume and portfolio.

## Customizing the Templates

The templates are written in HTML and use Jinja syntax to access the data in the JSON file. The templates are organized into the following directories:

- `templates/resume_template.html`: This is the main template for the resume. It defines the structure and layout of the resume, and uses Jinja syntax to access the data in the JSON file.
- `templates/resume_pdf_template.html`: This is the main template for the PDF version of the resume. It defines the structure and layout of the PDF resume, and uses Jinja syntax to access the data in the JSON file.
- `templates/index_template.html`: This is the main template for the portfolio. It defines the structure and layout of the portfolio, and uses Jinja syntax to access the data in the JSON file.

Stylesheets live under `templates/css/`:

- `templates/css/fonts.css`: Self-hosted local font faces (Montserrat, Nunito) served from `templates/fonts/`.
- `templates/css/tokens.css`: Shared design tokens (colors, spacing, typography, etc.) used across the site.
- `templates/css/components.css`: Shared primitives used by both web pages (contact chips, link indicator, theme toggle).
- `templates/css/portfolio.css`: Styles for the portfolio site (`index.html`).
- `templates/css/resume.css`: Styles for the web resume (`resume.html`).
- `templates/css/resume_pdf.css`: Styles for the ATS PDF resume only (`resume_pdf.html`).
- `templates/css/main.css`: Legacy shared stylesheet for the resume and portfolio.
- `templates/css/html5bp.css`, `templates/css/modern_normalize.css`: Base/normalization styles.

JavaScript lives under `templates/js/`:

- `templates/js/theme.js`: Shared light/dark theme controller (localStorage + prefers-color-scheme) used by `index.html` and `resume.html`.
- `templates/js/app.js`: Portfolio interactions (nav, filters, replayable reveal/skill animations, floating back-to-top, hero pointer parallax and click particles).

Generated PDFs are `generated/resume.pdf` and `generated/<First> <Last> Resumé.pdf` (accent on the final syllable only). `resume_pdf.html` loads only `css/fonts.css` and `css/resume_pdf.css`, while the web pages additionally load `css/tokens.css` and `css/components.css`.

All fonts, CSS, JavaScript, and images are local to the project. Generation does not fetch any network resources: templates reference only relative paths under `templates/`, and WeasyPrint renders with `media_type="screen"` from the locally generated HTML. The PDF link indicator uses `templates/img/link.svg` so the PDF text stream stays clean for ATS parsing.

To customize the templates, simply edit the HTML and CSS files in the `templates` directory. The changes will be reflected in the generated resume and portfolio.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
