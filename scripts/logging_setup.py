# ruff: noqa: UP007, UP045

"""
Configure Rich logging for portfolio generator scripts.

WeasyPrint and other libraries emit long log lines; this module keeps timestamp
and level on every wrapped segment when using RichHandlerEveryLine.
"""

import copy
import logging
import shutil
import textwrap
from collections.abc import Iterable
from datetime import datetime
from typing import Optional, Union, cast

from constants import LOG_LEVEL
from rich._log_render import FormatTimeCallable, LogRender
from rich.console import Console, ConsoleRenderable, RenderableType
from rich.containers import Renderables
from rich.logging import RichHandler
from rich.table import Table
from rich.text import Text, TextType

LOG_DATEFMT = "[%a, %d/%b/%Y - %I:%M:%S %p]"


class LogRenderEveryLine(LogRender):
    """Rich log layout that does not fold long messages inside one row."""

    def __call__(
        self,
        console: Console,
        renderables: Iterable[ConsoleRenderable],
        log_time: Optional[datetime] = None,
        time_format: Optional[Union[str, FormatTimeCallable]] = None,
        level: TextType = "",
        path: Optional[str] = None,
        line_no: Optional[int] = None,
        link_path: Optional[str] = None,
    ) -> Table:
        """
        Build a single Rich log table row without folding the message column.

        Args:
            console (Console): Rich console instance.
            renderables (Iterable[ConsoleRenderable]): Message renderables to display.
            log_time (Optional[datetime]): Timestamp for the log entry.
            time_format (Optional[Union[str, FormatTimeCallable]]): Time format string or callable.
            level (TextType): Styled level text.
            path (Optional[str]): Source file path for the log call.
            line_no (Optional[int]): Source line number for the log call.
            link_path (Optional[str]): Path used for terminal file links.

        Returns:
            Table: Rich table grid row for console.print.
        """

        row: list[RenderableType] = []
        output = Table.grid(padding=(0, 1))
        output.expand = True

        if self.show_time:
            output.add_column(style="log.time")

        if self.show_level:
            output.add_column(
                style="log.level", width=self.level_width, justify="center"
            )

        output.add_column(ratio=1, style="log.message", overflow="ignore")

        if self.show_path and path:
            output.add_column(style="log.path")

        if self.show_time:
            log_time = log_time or console.get_datetime()
            time_format = time_format or self.time_format

            if isinstance(time_format, str):
                log_time_display = Text(log_time.strftime(time_format))
            else:
                log_time_display = cast(FormatTimeCallable, time_format)(log_time)

            row.append(log_time_display)

            self._last_time = log_time_display

        if self.show_level:
            row.append(level)

        row.append(Renderables(renderables))

        if self.show_path and path:
            path_text = Text()
            path_text.append(
                path, style=f"link file://{link_path}" if link_path else ""
            )

            if line_no:
                path_text.append(":")
                path_text.append(
                    f"{line_no}",
                    style=f"link file://{link_path}#{line_no}" if link_path else "",
                )

            row.append(path_text)

        output.add_row(*row)

        return output


class RichHandlerEveryLine(RichHandler):
    """RichHandler that emits one full log row per wrapped segment of a message."""

    def __init__(self, *args, **kwargs) -> None:
        """
        Initialize the handler and attach LogRenderEveryLine for layout.

        Args:
            *args: Forwarded to RichHandler.
            **kwargs: Forwarded to RichHandler.
        """

        super().__init__(*args, **kwargs)

        self._log_render = LogRenderEveryLine(
            show_time=self._log_render.show_time,
            show_level=self._log_render.show_level,
            show_path=self._log_render.show_path,
            time_format=self._log_render.time_format,
            omit_repeated_times=False,
            level_width=7,  # self._log_render.level_width,
        )

    def _wrap_width(self) -> int:
        """
        Estimate how many characters fit in Rich's message column.

        Returns:
            int: Maximum segment width before splitting into another log row.
        """

        columns = max(shutil.get_terminal_size(fallback=(120, 24)).columns, 80)

        return max(columns - 48, 40)

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a log record, splitting long messages so each line keeps time and level.

        Args:
            record (logging.LogRecord): Log record from the logging system.
        """

        if (
            self.rich_tracebacks
            and record.exc_info
            and record.exc_info != (None, None, None)
        ):
            super().emit(record)

            return

        parts: list[str] = []
        message = record.getMessage()

        for segment in message.splitlines() or [""]:
            segment = segment.strip()

            if not segment:
                continue

            wrapped = textwrap.wrap(
                segment,
                width=self._wrap_width(),
                break_long_words=False,
                break_on_hyphens=False,
            )

            parts.extend(wrapped if wrapped else [segment])

        if len(parts) <= 1:
            super().emit(record)

            return

        for part in parts:
            sub = copy.copy(record)
            sub.msg = part
            sub.args = ()

            super().emit(sub)


def configure_logging(level: int = LOG_LEVEL) -> None:
    """
    Configure root logging with RichHandlerEveryLine for script output.

    Args:
        level (int, optional): Root log level. Defaults to LOG_LEVEL.

    :return: None
    """

    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt=LOG_DATEFMT,
        handlers=[
            RichHandlerEveryLine(
                rich_tracebacks=True,
                log_time_format=LOG_DATEFMT,
                omit_repeated_times=False,
            )
        ],
        force=True,
    )

    logging.getLogger("asyncio").setLevel(logging.WARNING)
