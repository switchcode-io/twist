import os
import csv
from datetime import datetime

# Function to sort CSV rows by 'Fix Date' and 'Severity'
def format_and_sort_csvs(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(folder_path, filename)
            
            # Read the CSV file
            try:
                with open(file_path, mode='r', newline='', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    header = next(reader)
                    
                    # Identify the columns for 'Fix Date' and 'Severity'
                    if 'Fix Date' in header and 'Severity' in header:
                        fix_date_idx = header.index('Fix Date')
                        severity_idx = header.index('Severity')
                        
                        # Read the remaining rows
                        rows = list(reader)
                        
                        # Convert 'Fix Date' to datetime for proper sorting and sort by Severity and Fix Date
                        def sort_key(row):
                            try:
                                # Convert Fix Date to datetime, default to large date if invalid
                                fix_date = datetime.strptime(row[fix_date_idx], '%Y-%m-%d')
                            except ValueError:
                                fix_date = datetime.max  # Assign max date for invalid formats
                            
                            return (row[severity_idx], fix_date)
                        
                        # Sort the rows
                        rows.sort(key=sort_key)
                        
                        # Write the sorted rows back to the CSV file
                        with open(file_path, mode='w', newline='', encoding='utf-8') as output_file:
                            writer = csv.writer(output_file)
                            writer.writerow(header)  # Write header first
                            writer.writerows(rows)  # Write sorted rows
                        
                        print(f"Formatted and sorted: {filename}")
                    else:
                        print(f"Missing necessary columns in {filename}. Skipping.")
            
            except Exception as e:
                print(f"Error processing {filename}: {e}")

# Example folder path (replace this with your actual folder path)
folder_path = '_Vuln1'

# Call the function to format and sort CSV files
format_and_sort_csvs(folder_path)
