import csv
import os
from datetime import datetime, timedelta

# Define severity thresholds
severity_thresholds = {
    'Critical': 7,
    'High': 15,
    'Medium': 30,
    'Moderate': 30,
    'Low': 90
}

def calculate_days_between(start_date, end_date):
    """Helper function to calculate the number of days between two dates."""
    fmt = "%m/%d/%Y"  # Date format MM/DD/YYYY
    if not start_date or not end_date:
        return None
    try:
        start = datetime.strptime(start_date, fmt)
        end = datetime.strptime(end_date, fmt)
        return (end - start).days
    except ValueError:
        return None  # Handle invalid date format

def calculate_mttd(published_date, discovered_date):
    """Calculate MTTD (Mean Time to Detect) between Published and Discovered dates."""
    return calculate_days_between(published_date, discovered_date)

def calculate_mttr(fix_date):
    """Calculate MTTR (Mean Time to Remediate) between Fix Date and Current Date."""
    current_date = datetime.now().strftime("%m/%d/%Y")  # Get the current date in MM/DD/YYYY format
    return calculate_days_between(fix_date, current_date)

def calculate_compliance_date(discovered_date, severity):
    """Calculate Compliance Date based on discovered date and severity threshold."""
    if not discovered_date or severity not in severity_thresholds:
        return None
    try:
        fmt = "%m/%d/%Y"
        discovered = datetime.strptime(discovered_date, fmt)
        threshold_days = severity_thresholds[severity]
        compliance_date = discovered + timedelta(days=threshold_days)
        return compliance_date.strftime(fmt)
    except ValueError:
        return None

def calculate_days_overdue(compliance_date):
    """Calculate Days Overdue based on compliance date and today's date."""
    if not compliance_date:
        return None
    try:
        fmt = "%m/%d/%Y"
        today = datetime.now()
        compliance = datetime.strptime(compliance_date, fmt)
        return (today - compliance).days
    except ValueError:
        return None

def extract_vulnerability_data(folder_path, output_file):
    """Extracts CVE data from all CSV files in a folder and writes to a new CSV file."""
    # Open the output CSV file in write mode, and write the headers
    with open(output_file, mode='w', newline='') as outfile:
    
        writer = csv.writer(outfile)
        writer.writerow(['Environment','CVE', 'Severity', 'Type','Package','Published', 'Fix Date', 'Discovered', 'Compliance Date', 'Days Overdue'])

        # Iterate over all CSV files in the given folder
        for filename in os.listdir(folder_path):
            if filename.endswith('.csv'):
                filename1 = filename.split(" ")[0]
                file_path = os.path.join(folder_path, filename)
                
                # Open each CSV file
                with open(file_path, mode='r') as infile:
                    reader = csv.DictReader(infile)
                    
                    # Process each row in the file
                    for row in reader:
                        cve = row.get('CVE', '').strip()
                        severity = row.get('Severity', '').strip()
                        type = row.get('Type', '').strip()
                        published = row.get('Published', '').strip()
                        fix_date = row.get('Fix Date', '').strip()
                        discovered = row.get('Discovered', '').strip()
                        #Package Name	Installed Version
                        package = row.get('Package Name', '').strip() + " " +row.get('Installed Version', '').strip()

                      
                        # Calculate Compliance Date and Days Overdue
                        compliance_date = calculate_compliance_date(discovered, severity)
                        days_overdue = calculate_days_overdue(compliance_date)

                        # Write the extracted and calculated data to the new CSV file
                        writer.writerow([filename1, cve, severity, type, package, published, fix_date, discovered, compliance_date,  days_overdue])

    print(f"Data successfully extracted to {output_file}")

# Specify the folder path where your CSV files are located
folder_path = '_Vuln'  # Replace with actual folder path
output_file = '_charts/all_environments.csv'  # Output CSV file path

# Run the function
extract_vulnerability_data(folder_path, output_file)
