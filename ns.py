import os
import csv
import subprocess

# Function to perform nslookup using os command
def ns_lookup(ip):
    try:
        # Using subprocess to run nslookup and capture output
        result = subprocess.run(['nslookup', ip], capture_output=True, text=True)
        output = result.stdout
        # Parse the output to get the hostname
        for line in output.splitlines():
            if "name =" in line:
                return line.split("name =")[1].strip()
        return "Hostname not found"
    except Exception as e:
        return f"Error: {str(e)}"

# Function to process the CSV and perform the NS lookup for each team
def process_ec2_file(input_file):
    teams = []
    with open(input_file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        # Read headers (team names)
        teams = next(reader)

        # Initialize a dictionary to store results for each team
        team_results = {team: [] for team in teams}

        # Process each row (IP addresses)
        for row in reader:
            for idx, ip in enumerate(row):
                ip = ip.strip()  # Clean up any leading/trailing spaces
                if ip:  # Check if the cell contains an IP address
                    team_name = teams[idx]
                    hostname = ns_lookup(ip)
                    team_results[team_name].append((ip, hostname))

        # Output results to separate files for each team
        for team, results in team_results.items():
            output_file = f"{team}.csv"
            with open(output_file, 'w', newline='') as outfile:
                writer = csv.writer(outfile)
                writer.writerow(["IP Address", "Hostname"])
                writer.writerows(results)
            print(f"Results written to {output_file}")

# Entry point
if __name__ == "__main__":
    input_csv = 'ec2.csv'  # Input CSV file
    process_ec2_file(input_csv)