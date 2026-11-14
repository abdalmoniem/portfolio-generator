# ruff: noqa: UP007, UP045, RUF100

"""
Run this script to watch for changes to the portfolio.json file and regenerate
the portfolio and resume pages when it changes.

Example usage:

    python watch.py

"""

import logging
import sys
from pathlib import Path
from subprocess import run
from sys import executable as python_executable
from typing import Optional

from constants import LOG_LEVEL
from livereload.server import Server as LiveReloadServer
from logging_setup import configure_logging

PORT = 8000
HOST = "localhost"
SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = SCRIPT_DIR / "../templates"
SCRIPT_TO_RUN = SCRIPT_DIR / "generate_portfolio.py"

watched_paths = [
    SCRIPT_DIR,
    TEMPLATES_DIR / "js",
    TEMPLATES_DIR / "css",
    TEMPLATES_DIR / "img",
    TEMPLATES_DIR / "fonts",
    TEMPLATES_DIR / "favicon.ico",
    TEMPLATES_DIR / "portfolio.json",
    TEMPLATES_DIR / "index_template.html",
    TEMPLATES_DIR / "resume_template.html",
    TEMPLATES_DIR / "resume_pdf_template.html",
]


configure_logging()
logger = logging.getLogger(__name__)


class Server(LiveReloadServer):
    """LiveReload server that logs through root Rich handlers only."""

    def _setup_logging(self) -> None:
        """
        Set library log levels without adding LiveReload's Tornado StreamHandler.

        The default implementation attaches a second handler and breaks Rich formatting.

        :return: None
        """

        logging.getLogger("livereload").setLevel(LOG_LEVEL)
        logging.getLogger("tornado").setLevel(LOG_LEVEL)


def run_script(changed_path: Optional[Path] | Optional[list[str]] = None) -> None:  # noqa: PYI016, UP045
    """
    Executes a specified script and handles changes to files.

    If a change is detected in the specified `changed_file`, the function
    prints a message indicating the detected change. It then runs the script
    defined by `SCRIPT_TO_RUN` using the Python interpreter. After the script
    execution, a message is printed to confirm the script has finished.

    If the `changed_file` is an HTML file (i.e., its name ends with ".html"),
    the function assumes it corresponds to a served file and prints messages
    indicating the need to reload the served file and the browser.

    Args:
        changed_file (Optional[Path] | Optional[list[str]]): The path to the
            changed file or a list of changed file paths. If None, no specific
            file change is detected.
    """

    try:
        if isinstance(changed_path, list):
            for file in changed_path:
                logger.info(f"Detected change in {file}!")
        elif isinstance(changed_path, Path):
            logger.info(f"Detected change in {changed_path}!")

        logger.info(f"Running {SCRIPT_TO_RUN}...")
        run([python_executable, SCRIPT_TO_RUN], check=True)
        logger.info(f"Script {SCRIPT_TO_RUN} finished!")

        if changed_path:
            if isinstance(changed_path, Path) and changed_path.suffix == ".html":
                new_name = changed_path.name.replace("_template", "")
                served_file = changed_path.with_name(new_name)

                logger.info(f"Reloading {served_file}...")
                logger.info("Reloading browser...")

            elif isinstance(changed_path, list):
                for path in changed_path:
                    path = Path(path)
                    if path.suffix == ".html":
                        new_name = path.name.replace("_template", "")
                        served_file = path.with_name(new_name)

                        logger.info(f"Reloading {served_file}...")
                        logger.info("Reloading browser...")
    except KeyboardInterrupt:
        logger.warning(f"{SCRIPT_TO_RUN} execution interrupted!")
        sys.exit(0)


def main() -> None:
    """
    Watches the specified files for changes and runs the specified script
    when changes are detected. Serves the current directory using a LiveReload
    server.

    This function runs the specified script once when it is first called, and
    also sets up a LiveReload server to watch for changes in the specified
    files. If any of the watched files are changed, the script is executed
    again.

    The LiveReload server is started after the script has finished running
    initially. The server serves the current directory, making it accessible
    at `http://<HOST>:<PORT>`. The server is configured to use LiveReload,
    which allows browsers to automatically reload the page when any of the
    watched files change.
    """

    run_script()

    watched_dirs = filter(lambda path: path.is_dir(), watched_paths)
    watched_files = filter(lambda path: path.is_file(), watched_paths)

    server = Server()

    # Watch individual files
    for file in watched_files:
        server.watch(
            filepath=str(file), func=lambda changed_file=file: run_script(changed_file)
        )

    # Watch directories recursively
    for dir in watched_dirs:
        server.watch(
            filepath=str(dir / "**/*"),
            func=lambda changed_file=dir: run_script(changed_file),
        )

    server.serve(root=SCRIPT_DIR / "../generated", port=PORT, host=HOST)


if __name__ == "__main__":
    main()
