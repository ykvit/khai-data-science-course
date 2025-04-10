import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

# --- ReportLab Imports ---
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY # TA_JUSTIFY може бути корисним
from reportlab.lib.units import inch
from reportlab.lib import colors
# --- New imports for Fonts ---
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from .config import AppConfig

try:
    font_path = Path(__file__).parent / "assets" / "fonts" / "OpenSans-VariableFont_wdth,wght.ttf" 
    if font_path.exists():
        pdfmetrics.registerFont(TTFont('OpenSans', str(font_path))) 
        FONT_NAME = 'OpenSans' 
        logging.info(f"Registered TTF font '{FONT_NAME}' from: {font_path}")
    else:
        logging.warning(f"Font file not found at {font_path}. Using default font (may cause issues with Cyrillic).")
        FONT_NAME = 'Helvetica'
        
except Exception as font_err:
    logging.error(f"Failed to register font: {font_err}", exc_info=True)
    FONT_NAME = 'Helvetica' 

# --- Setup basic styles using the registered font ---
styles = getSampleStyleSheet()

styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER, fontName=FONT_NAME))
styles.add(ParagraphStyle(name='LeftAligned', alignment=TA_LEFT, spaceAfter=6, fontName=FONT_NAME, leading=14)) 
styles.add(ParagraphStyle(name='H1', alignment=TA_CENTER, fontSize=16, spaceAfter=12, spaceBefore=12, fontName=FONT_NAME))
styles.add(ParagraphStyle(name='H2', alignment=TA_LEFT, fontSize=14, spaceAfter=10, spaceBefore=10, fontName=FONT_NAME))
styles.add(ParagraphStyle(name='TableHeader', alignment=TA_CENTER, fontName=FONT_NAME, fontSize=10))
styles.add(ParagraphStyle(name='TableCell', alignment=TA_CENTER, fontName=FONT_NAME, fontSize=9))

def _calculate_group_subject_averages(group_df: pd.DataFrame, config: AppConfig) -> Dict[str, float]:
    """Calculates the average score for each subject within the group."""
    averages = {}
    for col in config.subject_score_columns:
        if col in group_df.columns and pd.api.types.is_numeric_dtype(group_df[col]):
            avg = group_df[col].mean(skipna=True)
            subject_name = col.replace('(бали)', '').replace('(Бали)', '').strip()
            averages[subject_name] = avg if pd.notna(avg) else 0.0
    return averages

def _find_students_by_score_threshold(group_df: pd.DataFrame, config: AppConfig, threshold: int, condition: str) -> List[str]:
    """Finds students with any score meeting the condition (less than or greater than)."""
    students_found = set()
    for col in config.subject_score_columns:
        if col in group_df.columns and pd.api.types.is_numeric_dtype(group_df[col]):
            if condition == 'less':
                mask = group_df[col] < threshold
            elif condition == 'greater':
                mask = group_df[col] > threshold
            else:
                continue
            
            students_found.update(group_df.loc[mask, config.name_column].tolist())
            
    return sorted(list(students_found))


# --- The main function of PDF generation ---
def generate_group_report_pdf(
    group_df: pd.DataFrame, 
    group_stats: Dict[str, Any], 
    group_id: str, 
    config: AppConfig, 
    output_dir: Path
) -> Optional[str]:
    """
    Generates a PDF report for a specific student group, ensuring Cyrillic support.

    Args:
        group_df: DataFrame filtered for the specific group.
        group_stats: Dictionary containing pre-calculated stats for the group.
        group_id: The ID of the group.
        config: Application configuration.
        output_dir: Directory to save the PDF report.

    Returns:
        The path to the saved PDF file, or None if generation failed.
    """
    logging.info(f"Generating PDF report for group: {group_id} using font '{FONT_NAME}'")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_filename = output_dir / f"group_{group_id}_report.pdf"
    
    doc = SimpleDocTemplate(str(output_filename))
    story = [] 

    try:
        # --- Title ---
        story.append(Paragraph(f"Звіт Успішності Студентів - Група {group_id}", styles['H1']))
        story.append(Spacer(1, 0.2*inch))

        # --- Basic Group Statistics ---
        story.append(Paragraph("Загальна Інформація по Групі:", styles['H2']))
        story.append(Paragraph(f"Загальна кількість студентів: {group_stats.get('students_in_group', 'N/A')}", styles['LeftAligned']))
        story.append(Paragraph(f"Кількість стипендіатів: {group_stats.get('scholarship_recipients_in_group', 'N/A')}", styles['LeftAligned']))
        avg_gpa = group_stats.get('average_gpa_in_group')
        avg_gpa_str = f"{avg_gpa:.2f}" if isinstance(avg_gpa, (int, float)) else 'N/A'
        story.append(Paragraph(f"Середній бал (GPA) по групі: {avg_gpa_str}", styles['LeftAligned']))
        story.append(Spacer(1, 0.2*inch))

        story.append(Paragraph("Середній Бал по Предметах:", styles['H2']))
        subject_averages = _calculate_group_subject_averages(group_df, config)
        if subject_averages:
            avg_data = [
                [Paragraph('Предмет', styles['TableHeader']), Paragraph('Середній Бал', styles['TableHeader'])]
            ]
            for subject, avg in subject_averages.items():
                avg_data.append([
                    Paragraph(subject, styles['TableCell']), 
                    Paragraph(f"{avg:.2f}", styles['TableCell'])
                ])
            
            table_avg = Table(avg_data, colWidths=[3.5*inch, 1.5*inch]) 
            table_avg.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkslategray), 
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey), 
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5)
            ]))
            story.append(table_avg)
        else:
            story.append(Paragraph("Немає даних про середні бали.", styles['LeftAligned']))
        story.append(Spacer(1, 0.2*inch))

        # --- Students with Scores Below 65 ---
        story.append(Paragraph("Студенти з Оцінками Нижче 65 (з будь-якого предмету):", styles['H2']))
        low_performers = _find_students_by_score_threshold(group_df, config, 65, 'less')
        if low_performers:
            low_performers_text = "<br/>".join([f"- {name}" for name in low_performers])
            story.append(Paragraph(low_performers_text, styles['LeftAligned']))
        else:
            story.append(Paragraph("Студентів з оцінками нижче 65 не знайдено.", styles['LeftAligned']))
        story.append(Spacer(1, 0.2*inch))

        # --- Students with Scores Above 95 ---
        story.append(Paragraph("Студенти з Оцінками Вище 95 (з будь-якого предмету):", styles['H2']))
        high_performers = _find_students_by_score_threshold(group_df, config, 95, 'greater')
        if high_performers:
            high_performers_text = "<br/>".join([f"- {name}" for name in high_performers])
            story.append(Paragraph(high_performers_text, styles['LeftAligned']))
        else:
            story.append(Paragraph("Студентів з оцінками вище 95 не знайдено.", styles['LeftAligned']))

        # --- Build the PDF ---
        doc.build(story)
        logging.info(f"PDF report saved successfully to {output_filename}")
        return str(output_filename)

    except Exception as e:
        logging.error(f"Failed to generate PDF report for group {group_id}: {e}", exc_info=True)
        return None