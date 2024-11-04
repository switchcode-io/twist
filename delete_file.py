import boto3
import time
import logging

# Define the path of the file you want to delete
FILE_PATH = "/path/to/your/file"
LOG_FILE = "delete_file_results.log"

# Configure logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, 
                    format="%(asctime)s - %(message)s")

# Initialize SSM and WorkSpaces clients
ssm_client = boto3.client('ssm')
workspaces_client = boto3.client('workspaces')

def get_all_workspace_instances():
    """
    Retrieves all WorkSpace instances in the environment.
    """
    instance_ids = []
    paginator = workspaces_client.get_paginator('describe_workspaces')
    for page in paginator.paginate():
        for workspace in page['Workspaces']:
            instance_ids.append(workspace['WorkspaceId'])
    return instance_ids

def delete_file_on_workspace(instance_id):
    """
    Uses SSM to sudo to `su`, checks for the file, and deletes it if found.
    Logs the result for each WorkSpace.
    """
    command = f'sudo su -c "if [ -f {FILE_PATH} ]; then rm -f {FILE_PATH}; echo Deleted; else echo Not found; fi"'
    
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
            logging.info(f"Workspace {instance_id}: {output}")
            print(f"Workspace {instance_id}: {output}")
        else:
            error_msg = result['StandardErrorContent'].strip()
            logging.error(f"Workspace {instance_id}: Command failed - {error_msg}")
            print(f"Workspace {instance_id}: Command failed - {error_msg}")
    
    except Exception as e:
        logging.error(f"Workspace {instance_id}: Error - {str(e)}")
        print(f"Workspace {instance_id}: Error - {str(e)}")

def main():
    # Get list of all WorkSpaces
    instance_ids = get_all_workspace_instances()
    if not instance_ids:
        print("No WorkSpaces found.")
        return
    
    print(f"Found {len(instance_ids)} WorkSpaces. Starting file deletion process...")
    
    # Iterate over each WorkSpace and delete the file if it exists
    for instance_id in instance_ids:
        delete_file_on_workspace(instance_id)

    print("File deletion process completed. Check the log file for results.")

if __name__ == "__main__":
    main()
