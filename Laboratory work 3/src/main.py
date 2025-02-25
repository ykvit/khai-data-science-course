from analyzer import StudentPerformanceAnalyzer

def main():
    """Main function to run the student performance analysis."""
    try:
        # Initialize analyzer with input and output file paths
        analyzer = StudentPerformanceAnalyzer(
            input_file='data/LW3.xlsx',
            output_file='output/LW3_processed.xlsx'
        )
        
        # Process data and get statistics
        highest, lowest, scholarship_count = analyzer.process_data()
        
        # Print results
        print("\nAnalysis Results:")
        print(f"Highest scoring student: {highest}")
        print(f"Lowest scoring student: {lowest}")
        print(f"Number of scholarship recipients: {scholarship_count}")
        
    except Exception as e:
        print(f"\nError during analysis: {str(e)}")
        print("Please check your input file and ensure it contains student names and numeric scores.")

if __name__ == "__main__":
    main()