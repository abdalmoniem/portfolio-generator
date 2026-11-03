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
from jinja2 import Environment, FileSystemLoader, Template
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
        first_name (str): Given name
        middle_name (Optional[str]): Middle name
        last_name (str): Family name
        label (str): Professional label or title
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


class GeneratedItem:
    """HTML page to render from a Jinja template

    Attributes:
        template_path (Path): Path to the source template file
        output_path (Path): Path where rendered HTML is written
        env_template (Template): Loaded Jinja template ready for rendering
    """

    def __init__(
        self, template_path: Path, output_path: Path, env: Environment
    ) -> None:
        """
        Bind a template file to an output path using a shared Jinja environment.

        Args:
            template_path (Path): Path to the template under the templates directory.
            output_path (Path): Destination path for the generated HTML file.
            env (Environment): Jinja environment with loader and globals configured.

        :return: None
        """

        self.template_path: Path = template_path
        self.output_path: Path = output_path
        self.env_template: Template = env.get_template(self.template_path.name)


@dataclass
class CopyResource:
    """Static asset copy step for the generated site

    Attributes:
        src (Path): Source directory or file path to copy from
        dst (Path): Destination directory for copied files
        glob (str): Glob pattern passed to copy_files
        tag (str): Short label used in log messages for this copy step
    """

    src: Path
    dst: Path
    glob: str
    tag: str


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


def copy_files(src: Path, dest: Path, glob: str = "*.*") -> None:
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
        glob (str, optional): A glob pattern to match files in the source
                                 directory. Defaults to "*.*".
    """

    dest.mkdir(parents=True, exist_ok=True)
    for file in src.glob(glob):
        target_path = dest / file.name
        with file.open("rb") as source, target_path.open("wb") as target:
            content = source.read()
            target.write(content)
            logger.info(f"Copied {file.name} to {target_path.name}")


def write_file(file_path: Path, file_content: str) -> None:
    """
    Write text content to a file and verify the write succeeded.

    Args:
        file_path (Path): Path of the file to create or overwrite.
        file_content (str): UTF-8 text to write.

    :return: None
    """

    with file_path.open("w", encoding="utf-8") as file_handle:
        written = file_handle.write(file_content)
        check_status(file_path.name, lambda: written == len(file_content))


def check_status(file_name: str, predicate: Callable[[], bool]) -> None:
    """
    Log success or failure for a generation step.

    Args:
        file_name (str): Name of the artifact shown in log messages.
        predicate (Callable[[], bool]): Callable that returns True when the step succeeded.

    :return: None
    """

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

        global_builtins = {name: value for name, value in (builtins.__dict__).items()}

        # Set up Jinja environment
        env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), autoescape=False)
        env.globals.update(**global_builtins)

        generated_items = [
            GeneratedItem(
                template_path=TEMPLATES_DIR / "index_template.html",
                output_path=GENERATED_DIR / "index.html",
                env=env,
            ),
            GeneratedItem(
                template_path=TEMPLATES_DIR / "resume_template.html",
                output_path=GENERATED_DIR / "resume.html",
                env=env,
            ),
            GeneratedItem(
                template_path=TEMPLATES_DIR / "resume_pdf_template.html",
                output_path=GENERATED_DIR / "resume_pdf.html",
                env=env,
            ),
        ]

        pdf_output_paths = [
            GENERATED_DIR / "resume.pdf",
            GENERATED_DIR / f"{portfolio.first_name} {portfolio.last_name} Résumé.pdf",
        ]

        copy_resources = [
            CopyResource(
                src=TEMPLATES_DIR / "css",
                dst=SCRIPT_DIR / "../generated/css",
                glob="*.css",
                tag="CSS files",
            ),
            CopyResource(
                src=TEMPLATES_DIR / "fonts",
                dst=SCRIPT_DIR / "../generated/fonts",
                glob="*.ttf",
                tag="font files",
            ),
            CopyResource(
                src=TEMPLATES_DIR / "img",
                dst=SCRIPT_DIR / "../generated/img",
                glob="*.*",
                tag="Images",
            ),
            CopyResource(
                src=TEMPLATES_DIR / "img/favicon.ico",
                dst=SCRIPT_DIR / "../generated/img",
                glob=(TEMPLATES_DIR / "img/favicon.ico").name,
                tag="CSS files",
            ),
            CopyResource(
                src=TEMPLATES_DIR / "js",
                dst=SCRIPT_DIR / "../generated/js",
                glob="*.js",
                tag="JS files",
            ),
        ]

        for generated_item in generated_items:
            logger.info(f"Generating {generated_item.output_path.name} files...")

            # Render the template with the data
            generated_output = generated_item.env_template.render(
                portfolio=portfolio, extra_fields=extra_fields
            )

            # Write the output to an HTML file
            write_file(
                file_path=generated_item.output_path, file_content=generated_output
            )

        # Copy resources to generated dir
        for copy_resource in copy_resources:
            logger.info(f"Copying {copy_resource.tag}...")

            copy_resource.dst.mkdir(parents=True, exist_ok=True)

            copy_files(
                src=copy_resource.src, dest=copy_resource.dst, glob=copy_resource.glob
            )

        # Convert HTML to PDF with WeasyPrint
        for pdf_output_path in pdf_output_paths:
            logger.info(f"Generating {pdf_output_path.name} file...")

            HTML(
                filename=str(generated_items[-1].output_path), media_type="screen"
            ).write_pdf(str(pdf_output_path))

    except KeyboardInterrupt:
        logger.warning("portfolio generation interrupted!")
        sys.exit(0)


if __name__ == "__main__":
    main()
