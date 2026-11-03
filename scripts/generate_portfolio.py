# ruff: noqa: UP045
"""
Generate an HTML page from a Jinja template and a JSON data file.

The script assumes that the JSON file is in the same directory as the script,
and is named "portfolio.json". The script also assumes that the Jinja template
is in the same directory as the script, and is named "index_template.html".

The generated HTML page is saved to a file named "index.html", in the same
directory as the script.

The script also assumes that the JSON file is a serialized version of a
dataclass, and that the dataclass has a class variable named "TEMPLATE_VARS"
that contains a list of strings. The strings in the list are the names of
the variables that are available in the Jinja template.

The JSON file is read from disk, parsed into a Python object, and passed to
the Jinja template as a variable named "data". The Jinja template is then
rendered to HTML, and saved to disk.

The script can be run from the command line, with no arguments.

Example usage:

    python generate_portfolio.py

"""

import builtins
import logging
import os
import shutil
import sys
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

import json5
from dacite import from_dict
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

from logging_setup import configure_logging

configure_logging()
logger = logging.getLogger(__name__)


@dataclass
class ContactInfo:
    """Contact information class

    Attributes:
        email (str): Email address
        phone (str): Phone number
        location (str): Location
    """

    email: Optional[str]
    phone: Optional[str]
    location: Optional[str]


@dataclass
class SocialLink:
    """Social link class

    Attributes:
        label (str): Label of the social link
        url (str): URL of the social link
        svg_path (str): Path of the SVG icon
        svg_data (str): SVG data of the icon
    """

    label: str
    url: str
    svg_path: str
    svg_data: Optional[str]


@dataclass
class WorkExperience:
    """Work experience class

    Attributes:
        company (str): Company name
        position (str): Position
        url (str): URL of the company
        start_date (str): Start date of the work experience
        end_date (str): End date of the work experience
        summary (str): Summary of the work experience
        highlights (list[str]): Highlights of the work experience
    """

    company: str
    position: str
    url: Optional[str]
    start_date: str
    end_date: str
    summary: Optional[str]
    highlights: Optional[list[str]]


@dataclass
class Education:
    """Education class

    Attributes:
        institution (str): Institution of the education
        location (str): Location of the institution
        url (str): URL of the institution
        degrees (list[str]): Degrees of the education
        honors (list[str]): Honors of the education
        gpa_cumulative (str): Cumulative GPA of the education
        gpa_major (str): Major GPA of the education
        enrollment_date (str): Enrollment date of the education
        graduation_date (str): Graduation date of the education
    """

    institution: str
    location: str
    url: Optional[str]
    degrees: list[str]
    honors: Optional[list[str]]
    gpa_cumulative: Optional[str]
    gpa_major: Optional[str]
    enrollment_date: str
    graduation_date: str


@dataclass
class ProjectImage:
    """Project image class

    Attributes:
        img_path (str): Path to the image
        caption (str): Caption of the image
    """

    img_path: str
    caption: Optional[str]


@dataclass
class Project:
    """Project class

    Attributes:
        title (str): Title of the project
        summary (str): Summary of the project
        url (str): URL of the project
        highlights (list[str]): Highlights of the project
        images (list[ProjectImage]): List of images of the project
        tools (list[str]): List of tools used in the project
    """

    title: str
    summary: Optional[str]
    url: Optional[str]
    highlights: Optional[list[str]]
    images: Optional[list[ProjectImage]]
    tools: Optional[list[str]]


@dataclass
class Skill:
    """Skill class

    Attributes:
        name (str): Name of the skill
        proficiency (int): Proficiency of the skill
        proficiency_label (str): Proficiency label of the skill
    """

    name: str
    proficiency: Optional[int]
    proficiency_label: Optional[str]


@dataclass
class VolunteerExperience:
    """Volunteer experience class

    Attributes:
        organization (str): Organization of the volunteer experience
        position (str): Position of the volunteer experience
        url (str): URL of the organization
        start_date (str): Start date of the volunteer experience
        end_date (str): End date of the volunteer experience
        summary (str): Summary of the volunteer experience
        highlights (list[str]): Highlights of the volunteer experience
    """

    organization: str
    position: str
    url: Optional[str]
    start_date: str
    end_date: str
    summary: Optional[str]
    highlights: Optional[list[str]]


