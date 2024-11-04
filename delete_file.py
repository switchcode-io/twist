import boto3
import time
import logging
import csv

# Define the CSV file path and the log file
CSV_FILE = "workspaces_list.csv"
LOG_FILE = "remove_nessus_agent_results.log"

# Configure logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, 
                    format="%(asctime)s - %(message)s")

# Initialize SSM client
ssm_client = boto3.client('ssm')

def load_workspace_instances_from_csv(csv_file):
    """
    Reads the WorkSpace instance IDs and OS types from the provided CSV file.
    Returns a list of dictionaries with 'InstanceId' and 'OperatingSystem' keys.
    """
    instances = []
    try:
        with open(csv_file, mode='r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                instances.append({
                    'InstanceId': row['InstanceId'],
                    'OperatingSystem': row['OperatingSystem']
                })
    except FileNotFoundError:
        print(f"Error: CSV file '{csv_file}' not found.")
        return []
    except KeyError:
        print("Error: CSV file must contain 'InstanceId' and 'OperatingSystem' columns.")
        return []
    
    return instances

def remove_nessus_agent_on_workspace(instance_id, platform_type):
    """
    Uses SSM to remove the Nessus Agent based on the OS type of the WorkSpace.
    Logs the result for each WorkSpace.
    """
    if platform_type == "Windows":
        # Command to remove Nessus Agent on Windows
        command = r'"C:\Program Files\Tenable\Nessus Agent\nessuscli.exe" agent unlink && ' \
                  r'rmdir /S /Q "C:\ProgramData\Tenable\Nessus Agent"'
    elif platform_type == "Linux":
        # Command to remove Nessus Agent on Linux
        command = 'sudo /opt/nessus_agent/sbin/nessuscli agent unlink && ' \
                  'sudo rm -rf /opt/nessus_agent'

    try:
        # Run command on the WorkSpace
        response = ssm_client.send_command(
            InstanceIds=[instance_id],
            DocumentName="AWS-RunShellScript",
            Parameters={"commands": [command]},
        )
        
        command_id = response['Command']['CommandId']
        
        # Wait for command to finish
        time.sleep(2)
        
        # Check command status and retrieve output
        result = ssm_client.get_command_invocation(
            CommandId=command_id,
            InstanceId=instance_id
        )
        
        # Log the outcome
        if result['Status'] == 'Success':
            output = result['StandardOutputContent'].strip()
            logging.info(f"Workspace {instance_id} ({platform_type}): {output}")
            print(f"Workspace {instance_id} ({platform_type}): {output}")
        else:
            error_msg = result['StandardErrorContent'].strip()
            logging.error(f"Workspace {instance_id} ({platform_type}): Command failed - {error_msg}")
            print(f"Workspace {instance_id} ({platform_type}): Command failed - {error_msg}")
    
    except Exception as e:
        logging.error(f"Workspace {instance_id} ({platform_type}): Error - {str(e)}")
        print(f"Workspace {instance_id} ({platform_type}): Error - {str(e)}")

def main():
    # Load list of WorkSpaces from CSV file
    instances = load_workspace_instances_from_csv(CSV_FILE)
    if not instances:
        print("No WorkSpaces found in the CSV file.")
        return
    
    print(f"Found {len(instances)} WorkSpaces in CSV. Starting Nessus Agent removal process...")
    
    # Iterate over each WorkSpace and remove the Nessus Agent based on OS type
    for instance in instances:
        instance_id = instance['InstanceId']
        platform_type = instance['OperatingSystem']
        
        # Remove Nessus Agent based on OS
        remove_nessus_agent_on_workspace(instance_id, platform_type)

    print("Nessus Agent removal process completed. Check the log file for results.")

if __name__ == "__main__":
    main()
