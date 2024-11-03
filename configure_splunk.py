import boto3

# AWS Configuration
INSTANCE_ID = 'i-08707f6c15abfa43b'
PORT = 8000
PROTOCOL = 'tcp'
CIDR_IP = '0.0.0.0/0'  # Allow access from any IP

# Initialize boto3 client for EC2
ec2_client = boto3.client('ec2')

def get_security_group_id(instance_id):
    """Fetches the security group ID for the specified EC2 instance."""
    try:
        response = ec2_client.describe_instances(InstanceIds=[instance_id])
        security_groups = response['Reservations'][0]['Instances'][0]['SecurityGroups']
        # Assuming the instance has only one security group, otherwise modify as needed
        return security_groups[0]['GroupId']
    except Exception as e:
        print(f"Error retrieving security group ID: {e}")
        return None

def check_port_open(security_group_id, port, protocol, cidr_ip):
    """Checks if a rule exists that allows inbound traffic on the specified port."""
    try:
        response = ec2_client.describe_security_groups(GroupIds=[security_group_id])
        permissions = response['SecurityGroups'][0]['IpPermissions']
        
        for permission in permissions:
            if permission['FromPort'] == port and permission['IpProtocol'] == protocol:
                for ip_range in permission['IpRanges']:
                    if ip_range['CidrIp'] == cidr_ip:
                        return True
        return False
    except Exception as e:
        print(f"Error checking port rule: {e}")
        return False

def configure_firewall(security_group_id, port, protocol, cidr_ip):
    """Adds a rule to the security group to allow inbound traffic on the specified port."""
    try:
        ec2_client.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[
                {
                    'IpProtocol': protocol,
                    'FromPort': port,
                    'ToPort': port,
                    'IpRanges': [{'CidrIp': cidr_ip}]
                }
            ]
        )
        print(f"Port {port} opened successfully on security group {security_group_id}.")
    except ec2_client.exceptions.ClientError as e:
        if 'InvalidPermission.Duplicate' in str(e):
            print(f"Port {port} is already open on security group {security_group_id}.")
        else:
            print(f"Error adding port rule: {e}")

def main():
    # Get the security group ID
    security_group_id = get_security_group_id(INSTANCE_ID)
    if not security_group_id:
        print("Failed to retrieve security group ID. Exiting.")
        return

    # Check if port is already open
    if check_port_open(security_group_id, PORT, PROTOCOL, CIDR_IP):
        print(f"Port {PORT} is already open on security group {security_group_id}.")
    else:
        print(f"Opening port {PORT} on security group {security_group_id}...")
        configure_firewall(security_group_id, PORT, PROTOCOL, CIDR_IP)

if __name__ == "__main__":
    main()
