import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import logging
from pathlib import Path
from typing import Optional

from .config import AppConfig

# Define the simplified score mapping
SCORE_MAP_345 = {
    (60, 74): 3,
    (75, 89): 4,
    (90, 100): 5,
}

# Create bins and labels for pd.cut based on the map
BINS_345 = [59] + [upper for lower, upper in sorted(SCORE_MAP_345.keys())]
LABELS_345 = [score for (lower, upper), score in sorted(SCORE_MAP_345.items(), key=lambda item: item[0][0])]

def _prepare_pie_chart_data(group_df: pd.DataFrame, config: AppConfig) -> pd.Series:
    """
    Prepares data for the group performance pie chart by converting
    scores to a 3/4/5 scale and counting occurrences.

    Args:
        group_df: DataFrame filtered for the specific group.
        config: Application configuration.

    Returns:
        A pandas Series with counts for each simplified score (3, 4, 5).
    """
    all_scores_345 = []
    for score_col in config.subject_score_columns:
        if score_col in group_df.columns and pd.api.types.is_numeric_dtype(group_df[score_col]):
            simplified_scores = pd.cut(
                group_df[score_col],
                bins=BINS_345,
                labels=LABELS_345,
                right=True,
                include_lowest=False
            ).dropna().astype(int)
            all_scores_345.extend(simplified_scores.tolist())

    if not all_scores_345:
        return pd.Series(dtype=int)

    score_counts = pd.Series(all_scores_345).value_counts().sort_index()
    score_counts.index = score_counts.index.map({3: 'Satisfactory (3)', 4: 'Good (4)', 5: 'Excellent (5)'})
    return score_counts


def create_group_performance_pie(group_df: pd.DataFrame, group_id: str, config: AppConfig) -> Optional[Figure]:
    """
    Args:
        group_df: DataFrame filtered for the specific group.
        group_id: The ID of the group being plotted.
        config: Application configuration.

    Returns:
        Matplotlib Figure object containing the plot, or None if plotting failed.
    """
    logging.info(f"Creating performance pie chart figure for group: {group_id}")
    try:
        score_counts = _prepare_pie_chart_data(group_df, config)

        if score_counts.empty:
            logging.warning(f"No valid scores found for group {group_id} to generate pie chart.")
            return None

        fig, ax = plt.subplots(figsize=(6, 6))
        ax.pie(score_counts, labels=score_counts.index, autopct='%1.1f%%', startangle=90, counterclock=False)
        ax.axis('equal')
        ax.set_title(f'Успішність Групи {group_id} (3/4/5 балів)')

        logging.info(f"Pie chart figure created for group {group_id}")
        return fig 
    except Exception as e:
        logging.error(f"Failed to create pie chart figure for group {group_id}: {e}", exc_info=True)
        plt.close('all')
        return None


def create_student_scores_bar(student_data: pd.Series, config: AppConfig) -> Optional[Figure]:
    """
    Args:
        student_data: A pandas Series representing a single student's data row.
        config: Application configuration.

    Returns:
        Matplotlib Figure object containing the plot, or None if plotting failed.
    """
    student_name = student_data.get(config.name_column, 'Невідомий Студент')
    logging.info(f"Creating scores bar chart figure for student: {student_name}")

    try:
        scores = {}
        for col in config.subject_score_columns:
            if col in student_data.index:
                scores[col.replace('(бали)', '').replace('(Бали)', '').strip()] = student_data[col]
            else:
                scores[col.replace('(бали)', '').replace('(Бали)', '').strip()] = np.nan

        scores_series = pd.Series(scores).dropna()

        if scores_series.empty:
            logging.warning(f"No valid scores found for student {student_name} to generate bar chart.")
            return None

        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.bar(scores_series.index, scores_series.values, color='cornflowerblue') 
        ax.set_ylabel('Бал')
        ax.set_title(f'Оцінки Студента: {student_name}')
        ax.set_ylim(0, 105)
        plt.xticks(rotation=40, ha='right', fontsize=9)

        ax.bar_label(bars, fmt='%.0f')
        plt.tight_layout()

        # plt.savefig(...) 
        # plt.close(fig)
        logging.info(f"Bar chart figure created for student {student_name}")
        return fig 

    except Exception as e:
        logging.error(f"Failed to create bar chart figure for student {student_name}: {e}", exc_info=True)
        plt.close('all') 
        return None