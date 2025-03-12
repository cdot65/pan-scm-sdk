#!/usr/bin/env python3
"""
Standardized reporting utilities for Strata Cloud Manager SDK examples.

This module provides standardized reporting functionality for SDK examples,
with support for both CSV and PDF report generation.

Features:
- CSV report generation with summary data
- PDF report generation with tables and charts
- Consistent reporting format and styling
- Error handling and fallback mechanisms
- Progress tracking for report generation

Usage:
    from examples.utils.report import ReportGenerator
    from examples.utils.logging import SDKLogger

    # Initialize the logger
    logger = SDKLogger("example_name")

    # Create the report generator
    report_gen = ReportGenerator("object_name", logger)

    # Generate CSV report
    headers = ["ID", "Name", "Type", "Value"]
    data = [
        ["123", "object1", "IPv4", "10.0.0.1/32"],
        ["456", "object2", "FQDN", "example.com"]
    ]
    summary = {
        "Total Objects": 2,
        "Generation Time": "2023-01-01 12:00:00"
    }

    csv_file = report_gen.generate_csv(headers, data, summary)
    pdf_file = report_gen.generate_pdf("Object Report", headers, data, summary)
"""

import csv
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

# ReportLab imports
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate,
        Table,
        TableStyle,
        Paragraph,
        Spacer,
    )

    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class ReportGenerator:
    """Generate standardized reports in both CSV and PDF formats."""

    def __init__(self, report_name: str, logger: Any):
        """
        Initialize the report generator.

        Args:
            report_name: Base name for the report files (without extension)
            logger: The SDKLogger instance for logging
        """
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.report_name = report_name
        self.csv_filename = f"{report_name}_report_{self.timestamp}.csv"
        self.pdf_filename = f"{report_name}_report_{self.timestamp}.pdf"
        self.logger = logger

        # Check if ReportLab is available
        if not REPORTLAB_AVAILABLE:
            self.logger.warning("ReportLab not installed. PDF generation will not be available.")
            self.logger.info("Install ReportLab for PDF support: pip install reportlab")

    def generate_csv(
        self,
        headers: List[str],
        data: List[List[Any]],
        summary_data: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        Generate CSV report with headers, data rows, and optional summary.

        Args:
            headers: List of column headers
            data: List of data rows (each row is a list of values)
            summary_data: Optional dictionary of summary information to append

        Returns:
            str: Path to the generated CSV file, or None if generation failed
        """
        try:
            with open(self.csv_filename, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                writer.writerows(data)

                # Add summary section
                if summary_data:
                    writer.writerow([])
                    writer.writerow(["SUMMARY"])
                    for key, value in summary_data.items():
                        writer.writerow([key, value])

            self.logger.success(f"CSV report generated: {self.csv_filename}")
            return self.csv_filename

        except Exception as e:
            self.logger.error("Failed to write CSV report", e)

            # Try fallback location
            try:
                fallback_file = f"{self.report_name}_{self.timestamp}.csv"
                fallback_path = Path.home() / fallback_file

                self.logger.info(f"Attempting to write to fallback location: {fallback_path}")

                with open(fallback_path, "w", newline="") as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(headers)
                    writer.writerows(data)

                    # Add summary section
                    if summary_data:
                        writer.writerow([])
                        writer.writerow(["SUMMARY"])
                        for key, value in summary_data.items():
                            writer.writerow([key, value])

                self.logger.success(f"CSV report generated at fallback location: {fallback_path}")
                return str(fallback_path)

            except Exception as fallback_error:
                self.logger.error("Failed to write to fallback location", fallback_error)
                return None

    def generate_pdf(
        self,
        title: str,
        headers: List[str],
        data: List[List[Any]],
        summary_data: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        Generate PDF report with headers, data rows, and optional summary.

        Args:
            title: The report title
            headers: List of column headers
            data: List of data rows (each row is a list of values)
            summary_data: Optional dictionary of summary information to append

        Returns:
            str: Path to the generated PDF file, or None if generation failed
        """
        if not REPORTLAB_AVAILABLE:
            self.logger.error("Cannot generate PDF: ReportLab library not installed")
            self.logger.info("Install ReportLab for PDF support: pip install reportlab")
            return None

        try:
            # Determine orientation based on number of columns
            pagesize = landscape(letter) if len(headers) > 5 else letter

            # Create the PDF document
            doc = SimpleDocTemplate(
                self.pdf_filename,
                pagesize=pagesize,
                rightMargin=0.5 * inch,
                leftMargin=0.5 * inch,
                topMargin=0.5 * inch,
                bottomMargin=0.5 * inch,
            )

            # List to hold all the flowables
            elements = []

            # Define styles
            styles = getSampleStyleSheet()
            title_style = styles["Title"]
            heading_style = styles["Heading2"]
            normal_style = styles["Normal"]

            # Create a custom timestamp style
            timestamp_style = ParagraphStyle(
                "Timestamp", parent=styles["Normal"], fontSize=8, textColor=colors.gray
            )

            # Add title
            elements.append(Paragraph(title, title_style))
            elements.append(Spacer(1, 0.1 * inch))

            # Add timestamp
            timestamp_text = f"Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            elements.append(Paragraph(timestamp_text, timestamp_style))
            elements.append(Spacer(1, 0.2 * inch))

            # Truncate data if there are too many rows to fit in the PDF
            row_limit = 500
            if len(data) > row_limit:
                truncated_data = data[:row_limit]
                self.logger.warning(
                    f"Data truncated for PDF report: showing {row_limit} of {len(data)} rows"
                )

                # Add truncation notice
                truncate_notice = (
                    f"Note: This report shows {row_limit} of {len(data)} total records. "
                    f"Please see the CSV report for the complete dataset."
                )
                elements.append(
                    Paragraph(
                        truncate_notice,
                        ParagraphStyle("Notice", parent=normal_style, textColor=colors.red),
                    )
                )
                elements.append(Spacer(1, 0.2 * inch))
            else:
                truncated_data = data

            # Add main data table
            table_data = [headers] + truncated_data

            # Calculate column widths based on content
            col_widths = self._calculate_column_widths(headers, truncated_data, pagesize)

            # Create the table
            table = Table(table_data, colWidths=col_widths)

            # Apply table styles
            table.setStyle(
                TableStyle(
                    [
                        # Header row styling
                        ("BACKGROUND", (0, 0), (-1, 0), colors.skyblue),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                        # Data rows styling - alternating colors
                        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                        (
                            "BACKGROUND",
                            (0, 2),
                            (-1, -1),
                            colors.lightgrey,
                        ),  # Start with row 2 (0-indexed)
                        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                        *[
                            ("BACKGROUND", (0, i), (-1, i), colors.whitesmoke)
                            for i in range(2, len(table_data), 2)
                        ],
                        # All cells styling
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 1), (-1, -1), 8),
                        ("TOPPADDING", (0, 1), (-1, -1), 4),
                        ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
                        # Grid styling
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        ("BOX", (0, 0), (-1, -1), 1, colors.black),
                        ("BOX", (0, 0), (-1, 0), 1, colors.black),
                    ]
                )
            )

            elements.append(table)
            elements.append(Spacer(1, 0.3 * inch))

            # Add summary section if provided
            if summary_data:
                elements.append(Paragraph("Summary", heading_style))
                elements.append(Spacer(1, 0.1 * inch))

                # Create summary data for table
                summary_table_data = [[k, str(v)] for k, v in summary_data.items()]

                # Create summary table
                summary_table = Table(summary_table_data, colWidths=[2 * inch, 4 * inch])
                summary_table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (0, -1), colors.lightblue),
                            ("TEXTCOLOR", (0, 0), (0, -1), colors.black),
                            ("ALIGN", (0, 0), (0, -1), "LEFT"),
                            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                            ("FONTSIZE", (0, 0), (1, -1), 9),
                            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                            ("BOX", (0, 0), (-1, -1), 1, colors.black),
                        ]
                    )
                )

                elements.append(summary_table)

            # Build PDF
            doc.build(elements)
            self.logger.success(f"PDF report generated: {self.pdf_filename}")
            return self.pdf_filename

        except Exception as e:
            self.logger.error("Failed to generate PDF report", e)

            # Try fallback location
            try:
                fallback_file = f"{self.report_name}_{self.timestamp}.pdf"
                fallback_path = Path.home() / fallback_file

                self.logger.info(f"Attempting to write PDF to fallback location: {fallback_path}")

                # Create a new document at the fallback location
                doc = SimpleDocTemplate(
                    str(fallback_path),
                    pagesize=letter,
                    rightMargin=0.5 * inch,
                    leftMargin=0.5 * inch,
                    topMargin=0.5 * inch,
                    bottomMargin=0.5 * inch,
                )

                # Simplified content for fallback
                elements = []

                # Add title with error note
                styles = getSampleStyleSheet()
                elements.append(Paragraph(f"{title} (Fallback)", styles["Title"]))
                elements.append(Spacer(1, 0.2 * inch))
                elements.append(
                    Paragraph(
                        "Note: This is a simplified fallback report due to an error generating the full report.",
                        ParagraphStyle("Notice", parent=styles["Normal"], textColor=colors.red),
                    )
                )
                elements.append(Spacer(1, 0.2 * inch))

                # Add simplified table
                truncated_data = data[: min(50, len(data))]  # Limit to 50 rows for fallback
                table_data = [headers] + truncated_data

                table = Table(table_data)
                table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), colors.skyblue),
                            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        ]
                    )
                )

                elements.append(table)

                # Build fallback PDF
                doc.build(elements)

                self.logger.success(
                    f"Simplified PDF report generated at fallback location: {fallback_path}"
                )
                return str(fallback_path)

            except Exception as fallback_error:
                self.logger.error("Failed to write fallback PDF", fallback_error)
                return None

    def _calculate_column_widths(
        self, headers: List[str], data: List[List[Any]], pagesize: Tuple[float, float]
    ) -> List[float]:
        """
        Calculate appropriate column widths based on content and page size.

        Args:
            headers: List of column headers
            data: List of data rows
            pagesize: ReportLab pagesize tuple (width, height)

        Returns:
            List of column widths in points
        """
        # Get page width (accounting for margins)
        page_width = pagesize[0] - 1 * inch  # Subtract margins

        # Calculate average content length for each column
        col_lengths = []
        for i in range(len(headers)):
            # Check header length
            header_len = len(str(headers[i]))

            # Check data lengths for this column
            data_lengths = [
                len(str(row[i])) if i < len(row) else 0 for row in data[:100]
            ]  # Sample first 100 rows

            # Get max length for this column
            if data_lengths:
                max_data_len = max(data_lengths)
                col_lengths.append(max(header_len, max_data_len))
            else:
                col_lengths.append(header_len)

        # Calculate proportional widths based on content length
        total_chars = sum(col_lengths)
        if total_chars == 0:
            # Equal distribution if no content
            return [page_width / len(headers)] * len(headers)

        # Minimum width per column (for very short columns)
        min_width = 0.5 * inch

        # Calculate proportional widths, but ensure each column gets at least the minimum width
        widths = []
        for length in col_lengths:
            # Calculate proportional width
            prop_width = (length / total_chars) * page_width

            # Ensure minimum width
            widths.append(max(prop_width, min_width))

        # Scale widths to fit page width
        total_width = sum(widths)
        if total_width > page_width:
            scale_factor = page_width / total_width
            widths = [width * scale_factor for width in widths]

        return widths
