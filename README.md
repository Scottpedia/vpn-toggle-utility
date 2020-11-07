# vpn-toggle-utility

This branch of the repo is dedicated to a python script that deploys a ready-to-go client VPN endpoint on AWS, and also functions as a CLI to manage the endpoint. 

----------------------------------------------

# Requirements

- AWS CLI(boto3)
- python3
- easy-rsa

# Currently Proposed Workflow

1. Generating server-side and client-side credentials and upload them to ACM(AWS Certificate Manager) with AWS SDK.
1. Creating the Client VPN Components with AWS Cloudformation with the existing template.
1. Download the Client Connection Information.(.ovpn)
1. Insert the key and certificate into the  `.ovpn` file.
1. Save the setup information for CLI Commands.
1. Cleanup

```
Usage: ./client-vpn-toggler command
The followings are the available commands of this utility and the descriptions for them:
    
      get-status : Get the current association state of the client vpn endpoint. 
       associate : Associate the specified client vpn endpoint with the target subnet.
create-new-route : Create the additional route for the specified endpoint to allow the access to the Inernet.
    disassociate : Disassociate the target subnet from the client vpn endpoint.
         turn-on : The combination of two commands(associate & create-new-route) to quickly set up the endpoint.
            help : Display this help message.

Please note that the IDs for both client vpn enpoint and the target subnet are specified by defining the environment variables shown below:
    CLIENT_VPN_ENDPOINT_ID  
    SUBNET_ID
You can also specify the IDs directly in the script file by defining the variables above. This is especially useful if you want to use the script with the same resource repeatedly.
```
