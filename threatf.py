import os
import csv
from tkinter import filedialog, Tk, Button

# Function to browse and select a folder
def browse_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        process_twistlock_files(folder_selected)

# Function to process all Twistlock vulnerability files
def process_twistlock_files(folder_path):
    # Initialize an empty set to store unique CVEs
    unique_cves = set()
    
    # Loop through all files in the selected folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".csv"):  # Assuming CSV files
            file_path = os.path.join(folder_path, file_name)
            # Read the CSV file to extract CVEs
            with open(file_path, mode='r') as file:
                reader = csv.DictReader(file)
                if 'CVE' in reader.fieldnames:  # Check if 'CVE' column exists
                    for row in reader:
                        unique_cves.add(row['CVE'])
    
    # Use threat_form.csv as a template to store CVE data
    collect_threat_info(unique_cves)

# Function to collect missing threat info from the user
def collect_threat_info(cves):
    threat_form = 'threat_form.csv'
    
    # Read the existing threat form template or create a new one
    if os.path.exists(threat_form):
        with open(threat_form, mode='r') as file:
            reader = csv.DictReader(file)
            existing_cves = {row['CVE ID'] for row in reader}
    else:
        # Create a new CSV file with the appropriate headers
        headers = ['CVE ID', 'CVSS Score', 'Severity', 'Asset Name/ID', 'Asset Criticality', 
                   'Attack Vector', 'Exploit Available (Y/N)', 'Potential Impact', 'Business Impact', 
                   'Patch Available (Y/N)', 'Patch Status (Applied/Not Applied)', 'Mitigating Controls', 
                   'Detection Mechanism', 'Date Discovered', 'Date Last Exploited', 'Business Risk', 
                   'Compliance Impact', 'MITRE ATT&CK Tactic', 'Comments']
        with open(threat_form, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
        existing_cves = set()

    # Open the CSV file in append mode to add new CVE entries
    with open(threat_form, mode='a', newline='') as file:
        writer = csv.writer(file)

        # Iterate through unique CVEs and collect missing information
        for cve in cves:
            if cve in existing_cves:
                continue  # Skip if CVE already exists in the file
            
            print(f"Enter data for CVE: {cve}")
            
            # Collecting missing information from the user
            cvss_score = input(f"Enter CVSS Score for {cve}: ")
            severity = input(f"Enter Severity (Low/Medium/High/Critical) for {cve}: ")
            asset_name = input(f"Enter Asset Name/ID for {cve}: ")
            asset_criticality = input(f"Enter Asset Criticality (Low/Medium/High/Critical) for {cve}: ")
            attack_vector = input(f"Enter Attack Vector for {cve} (e.g., network, local): ")
            exploit_available = input(f"Exploit Available (Y/N) for {cve}: ")
            potential_impact = input(f"Enter Potential Impact for {cve}: ")
            business_impact = input(f"Enter Business Impact for {cve}: ")
            patch_available = input(f"Patch Available (Y/N) for {cve}: ")
            patch_status = input(f"Patch Status (Applied/Not Applied) for {cve}: ")
            mitigating_controls = input(f"Mitigating Controls for {cve}: ")
            detection_mechanism = input(f"Detection Mechanism for {cve}: ")
            date_discovered = input(f"Date Discovered for {cve} (YYYY-MM-DD): ")
            date_last_exploited = input(f"Date Last Exploited for {cve} (YYYY-MM-DD): ")
            business_risk = input(f"Enter Business Risk (Low/Medium/High): ")
            compliance_impact = input(f"Enter Compliance Impact for {cve}: ")
            mitre_tactic = input(f"Enter MITRE ATT&CK Tactic for {cve} (if applicable): ")
            comments = input(f"Enter Comments for {cve} (optional): ")
            
            # Write the collected information to the CSV file
            writer.writerow([cve, cvss_score, severity, asset_name, asset_criticality, attack_vector, 
                             exploit_available, potential_impact, business_impact, patch_available, patch_status, 
                             mitigating_controls, detection_mechanism, date_discovered, date_last_exploited, 
                             business_risk, compliance_impact, mitre_tactic, comments])

# Setting up the Tkinter GUI
root = Tk()
root.title("Twistlock CVE Processor")

# Creating a button to select the folder
select_button = Button(root, text="Select Twistlock Vulnerability Folder", command=browse_folder)
select_button.pack(pady=20)

# Running the Tkinter main loop
root.mainloop()