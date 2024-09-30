import requests
import csv
import os

def get_cve_data(cve_id):
    """
    Function to fetch all relevant CVE data from the CVE API based on a supplied CVE ID.
    Appends the CVE data to a CSV file.
    """
    # Define the base URL for the API
    url = f"https://cveawg.mitre.org/api/cve/{cve_id}"
    
    try:
        # Make a GET request to the API
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON data returned by the API
            cve_data = response.json()
            
            # Initialize default values in case data is missing
            title = "N/A"
            severity = "N/A"
            base_score = "N/A"
            published_date = "N/A"
            impact_type = "N/A"
            attack_vector = "N/A"
            attack_complexity = "N/A"
            privileges_required = "N/A"
            user_interaction = "N/A"
            scope = "N/A"
            confidentiality_impact = "N/A"
            integrity_impact = "N/A"
            availability_impact = "N/A"
            affected_products = []
            references = []
            
            # Extract title and datePublic (from containers.cna)
            if 'containers' in cve_data and 'cna' in cve_data['containers']:
                title = cve_data['containers']['cna'].get('title', 'N/A')
                published_date = cve_data['containers']['cna'].get('datePublic', 'N/A')
            
                # Extract affected products
                affected = cve_data['containers']['cna'].get('affected', [])
                for product in affected:
                    vendor = product.get('vendor', 'N/A')
                    prod_name = product.get('product', 'N/A')
                    versions = [v.get('version', 'N/A') for v in product.get('versions', [])]
                    affected_products.append(f"{vendor} {prod_name} versions: {', '.join(versions)}")
            
                # Extract references
                references = [ref['url'] for ref in cve_data['containers']['cna'].get('references', [])]
            
            # Extract severity and baseScore (from containers.cna.metrics.cvssV3_1)
            if 'containers' in cve_data and 'cna' in cve_data['containers']:
                metrics = cve_data['containers']['cna'].get('metrics', [])
                for metric in metrics:
                    if 'cvssV3_1' in metric:
                        severity = metric['cvssV3_1'].get('baseSeverity', 'N/A')
                        base_score = metric['cvssV3_1'].get('baseScore', 'N/A')
                        attack_vector = metric['cvssV3_1'].get('attackVector', 'N/A')
                        attack_complexity = metric['cvssV3_1'].get('attackComplexity', 'N/A')
                        privileges_required = metric['cvssV3_1'].get('privilegesRequired', 'N/A')
                        user_interaction = metric['cvssV3_1'].get('userInteraction', 'N/A')
                        scope = metric['cvssV3_1'].get('scope', 'N/A')
                        confidentiality_impact = metric['cvssV3_1'].get('confidentialityImpact', 'N/A')
                        integrity_impact = metric['cvssV3_1'].get('integrityImpact', 'N/A')
                        availability_impact = metric['cvssV3_1'].get('availabilityImpact', 'N/A')
                        break  # Exit after finding the first CVSS metrics
            
            # Extract impact (from containers.cna.problemTypes.descriptions[].type)
            if 'containers' in cve_data and 'cna' in cve_data['containers']:
                problem_types = cve_data['containers']['cna'].get('problemTypes', [])
                for problem in problem_types:
                    if 'descriptions' in problem:
                        for description in problem['descriptions']:
                            if description.get('type', '') == 'Impact':
                                impact_type = description.get('description', 'N/A')
                                break
            
            # Append the data to a CSV file
            save_to_csv(cve_id, title, severity, base_score, published_date, impact_type, 
                        attack_vector, attack_complexity, privileges_required, user_interaction, 
                        scope, confidentiality_impact, integrity_impact, availability_impact, 
                        affected_products, references)
            
        else:
            print(f"Failed to fetch data. HTTP Status Code: {response.status_code}")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def save_to_csv(cve_id, title, severity, base_score, published_date, impact_type, 
                attack_vector, attack_complexity, privileges_required, user_interaction, 
                scope, confidentiality_impact, integrity_impact, availability_impact, 
                affected_products, references):
    """
    Appends all relevant CVE data to a CSV file.
    """
    # Define the CSV file path
    csv_file = 'cve_full_data.csv'
    
    # Check if the file exists to determine if the header is needed
    file_exists = os.path.isfile(csv_file)

    # Open the CSV file in append mode
    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Write the header if the file does not exist
        if not file_exists:
            writer.writerow([
                                'CVE ID', 'Title', 'Severity', 'Base Score', 'Published Date', 'Impact Type', 
                'Attack Vector', 'Attack Complexity', 'Privileges Required', 'User Interaction', 
                'Scope', 'Confidentiality Impact', 'Integrity Impact', 'Availability Impact', 
                'Affected Products', 'References'
            ])
        
        # Write the data
        writer.writerow([
            cve_id, title, severity, base_score, published_date, impact_type, 
            attack_vector, attack_complexity, privileges_required, user_interaction, 
            scope, confidentiality_impact, integrity_impact, availability_impact, 
            '; '.join(affected_products), '; '.join(references)
        ])
    
    print(f"Data for {cve_id} has been appended to {csv_file}")

# Main function to run the script
if __name__ == "__main__":
    # Prompt the user to enter a CVE ID
    cve_id = input("Enter CVE ID (e.g., CVE-2021-34527): ").strip()
    
    # Validate the CVE ID format
    if not cve_id.startswith("CVE-"):
        print("Invalid CVE ID format. Please enter a valid CVE ID.")
    else:
        # Call the function to get CVE data
        get_cve_data(cve_id)
