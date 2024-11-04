import boto3
import time
import logging
import csv
import os

# Define the paths
CSV_FILE = "workspaces_list.csv"  # Path to CSV with WorkSpace details
LOCAL_FILE_PATH = "file_to_copy.txt"  # Local file to be copied
REMOTE_FILE_PATH_WINDOWS = r"C:\Users\Public\file_to_copy.txt"
REMOTE_FILE_PATH_LINUX = "/home/ec2-user/file_to_copy.txt"
LOG_FILE = "file_copy_results.log"

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

def upload_file_to_workspace(instance_id, platform_type):
    """
    Uses SSM to upload a local file to the specified WorkSpace based on OS type.
    """
    try:
        # Read the content of the local file
        with open(LOCAL_FILE_PATH, 'r') as file:
            file_content = file.read()
        
        # Set remote file path based on OS type
        if platform_type == "Windows":
            remote_file_path = REMOTE_FILE_PATH_WINDOWS
            command = f"echo '{file_content}' > {remote_file_path}"
        elif platform_type == "Linux":
            remote_file_path = REMOTE_FILE_PATH_LINUX
            command = f"echo '{file_content}' > {remote_file_path}"

        # Run the command on the WorkSpace
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
            logging.info(f"Workspace {instance_id} ({platform_type}): File copied to {remote_file_path}")
            print(f"Workspace {instance_id} ({platform_type}): File copied to {remote_file_path}")
        else:
            error_msg = result['StandardErrorContent'].strip()
            logging.error(f"Workspace {instance_id} ({platform_type}): Command failed - {error_msg}")
            print(f"Workspace {instance_id} ({platform_type}): Command failed - {error_msg}")
    
    except Exception as e:
        logging.error(f"Workspace {instance_id} ({platform_type}): Error - {str(e)}")
        print(f"Workspace {instance_id} ({platform_type}): Error - {str(e)}")

def main():
    # Check if the local file exists
    if not os.path.exists(LOCAL_FILE_PATH):
        print(f"Error: The file '{LOCAL_FILE_PATH}' does not exist.")
        return
    
    # Load list of WorkSpaces from CSV file
    instances = load_workspace_instances_from_csv(CSV_FILE)
    if not instances:
        print("No WorkSpaces found in the CSV file.")
        return
    
    print(f"Found {len(instances)} WorkSpaces in CSV. Starting file copy process...")
    
    # Iterate over each WorkSpace and upload the file based on OS type
    for instance in instances:
        instance_id = instance['InstanceId']
        platform_type = instance['OperatingSystem']
        
        # Upload file based on OS
        upload_file_to_workspace(instance_id, platform_type)

    print("File copy process completed. Check the log file for results.")

if __name__ == "__main__":
    main()
