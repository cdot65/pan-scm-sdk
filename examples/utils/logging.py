#!/usr/bin/env python3
"""Standardized logging utilities for Strata Cloud Manager SDK examples.

This module provides enhanced logging capabilities for SDK examples using
the Rich library for improved terminal formatting and visual output.

Features:
- Color-coded console output
- Visual section headers and progress tracking
- Standardized formatting for info, success, warning, and error messages
- Table generation for structured data display
- Progress tracking with spinners for long-running operations

Usage:
    from examples.utils.logging import SDKLogger

    # Initialize the logger
    logger = SDKLogger("example_name")

    # Use the logger methods
    logger.section("SECTION TITLE")
    logger.operation_start("Starting operation")
    logger.info("Informational message")
    logger.success("Operation completed successfully")
    logger.warning("Warning message")
    logger.error("Error message", error_object)

    # Create progress tracking
    with logger.create_progress() as progress:
        task = progress.add_task("Processing items...", total=100)
        for i in range(100):
            # Do work
            progress.update(task, advance=1)

    # Create tables for displaying structured data
    table = logger.create_table("Table Title", ["Column 1", "Column 2"])
    table.add_row("Value 1", "Value 2")
    logger.console.print(table)
"""

import logging
from typing import List, Optional, Any

# Rich imports
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.table import Table
    from rich.theme import Theme

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    from functools import partial

    class DummyConsole:
        """Fallback console when Rich is not available."""

        def print(self, *args, **kwargs):
            """Print a message without Rich formatting.
            
            Args:
                *args: Positional arguments to print
                **kwargs: Keyword arguments (ignored)
            """
            # Extract the text content without Rich formatting
            message = str(args[0])
            for prefix in ["[info]", "[success]", "[warning]", "[error]", "[section]"]:
                message = message.replace(prefix, "")
            for suffix in ["[/info]", "[/success]", "[/warning]", "[/error]", "[/section]"]:
                message = message.replace(suffix, "")
            print(message)

    class DummyPanel:
        """Fallback Panel when Rich is not available."""

        @staticmethod
        def __call__(*args, **kwargs):
            """Return the first argument without formatting.
            
            Args:
                *args: Positional arguments
                **kwargs: Keyword arguments (ignored)
                
            Returns:
                The first positional argument
            """
            return args[0]

    class DummyProgressContext:
        """Dummy context manager for progress tracking when Rich is not available."""

        def __init__(self, *args, **kwargs):
            """Initialize the dummy progress context.
            
            Args:
                *args: Positional arguments (ignored)
                **kwargs: Keyword arguments (ignored)
            """
            pass

        def __enter__(self):
            """Enter the context manager.
            
            Returns:
                Self reference for context management
            """
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            """Exit the context manager.
            
            Args:
                exc_type: Exception type (if any)
                exc_val: Exception value (if any)
                exc_tb: Exception traceback (if any)
            """
            pass

        def add_task(self, description, total=None):
            """Add a task to the progress tracker.
            
            Args:
                description: Description of the task
                total: Total steps for the task (optional)
                
            Returns:
                A dummy task ID string
            """
            print(f"Task started: {description}")
            return "task_id"

        def update(self, task_id, advance=None):
            """Update task progress.
            
            Args:
                task_id: The task identifier
                advance: How much to advance the progress (optional)
            """
            pass

    class DummyTable:
        """Fallback Table when Rich is not available."""

        def __init__(self, title=None):
            """Initialize the dummy table.
            
            Args:
                title: Optional title for the table
            """
            self.title = title
            self.columns = []
            self.rows = []
            print(f"Table: {title if title else 'Unnamed'}")

        def add_column(self, column):
            """Add a column to the table.
            
            Args:
                column: Column name to add
            """
            self.columns.append(column)

        def add_row(self, *args):
            """Add a row to the table.
            
            Args:
                *args: Cell values for the row
            """
            self.rows.append(args)
            print(" | ".join(str(a) for a in args))

    # Create dummy versions of Rich objects
    Console = DummyConsole
    Panel = DummyPanel()
    Progress = partial(DummyProgressContext)
    Table = DummyTable
    Theme = dict

# Define ANSI color codes for fallback (when Rich is not available)
COLORS = {
    "RESET": "\033[0m",
    "BOLD": "\033[1m",
    "RED": "\033[31m",
    "GREEN": "\033[32m",
    "YELLOW": "\033[33m",
    "BLUE": "\033[34m",
    "MAGENTA": "\033[35m",
    "CYAN": "\033[36m",
    "WHITE": "\033[37m",
    "BRIGHT_GREEN": "\033[92m",
    "BRIGHT_YELLOW": "\033[93m",
    "BRIGHT_BLUE": "\033[94m",
    "BRIGHT_MAGENTA": "\033[95m",
    "BRIGHT_CYAN": "\033[96m",
}

# Custom theme for consistent colors when Rich is available
RICH_THEME = {
    "info": "bright_blue",
    "success": "bright_green",
    "warning": "bright_yellow",
    "error": "bright_red",
    "section": "bright_cyan bold",
    "progress.description": "bright_blue",
    "progress.percentage": "bright_green",
    "progress.elapsed": "bright_cyan",
}


