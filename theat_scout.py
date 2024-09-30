from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# Function to fetch CVE data from the MITRE CVE API
def fetch_cve_data(cve_id):
    """
    Function to fetch CVE data from the MITRE CVE API and return a JSON response.
    """
    url = f"https://cveawg.mitre.org/api/cve/{cve_id}"
    
    try:
        # Make a GET request to the API
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code == 200:
            cve_data = response.json()
            # Extract CVSS v3.x metrics
            if 'impact' in cve_data and 'cvssV3' in cve_data['impact']:
                cvss_v3 = cve_data['impact']['cvssV3']
                base_score = cvss_v3.get('baseScore', 'N/A')
                confidentiality_impact = cvss_v3.get('confidentialityImpact', 'N/A')
                integrity_impact = cvss_v3.get('integrityImpact', 'N/A')
                availability_impact = cvss_v3.get('availabilityImpact', 'N/A')
                
                return {
                    "CVE_ID": cve_id,
                    "Base_Score": base_score,
                    "Confidentiality_Impact": confidentiality_impact,
                    "Integrity_Impact": integrity_impact,
                    "Availability_Impact": availability_impact
                }
            else:
                return {"error": f"No CVSS v3.x data found for {cve_id}"}
        else:
            return {"error": f"Failed to fetch data for {cve_id}, HTTP Status Code: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

# API route to fetch CVE data
@app.route('/cve/<cve_id>', methods=['GET'])
def get_cve_data(cve_id):
    """
    API endpoint to fetch CVE data based on the CVE ID provided in the URL.
    """
    # Call the fetch_cve_data function to get the data
    cve_info = fetch_cve_data(cve_id)
    
    # Return the data as a JSON response
    return jsonify(cve_info)

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
