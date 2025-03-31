import logging
import pandas as pd
from pathlib import Path

from .analysis import DataAnalyzer
from .plotting import plot_group_performance_pie, plot_student_scores_bar
from .pdf_reporter import generate_group_report_pdf


def display_student_info(student_data: pd.Series, config):
    """Formats and prints student details."""
    print("\n--- Student Details ---")
    print(f"Name: {student_data.get(config.name_column, 'N/A')}")
    print(f"Group: {student_data.get(config.group_column, 'N/A')}")
    print(f"GPA: {student_data.get(config.gpa_column, 'N/A'):.2f}")
    print(f"Receives Scholarship: {'Yes' if student_data.get(config.scholarship_column) == config.scholarship_marker else 'No'}")
    print("\nScores:")
    for score_col in config.subject_score_columns:
        grade_col = config.get_national_scale_column_name(score_col)
        score = student_data.get(score_col, 'N/A')
        grade = student_data.get(grade_col, 'N/A')
        subject_name = score_col.replace('(бали)', '').replace('(Бали)', '').strip()
        # Format score nicely, handling potential NaN or non-numeric
        score_str = f"{score:.0f}" if isinstance(score, (int, float)) and pd.notna(score) else str(score)
        print(f"  - {subject_name}: {score_str} ({grade})")
    print("-" * 21)


def display_group_info(group_stats: dict):
    """Formats and prints group statistics."""
    print("\n--- Group Statistics ---")
    print(f"Group ID: {group_stats.get('group_id', 'N/A')}")
    print(f"Total Students: {group_stats.get('students_in_group', 'N/A')}")
    print(f"Scholarship Recipients: {group_stats.get('scholarship_recipients_in_group', 'N/A')}")
    print(f"Average GPA: {group_stats.get('average_gpa_in_group', 'N/A'):.2f}")
    print(f"Highest Scorer: {group_stats.get('highest_gpa_student_in_group', 'N/A')}")
    print(f"Lowest Scorer: {group_stats.get('lowest_gpa_student_in_group', 'N/A')}")
    print("-" * 22)


def display_scholarship_list(scholars_df: pd.DataFrame, config):
    """Prints the list of students receiving scholarships."""
    if scholars_df is None or scholars_df.empty:
        print("\nNo students found receiving scholarships.")
        return
        
    print("\n--- Scholarship Recipients ---")
    for name in scholars_df[config.name_column]:
        print(f"- {name}")
    print("-" * 28)


def run_cli(analyzer: DataAnalyzer):
    """Runs the main command-line interface loop."""
    
    if not analyzer._is_processed or analyzer.processed_df is None:
        print("Error: Data analysis could not be completed. Cannot start CLI.")
        logging.critical("Attempted to start CLI without processed data.")
        return

    print("\n--- Student Performance Analysis CLI ---")
    
    while True:
        print("\nAvailable Commands:")
        print("  1. Find Student by Name")
        print("  2. Show Group Statistics")
        print("  3. List All Scholarship Recipients")
        print("  4. Generate Group Performance Plot (Pie Chart)")
        print("  5. Generate Student Score Plot (Bar Chart)")
        print("  6. Generate Group PDF Report")
        print("  0. Exit")
        
        choice = input("Enter command number: ").strip()

        try:
            if choice == '1':
                search_term = input("Enter full or partial student name: ").strip()
                if not search_term:
                    print("Search term cannot be empty.")
                    continue
                
                results = analyzer.find_student_by_name(search_term)
                if results is None or results.empty:
                    print(f"No students found matching '{search_term}'.")
                elif len(results) == 1:
                    display_student_info(results.iloc[0], analyzer.config)
                else:
                    print(f"\nMultiple students found for '{search_term}'. Please be more specific:")
                    for i, name in enumerate(results[analyzer.config.name_column]):
                        print(f"  {i+1}. {name}")

            elif choice == '2':
                group_id = input(f"Enter group ID (or press Enter for default '{analyzer.config.target_group}'): ").strip()
                if not group_id:
                    group_id = analyzer.config.target_group # Use default if empty
                
                try:
                    group_stats = analyzer.get_group_stats(group_id)
                    display_group_info(group_stats)
                except ValueError as e:
                    print(f"Error: {e}") # Group not found error

            elif choice == '3':
                 scholars = analyzer.get_scholarship_students()
                 display_scholarship_list(scholars, analyzer.config)

            elif choice == '4':
                group_id = input(f"Enter group ID for plot (or press Enter for default '{analyzer.config.target_group}'): ").strip()
                if not group_id:
                    group_id = analyzer.config.target_group
                
                group_df = analyzer.get_group_data(group_id)
                if group_df is None or group_df.empty:
                     print(f"Error: Group '{group_id}' not found or has no data.")
                     continue

                output_file = plot_group_performance_pie(group_df, group_id, analyzer.config, Path("output"))
                if output_file:
                    print(f"Group performance pie chart saved to: {output_file}")
                else:
                    print(f"Could not generate pie chart for group {group_id}.")

            elif choice == '5':
                 search_term = input("Enter full or partial name of the student for the plot: ").strip()
                 if not search_term:
                    print("Search term cannot be empty.")
                    continue
                 results = analyzer.find_student_by_name(search_term)
                 
                 selected_student_data = None
                 if results is None or results.empty:
                    print(f"No students found matching '{search_term}'.")
                 elif len(results) == 1:
                    selected_student_data = results.iloc[0]
                 else:
                     # Handle multiple matches if needed (e.g., ask user to choose)
                     print(f"Multiple students found matching '{search_term}'. Please refine your search.")
                     # For now, we'll just skip plotting if multiple found
                     
                 if selected_student_data is not None:
                     output_file = plot_student_scores_bar(selected_student_data, analyzer.config, Path("output"))
                     if output_file:
                         print(f"Student score bar chart saved to: {output_file}")
                     else:
                         print(f"Could not generate bar chart for the student.")

            elif choice == '6':
                group_id = input(f"Enter group ID for PDF report (or press Enter for default '{analyzer.config.target_group}'): ").strip()
                if not group_id:
                    group_id = analyzer.config.target_group

                try:
                    group_stats = analyzer.get_group_stats(group_id) # Get stats first
                    group_df = analyzer.get_group_data(group_id) # Then get data
                    
                    if group_df is None or group_df.empty: # Should be caught by get_group_stats already, but double check
                        print(f"Error: Group '{group_id}' not found or has no data.")
                        continue

                    output_file = generate_group_report_pdf(group_df, group_stats, group_id, analyzer.config, Path("output"))
                    if output_file:
                        print(f"Group PDF report saved to: {output_file}")
                    else:
                        print(f"Could not generate PDF report for group {group_id}.")

                except ValueError as e: # Catch group not found from get_group_stats
                     print(f"Error: {e}")
                except Exception as e: # Catch potential errors during PDF generation
                     print(f"An unexpected error occurred during PDF generation: {e}")
                     logging.error("PDF generation failed", exc_info=True)


            elif choice == '0':
                print("Exiting CLI. Goodbye!")
                break

            else:
                print("Invalid command number. Please try again.")

        except KeyboardInterrupt:
             print("\nOperation cancelled by user. Exiting.")
             break
        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}")
            logging.error("CLI Error", exc_info=True)