class SDKLogger:
    """Unified logger for SDK example scripts with enhanced formatting."""

    def __init__(self, name: str, log_level: str = "INFO"):
        """Initialize the SDK Logger.

        Args:
            name: The logger name (usually the script or module name)
            log_level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        # Set up Python standard logging
        self.logger = logging.getLogger(name)
        numeric_level = getattr(logging, log_level.upper(), None)
        if not isinstance(numeric_level, int):
            numeric_level = logging.INFO

        # Configure basic logging if not already configured
        if not self.logger.handlers:
            log_format = "%(asctime)s %(levelname)-8s %(message)s"
            date_format = "%Y-%m-%d %H:%M:%S"
            logging.basicConfig(level=numeric_level, format=log_format, datefmt=date_format)
            self.logger.setLevel(numeric_level)

        # Set up Rich console if available
        if RICH_AVAILABLE:
            self.console = Console(theme=Theme(RICH_THEME))
            self.is_rich = True
        else:
            self.console = Console()
            self.is_rich = False
            print(
                f"{COLORS['YELLOW']}WARNING: Rich library not installed. Basic formatting will be used.{COLORS['RESET']}"
            )
            print(
                f"{COLORS['YELLOW']}Install Rich for enhanced output: pip install rich{COLORS['RESET']}"
            )

    def section(self, title: str) -> None:
        """Display a section header with visual separation.

        Args:
            title: The section title to display
        """
        self.logger.info(f"SECTION: {title}")

        if self.is_rich:
            self.console.print()
            self.console.print(
                Panel(f"[section]{title.upper()}[/section]", expand=False, border_style="cyan")
            )
        else:
            separator = "=" * 80
            print("")
            print(f"{COLORS['BOLD']}{COLORS['BRIGHT_CYAN']}{separator}{COLORS['RESET']}")
            print(f"{COLORS['BOLD']}{COLORS['BRIGHT_CYAN']}   {title.upper()}{COLORS['RESET']}")
            print(f"{COLORS['BOLD']}{COLORS['BRIGHT_CYAN']}{separator}{COLORS['RESET']}")

    def operation_start(self, operation: str) -> None:
        """Log the start of an operation with clear visual indicator.

        Args:
            operation: The name of the operation being started
        """
        self.logger.info(f"START: {operation}")

        if self.is_rich:
            self.console.print(f"[info]▶ STARTING:[/info] {operation}")
        else:
            print(f"{COLORS['BRIGHT_BLUE']}▶ STARTING: {operation}{COLORS['RESET']}")

    def operation_complete(self, operation: str, details: Optional[str] = None) -> None:
        """Log the completion of an operation with success status.

        Args:
            operation: The name of the completed operation
            details: Optional details about the completion
        """
        if details:
            self.logger.info(f"COMPLETE: {operation} - {details}")
            if self.is_rich:
                self.console.print(f"[success]✓ COMPLETED:[/success] {operation} - {details}")
            else:
                print(
                    f"{COLORS['BRIGHT_GREEN']}✓ COMPLETED: {operation} - {details}{COLORS['RESET']}"
                )
        else:
            self.logger.info(f"COMPLETE: {operation}")
            if self.is_rich:
                self.console.print(f"[success]✓ COMPLETED:[/success] {operation}")
            else:
                print(f"{COLORS['BRIGHT_GREEN']}✓ COMPLETED: {operation}{COLORS['RESET']}")

    def warning(self, message: str) -> None:
        """Log a warning message with clear visual indicator.

        Args:
            message: The warning message to log
        """
        self.logger.warning(message)

        if self.is_rich:
            self.console.print(f"[warning]⚠ WARNING:[/warning] {message}")
        else:
            print(f"{COLORS['BRIGHT_YELLOW']}⚠ WARNING: {message}{COLORS['RESET']}")

    def error(self, message: str, error: Optional[Any] = None) -> None:
        """Log an error message with clear visual indicator.

        Args:
            message: The error message to log
            error: Optional exception or error object with additional details
        """
        if error:
            self.logger.error(f"{message} - {str(error)}")
            if self.is_rich:
                self.console.print(f"[error]✘ ERROR:[/error] {message} - {str(error)}")
            else:
                print(f"{COLORS['RED']}✘ ERROR: {message} - {str(error)}{COLORS['RESET']}")
        else:
            self.logger.error(message)
            if self.is_rich:
                self.console.print(f"[error]✘ ERROR:[/error] {message}")
            else:
                print(f"{COLORS['RED']}✘ ERROR: {message}{COLORS['RESET']}")

    def info(self, message: str) -> None:
        """Log an informational message.

        Args:
            message: The informational message to log
        """
        self.logger.info(message)

        if self.is_rich:
            self.console.print(f"[info]{message}[/info]")
        else:
            print(f"{COLORS['BRIGHT_BLUE']}{message}{COLORS['RESET']}")

    def success(self, message: str) -> None:
        """Log a success message.

        Args:
            message: The success message to log
        """
        self.logger.info(message)

        if self.is_rich:
            self.console.print(f"[success]✓ {message}[/success]")
        else:
            print(f"{COLORS['BRIGHT_GREEN']}✓ {message}{COLORS['RESET']}")

    def create_progress(self, description: str = "Processing") -> Progress:
        """Create a Rich progress bar for operations.

        Args:
            description: Default description for the progress bar

        Returns:
            A Progress object for tracking operations
        """
        if self.is_rich:
            return Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
                console=self.console,
            )
        else:
            return Progress()

    def create_table(self, title: str, columns: List[str]) -> Table:
        """Create a Rich table for displaying structured data.

        Args:
            title: The table title
            columns: List of column names

        Returns:
            A Table object for displaying structured data
        """
        if self.is_rich:
            table = Table(title=title)
            for column in columns:
                table.add_column(column)
            return table
        else:
            table = Table(title=title)
            for column in columns:
                table.add_column(column)
            return table
