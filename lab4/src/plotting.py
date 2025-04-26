import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging
from pathlib import Path
from typing import Optional

from .config import AppConfig # Assuming AppConfig holds relevant info

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
            # Apply pd.cut using the defined bins and labels
            simplified_scores = pd.cut(
                group_df[score_col],
                bins=BINS_345,
                labels=LABELS_345,
                right=True,
                include_lowest=False # Scores exactly 59 or lower won't be included
            ).dropna().astype(int) # Drop NaN results (scores outside 60-100) and convert labels (3,4,5) to int
            all_scores_345.extend(simplified_scores.tolist())

    if not all_scores_345:
        return pd.Series(dtype=int) # Return empty series if no valid scores

    # Count occurrences of 3, 4, 5
    score_counts = pd.Series(all_scores_345).value_counts().sort_index()
    score_counts.index = score_counts.index.map({3: 'Satisfactory (3)', 4: 'Good (4)', 5: 'Excellent (5)'})
    return score_counts


def plot_group_performance_pie(group_df: pd.DataFrame, group_id: str, config: AppConfig, output_dir: Path) -> Optional[str]:
    """
    Generates and saves a pie chart showing the distribution of simplified
    scores (3/4/5) for a specific student group.

    Args:
        group_df: DataFrame filtered for the specific group.
        group_id: The ID of the group being plotted.
        config: Application configuration.
        output_dir: Directory to save the plot.

    Returns:
        The path to the saved plot file, or None if plotting failed.
    """
    logging.info(f"Generating performance pie chart for group: {group_id}")
    try:
        score_counts = _prepare_pie_chart_data(group_df, config)

        if score_counts.empty:
            logging.warning(f"No valid scores found for group {group_id} to generate pie chart.")
            return None

        fig, ax = plt.subplots(figsize=(8, 8))
        ax.pie(score_counts, labels=score_counts.index, autopct='%1.1f%%', startangle=90, counterclock=False)
        ax.axis('equal') # Equal aspect ratio ensures that pie is drawn as a circle.
        ax.set_title(f'Overall Performance Distribution (Simplified Scale) - Group {group_id}')

        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        output_filename = output_dir / f"group_{group_id}_performance_pie.png"

        plt.savefig(output_filename)
        plt.close(fig) # Close the figure to free memory
        logging.info(f"Pie chart saved to {output_filename}")
        return str(output_filename)

    except Exception as e:
        logging.error(f"Failed to generate pie chart for group {group_id}: {e}", exc_info=True)
        return None


def plot_student_scores_bar(student_data: pd.Series, config: AppConfig, output_dir: Path) -> Optional[str]:
    """
    Generates and saves a bar chart showing the scores of a specific student
    across different subjects.

    Args:
        student_data: A pandas Series representing a single student's data row.
        config: Application configuration.
        output_dir: Directory to save the plot.

    Returns:
        The path to the saved plot file, or None if plotting failed.
    """
    student_name = student_data.get(config.name_column, 'Unknown Student')
    logging.info(f"Generating scores bar chart for student: {student_name}")

    try:
        # Extract scores for relevant columns, handling potential missing ones
        scores = {}
        for col in config.subject_score_columns:
            if col in student_data.index:
                scores[col.replace('(бали)', '').replace('(Бали)', '').strip()] = student_data[col] # Use cleaned name for label
            else:
                 scores[col.replace('(бали)', '').replace('(Бали)', '').strip()] = np.nan # Mark as NaN if column missing for student

        scores_series = pd.Series(scores).dropna() # Remove subjects with NaN scores

        if scores_series.empty:
            logging.warning(f"No valid scores found for student {student_name} to generate bar chart.")
            return None

        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(scores_series.index, scores_series.values, color='skyblue')
        ax.set_ylabel('Score')
        ax.set_xlabel('Subject')
        ax.set_title(f'Scores for {student_name}')
        ax.set_ylim(0, 105) # Set Y axis limit slightly above max score
        plt.xticks(rotation=45, ha='right') # Rotate labels if they overlap

        # Add score labels on top of bars
        ax.bar_label(bars, fmt='%.0f') # Display integer scores

        plt.tight_layout() # Adjust layout

        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        # Sanitize student name for filename
        safe_student_name = "".join(c if c.isalnum() else "_" for c in student_name)
        output_filename = output_dir / f"student_{safe_student_name}_scores_bar.png"

        plt.savefig(output_filename)
        plt.close(fig) # Close the figure
        logging.info(f"Bar chart saved to {output_filename}")
        return str(output_filename)

    except Exception as e:
        logging.error(f"Failed to generate bar chart for student {student_name}: {e}", exc_info=True)
        return None