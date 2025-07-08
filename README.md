# VPN
My attempt at 'automatic' VPN creation  

# Run this python file to set up

# BEFORE RUNNING SCRIPT
Requires an AWS account with access to ec2  
Configure the permissions for AWS account  

Need to download the wireguard app on client device  
Create a new wireguard tunnel from scratch  
Generate a public and private key  
The script requires you to insert the Client public key into constant variable  

# CLIENT SETUP AFTER RUNNING SCRIPT  
Retrive the Server's public key using ssh  
Add a peer  
Set peer's public key equal to Server's public key  
Make the address 10.0.0.2/32  
After it has been set up, add a peer with  
Edpoint as {ec2_public_ip}:51820  
Allowed IPs 0.0.0.0/0  
Persistent keepalive: 30 seconds  

# IMPORTANT NOTES
By deafult, will download .pem for ssh into user downloads  
SSH is configured to be only accessible on the device used to set it up  
The region can be changed to whatever you wish  
...Aaaand it might not work exactly as intended.  
