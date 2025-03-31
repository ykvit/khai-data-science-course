import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

# ReportLab imports
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import inch
from reportlab.lib import colors

from .config import AppConfig # Assuming AppConfig holds relevant info

# Setup basic styles
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER))
styles.add(ParagraphStyle(name='LeftAligned', alignment=TA_LEFT, spaceAfter=6))
styles.add(ParagraphStyle(name='H1', alignment=TA_CENTER, fontSize=16, spaceAfter=12, spaceBefore=12))
styles.add(ParagraphStyle(name='H2', alignment=TA_LEFT, fontSize=14, spaceAfter=10, spaceBefore=10))


def _calculate_group_subject_averages(group_df: pd.DataFrame, config: AppConfig) -> Dict[str, float]:
    """Calculates the average score for each subject within the group."""
    averages = {}
    for col in config.subject_score_columns:
        if col in group_df.columns and pd.api.types.is_numeric_dtype(group_df[col]):
            # Calculate mean, ignoring NaN values
            avg = group_df[col].mean(skipna=True)
            averages[col.replace('(бали)', '').replace('(Бали)', '').strip()] = avg if pd.notna(avg) else 0.0 # Store cleaned name
    return averages

def _find_students_by_score_threshold(group_df: pd.DataFrame, config: AppConfig, threshold: int, condition: str) -> List[str]:
    """Finds students with any score meeting the condition (less than or greater than)."""
    students_found = set() # Use set to avoid duplicates
    for col in config.subject_score_columns:
        if col in group_df.columns and pd.api.types.is_numeric_dtype(group_df[col]):
            if condition == 'less':
                mask = group_df[col] < threshold
            elif condition == 'greater':
                mask = group_df[col] > threshold
            else:
                continue # Should not happen
            
            students_found.update(group_df.loc[mask, config.name_column].tolist())
            
    return sorted(list(students_found))


def generate_group_report_pdf(
    group_df: pd.DataFrame, 
    group_stats: Dict[str, Any], 
    group_id: str, 
    config: AppConfig, 
    output_dir: Path
) -> Optional[str]:
    """
    Generates a PDF report for a specific student group.

    Args:
        group_df: DataFrame filtered for the specific group.
        group_stats: Dictionary containing pre-calculated stats for the group.
        group_id: The ID of the group.
        config: Application configuration.
        output_dir: Directory to save the PDF report.

    Returns:
        The path to the saved PDF file, or None if generation failed.
    """
    logging.info(f"Generating PDF report for group: {group_id}")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_filename = output_dir / f"group_{group_id}_report.pdf"
    
    doc = SimpleDocTemplate(str(output_filename))
    story = []

    try:
        # --- Title ---
        story.append(Paragraph(f"Student Performance Report - Group {group_id}", styles['H1']))
        story.append(Spacer(1, 0.2*inch))

        # --- Basic Group Statistics (from Task 2) ---
        story.append(Paragraph("Group Summary:", styles['H2']))
        story.append(Paragraph(f"Total Students in Group: {group_stats.get('students_in_group', 'N/A')}", styles['LeftAligned']))
        story.append(Paragraph(f"Number of Scholarship Recipients: {group_stats.get('scholarship_recipients_in_group', 'N/A')}", styles['LeftAligned']))
        story.append(Paragraph(f"Average GPA in Group: {group_stats.get('average_gpa_in_group', 'N/A'):.2f}", styles['LeftAligned']))
        story.append(Spacer(1, 0.2*inch))

        # --- Average Score per Subject ---
        story.append(Paragraph("Average Score per Subject:", styles['H2']))
        subject_averages = _calculate_group_subject_averages(group_df, config)
        if subject_averages:
            avg_data = [['Subject', 'Average Score']]
            for subject, avg in subject_averages.items():
                avg_data.append([subject, f"{avg:.2f}"])
            
            table_avg = Table(avg_data, colWidths=[3*inch, 1.5*inch])
            table_avg.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(table_avg)
        else:
            story.append(Paragraph("No subject average data available.", styles['LeftAligned']))
        story.append(Spacer(1, 0.2*inch))

        # --- Students with Scores Below 65 ---
        story.append(Paragraph("Students with Scores Below 65 (in any subject):", styles['H2']))
        low_performers = _find_students_by_score_threshold(group_df, config, 65, 'less')
        if low_performers:
            for student in low_performers:
                story.append(Paragraph(f"- {student}", styles['LeftAligned']))
        else:
            story.append(Paragraph("No students found with scores below 65.", styles['LeftAligned']))
        story.append(Spacer(1, 0.2*inch))

        # --- Students with Scores Above 95 ---
        story.append(Paragraph("Students with Scores Above 95 (in any subject):", styles['H2']))
        high_performers = _find_students_by_score_threshold(group_df, config, 95, 'greater')
        if high_performers:
            for student in high_performers:
                 story.append(Paragraph(f"- {student}", styles['LeftAligned']))
        else:
            story.append(Paragraph("No students found with scores above 95.", styles['LeftAligned']))

        # --- Build the PDF ---
        doc.build(story)
        logging.info(f"PDF report saved to {output_filename}")
        return str(output_filename)

    except Exception as e:
        logging.error(f"Failed to generate PDF report for group {group_id}: {e}", exc_info=True)
        return None