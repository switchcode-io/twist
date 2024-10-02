import http.client
import json
import ssl

def download_twistlock_vulnerability_scans(base_url, username, password, output_file='vulnerability_report.json'):
    """
    Function to download vulnerability scans from a Twistlock (Prisma Cloud) server using http.client.

    Parameters:
    - base_url: URL of the Twistlock (Prisma Cloud) console (e.g., "twistlock.example.com").
    - username: API username.
    - password: API password.
    - output_file: File where the downloaded report will be saved (default is 'vulnerability_report.json').

    Returns:
    - None (downloads the report to the specified file).
    """

    try:
        # Disable SSL certificate verification (optional: only if required)
        context = ssl._create_unverified_context()

        # Extract the hostname and determine if it's an HTTPS connection
        if base_url.startswith("https://"):
            hostname = base_url.replace("https://", "")
            connection = http.client.HTTPSConnection(hostname, context=context)
        elif base_url.startswith("http://"):
            hostname = base_url.replace("http://", "")
            connection = http.client.HTTPConnection(hostname)
        else:
            print("Invalid URL format. Please include 'http://' or 'https://'.")
            return

        # Step 1: Authenticate and get the token (POST /api/v1/authenticate)
        auth_path = "/api/v1/authenticate"
        auth_payload = json.dumps({
            "username": username,
            "password": password
        })

        headers = {
            "Content-Type": "application/json"
        }

        # Send authentication request
        connection.request("POST", auth_path, body=auth_payload, headers=headers)
        response = connection.getresponse()

        if response.status != 200:
            print(f"Failed to login. HTTP Status Code: {response.status}")
            print(response.read().decode())
            return

        # Read the authentication token from the response
        response_data = response.read().decode()
        token_data = json.loads(response_data)
        token = token_data.get("token")

        if not token:
            print("Failed to retrieve authentication token.")
            return

        print(f"Successfully authenticated. Token: {token}")

        # Step 2: Fetch the vulnerability scan report (GET /api/v1/vulnerabilities/host)
        vuln_report_path = "/api/v1/vulnerabilities/host"
        
        # Headers with the Bearer token
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # Send GET request to retrieve the vulnerability report
        connection.request("GET", vuln_report_path, headers=headers)
        response = connection.getresponse()

        if response.status == 200:
            # Read and save the report
            report_data = response.read().decode()
            with open(output_file, 'w') as f:
                f.write(report_data)
            print(f"Vulnerability scan report saved to {output_file}.")
        else:
            print(f"Failed to retrieve vulnerability scans. HTTP Status Code: {response.status}")
            print(response.read().decode())

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        connection.close()

# Example usage
if __name__ == "__main__":
    # Replace these with your actual Twistlock (Prisma Cloud) server details
    base_url = "https://your-twistlock-server.com"
    username = "your_username"
    password = "your_password"

    download_twistlock_vulnerability_scans(base_url, username, password)
