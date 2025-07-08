# Run this python file to set up

# BEFORE RUNNING SCRIPT
# Create a new wireguard tunnel from scratch
# Generate a public and private key
# The script requires you to insert the Client public key into constant variable

# CLIENT SETUP AFTER RUNNING SCRIPT
# Retrive the Server's public key using ssh
# Add a peer
# Set peer's public key equal to Server's public key
# Make the address 10.0.0.2/32
# After it has been set up, add a peer with
# Edpoint as {ec2_public_ip}:51820
# Allowed IPs 0.0.0.0/0
# Persistent keepalive: 30 seconds

# IMPORTANT NOTES
# By deafult, will download .pem for ssh into user downloads
# SSH is configured to be only accessible on the device used to set it up
# The region can be changed to whatever you wish

import boto3
from botocore.exceptions import ClientError
import os
import requests

CLIENT_PUBLIC_KEY = "INSERT KEY HERE"
REGION = "us-east-1"
KEY_PAIR_NAME = "WireguardKeyPair"
KEY_PAIR_PATH = os.path.expanduser(f"~/Downloads/{KEY_PAIR_NAME}.pem")
THIS_IP = requests.get("https://api.ipify.org").text + "/32"

ec2_client = boto3.client("ec2", region_name=REGION)
ec2_resource = boto3.resource("ec2", region_name=REGION) # Service resource

# print(type(ec2_client))
# print(type(ec2_resource))

# Find the default VPC id
vpc_id = ec2_client.describe_vpcs(
    Filters=[{"Name": "isDefault", "Values": ["true"]}]
)["Vpcs"][0]["VpcId"]

# Create the security group
security_group = ec2_client.create_security_group(
    GroupName="WireguardVPN",
    Description="Allows UDP 51820",
    VpcId = vpc_id,
)
sg_id = security_group["GroupId"]

print(vpc_id)
print(sg_id)

# Create security group to allow ssh, wireguard port (51820)
ec2_client.authorize_security_group_ingress(
    GroupId=sg_id,
    IpPermissions=[
        {
            "IpProtocol": "udp",
            "FromPort": 51820,
            "ToPort": 51820,
            "IpRanges": [{"CidrIp": "0.0.0.0/0"}]
        },
        {
            "IpProtocol": "tcp",
            "FromPort": 22,
            "ToPort": 22,
            "IpRanges": [{"CidrIp": THIS_IP}]
        }
    ]
)

# Create key pair
try: 
    response = ec2_client.create_key_pair(KeyName=KEY_PAIR_NAME)
    private_key = response["KeyMaterial"]
    with open(KEY_PAIR_PATH, "w") as file:
        file.write(private_key)
    os.chmod(KEY_PAIR_PATH, 0o400)
    print("The key pair has been saved to user downloads")
except ClientError as err:
    if err.response["Error"]["Code"] == "InvalidKeyPair.Duplicate":
        print("Key pair already exists, using existing pair")
    else:
        raise 

# Prepare to create instance, load bash script
with open(os.path.join(__file__[:-12], "wireguard_setup.sh")) as f:
    sh_template = f.read()
sh_script = sh_template.replace(
    "__placeholderForClientPublicKey__", CLIENT_PUBLIC_KEY
)

# Create instance
instance = ec2_resource.create_instances( #type: ignore
    ImageId="ami-0a7d80731ae1b2435", # Amazon ubuntu 22.04
    InstanceType="t2.micro",
    MinCount=1,
    MaxCount=1,
    KeyName="WireguardKeyPair",
    SecurityGroupIds=[sg_id],

    # runs the script as root user
    UserData=sh_script
)[0]

instance.wait_until_running()
instance.reload()

print("Instance launched")
print(f"Public IPv4: {instance.public_ip_address}")

