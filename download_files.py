import boto3
import os

# Configure S3 bucket and directory
S3_BUCKET = "your-s3-bucket-name"
S3_DIRECTORY = "scripts"  # Optional folder in the bucket where scripts are stored, leave empty if scripts are in the root

# List of scripts to download
scripts = [
    "install_splunk.sh",
    "delete_file.py",
    "copy_file.py",
    "configure_splunk.py"
]

# Initialize S3 client
s3_client = boto3.client('s3')

def download_script_from_s3(file_name):
    """
    Download a script from the specified S3 bucket and directory.
    """
    s3_key = f"{S3_DIRECTORY}/{file_name}" if S3_DIRECTORY else file_name
    try:
        print(f"Downloading {file_name} from s3://{S3_BUCKET}/{s3_key}...")
        s3_client.download_file(S3_BUCKET, s3_key, file_name)
        print(f"Downloaded {file_name}")
    except Exception as e:
        print(f"Failed to download {file_name}: {e}")
        return False
    return True

def main():
    for script in scripts:
        # Download the script
        if not download_script_from_s3(script):
            print(f"Skipping {script} due to download failure.")
            continue

    print("All scripts have been downloaded.")

if __name__ == "__main__":
    main()