@dataclass
class Language:
    """Language class

    Attributes:
        name (str): Name of the language
        fluency (str): Fluency of the language
    """

    name: str
    fluency: Optional[str]


@dataclass
class InterestImage:
    """Interest image class

    Attributes:
        img_path (str): Path to the image
        caption (str): Caption of the image
    """

    img_path: str
    caption: Optional[str]


@dataclass
class Interest:
    """Interest class

    Attributes:
        name (str): Name of the interest
        summary (str): Summary of the interest
        images (list[InterestImage]): List of images related to the interest
    """

    name: str
    summary: Optional[str]
    images: Optional[list[InterestImage]]


@dataclass
class Portfolio:
    """Portfolio class

    Attributes:
        name (str): Name of the portfolio
        label (str): Label of the portfolio
        image_path (str): Path to the portfolio image
        contact (list[ContactInfo]): List of contact information
        summary (str): Summary of the portfolio
        base_url (str): Base URL of the portfolio
        social_links (list[SocialLink]): List of social links
        work_experience (list[WorkExperience]): List of work experiences
        projects (list[Project]): List of projects
        volunteer_experience (list[VolunteerExperience]): List of volunteer experiences
        education (list[Education]): List of education records
        skills (list[Skill]): List of skills
        interests (Optional[list[Interest]]): List of interests
        languages (Optional[list[Language]]): List of languages
        current_year (Optional[int]): The current year
    """

    first_name: str
    middle_name: Optional[str]
    last_name: str
    label: str
    image_path: str
    contact: list[ContactInfo]
    summary: str
    base_url: str
    social_links: list[SocialLink]
    work_experience: list[WorkExperience]
    projects: list[Project]
    volunteer_experience: list[VolunteerExperience]
    education: list[Education]
    skills: list[Skill]
    interests: Optional[list[Interest]]
    languages: Optional[list[Language]]
    current_year: Optional[int]


def delete_dir_contents(path: Path) -> None:
    """
    Deletes the contents of a given directory.

    This function is used to remove the previous build of the website
    before generating a new one.

    Args:
        path (Path): The path to the directory to be cleaned.
    """

    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # remove file or symlink
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # remove directory and its contents
        except Exception as e:  # noqa: BLE001
            logger.error(f"Failed to delete {file_path}. Reason: {e}")
            sys.exit(1)


def copy_files(src: Path, dest: Path, pattern: str = "*.*") -> None:
    """
    Copies files from a source directory to a destination directory.

    This function searches for files in the source directory matching the
    specified pattern and copies them to the destination directory. If the
    destination directory does not exist, it is created. The function reads
    the content of each file in binary mode and writes it to the corresponding
    file in the destination directory.

    Args:
        src (Path): The path to the source directory containing files to copy.
        dest (Path): The path to the destination directory where files are copied.
        pattern (str, optional): A glob pattern to match files in the source
                                 directory. Defaults to "*.*".
    """

    dest.mkdir(parents=True, exist_ok=True)
    for file in src.glob(pattern):
        target_path = dest / file.name
        with file.open("rb") as source, target_path.open("wb") as target:
            content = source.read()
            target.write(content)
            logger.info(f"Copied {file.name} to {target_path.name}")


def write_file(file_path: Path, file_content: str) -> None:
    logger.info(f"Generating {file_path.name} files...")
    with file_path.open("w", encoding="utf-8") as file_handle:
        written = file_handle.write(file_content)
        check_status(file_path.name, lambda: written == len(file_content))


def check_status(file_name: str, predicate: Callable[[], bool]) -> None:
    if predicate():
        logger.info(f"{file_name} generated successfully!")
    else:
        logger.error(f"Failed to generate {file_name}.")


def main() -> None:
    """
    Main entry point of the script.

    This function loads the Portfolio JSON data, loads the SVG files, sets up the Jinja environment,
    renders the HTML templates with the data, and writes the output to an HTML file.

    :return: None
    """

    try:
        SCRIPT_DIR = Path(__file__).resolve().parent
        TEMPLATES_DIR = SCRIPT_DIR / "../templates"
        GENERATED_DIR = SCRIPT_DIR / "../generated"
        portfolio_path = TEMPLATES_DIR / "portfolio.json"

        # Ensure the generated directory exists
        if not GENERATED_DIR.exists():
            logger.info(f"Creating directory: {GENERATED_DIR}")
            GENERATED_DIR.mkdir(parents=True, exist_ok=True)
        else:
            logger.info(f"Clearing directory: {GENERATED_DIR}")
            delete_dir_contents(GENERATED_DIR)

        # Load JSON data
        with portfolio_path.open(encoding="utf-8") as file_handle:
            raw_text = file_handle.read()
            raw_data = json5.loads(raw_text)
            portfolio = from_dict(data_class=Portfolio, data=raw_data)

        portfolio.current_year = datetime.now().year

        if portfolio.social_links:
            for link in portfolio.social_links:
                if link.svg_path:
                    with (TEMPLATES_DIR / link.svg_path).open(
                        encoding="utf-8"
                    ) as svg_file:
                        link.svg_data = svg_file.read()

        extra_fields = {}

        for key, value in raw_data.items():
            if not hasattr(portfolio, key):
                setattr(portfolio, key, value)
                extra_fields[key] = getattr(portfolio, key)

        index_template_path = TEMPLATES_DIR / "index_template.html"
        resume_template_path = TEMPLATES_DIR / "resume_template.html"
        resume_pdf_template_path = TEMPLATES_DIR / "resume_pdf_template.html"
        index_path = GENERATED_DIR / "index.html"
        resume_path = GENERATED_DIR / "resume.html"
        resume_pdf_path = GENERATED_DIR / "resume_pdf.html"
        pdf_output_paths = [
            GENERATED_DIR / "resume.pdf",
            GENERATED_DIR / f"{portfolio.first_name} {portfolio.last_name} Résumé.pdf",
        ]

        global_builtins = {name: value for name, value in (builtins.__dict__).items()}

        # Set up Jinja environment
        env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), autoescape=False)
        env.globals.update(**global_builtins)

        index_template = env.get_template(index_template_path.name)
        resume_template = env.get_template(resume_template_path.name)
        resume_pdf_template = env.get_template(resume_pdf_template_path.name)

        # Render the template with the data
        html_output = index_template.render(
            portfolio=portfolio, extra_fields=extra_fields
        )
        resume_output = resume_template.render(
            portfolio=portfolio, extra_fields=extra_fields
        )
        resume_pdf_output = resume_pdf_template.render(
            portfolio=portfolio, extra_fields=extra_fields
        )

        logger.info("Copying CSS files...")
        css_dir = TEMPLATES_DIR / "css"
        generated_css_dir = SCRIPT_DIR / "../generated/css"
        generated_css_dir.mkdir(parents=True, exist_ok=True)

        copy_files(
            src=css_dir,
            dest=generated_css_dir,
            pattern="*.css",
        )

        logger.info("Copying font files...")
        fonts_dir = TEMPLATES_DIR / "fonts"
        generated_fonts_dir = SCRIPT_DIR / "../generated/fonts"
        copy_files(
            src=fonts_dir,
            dest=generated_fonts_dir,
            pattern="*.ttf",
        )

        logger.info("Copying images...")
        images_dir = TEMPLATES_DIR / "img"
        favicon_path = TEMPLATES_DIR / "img/favicon.ico"
        generated_images_dir = SCRIPT_DIR / "../generated/img"

        copy_files(
            src=images_dir,
            dest=generated_images_dir,
            pattern="*.*",
        )

        copy_files(
            src=images_dir,
            dest=GENERATED_DIR,
            pattern=favicon_path.name,
        )

        logger.info("Copying JS files...")
        js_dir = TEMPLATES_DIR / "js"
        generated_js_dir = SCRIPT_DIR / "../generated/js"

        copy_files(
            src=js_dir,
            dest=generated_js_dir,
            pattern="*.js",
        )

        # Write the output to an HTML file
        write_file(index_path, html_output)
        write_file(resume_path, resume_output)
        write_file(resume_pdf_path, resume_pdf_output)

        # Convert HTML to PDF with WeasyPrint
        for pdf_output_path in pdf_output_paths:
            logger.info(f"Generating {pdf_output_path.name} file...")

            HTML(filename=str(resume_pdf_path), media_type="screen").write_pdf(
                str(pdf_output_path)
            )
    except KeyboardInterrupt:
        logger.warning("portfolio generation interrupted!")


if __name__ == "__main__":
    main()
