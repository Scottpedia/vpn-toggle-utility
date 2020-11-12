# vpn-toggle-utility

This branch of the repo is dedicated to a python script that deploys a ready-to-go client VPN endpoint on AWS, and also functions as a CLI to manage the endpoint. This script will be soon merged into the project [main repository](https://github.com/Scottpedia/aws-client-vpn-setup).

----------------------------------------------

# Requirements

- bash
- boto3
- aws cli
- python3
- git

# Currently Proposed Workflow

1. Generate server-side and client-side credentials and upload them to ACM(AWS Certificate Manager) with AWS SDK.
1. Create the Client VPN Components with AWS Cloudformation with the existing template.
1. Download the Client Connection Information.(.ovpn)
1. Insert the key and certificate into the  `.ovpn` file.
1. Save the setup information.
1. Cleanup

```
Usage: ./client-vpn-manager [command] -f [the_config_file]
The python script to deploy and manage the vpn service based on AWS Client VPN Endpoints.

NOTE: PLEASE HAVE YOUR AWS CLI SETUP WITH YOUR AWS ACCOUNT BEFORE YOU RUN THIS SCRIPT.
      THE SCRIPT WILL NOT RUN WITHOUT AN AWS ACCOUNT SETUP WITH THE CLI.

***TO DEPLOY A NEW VPN SERVICE, please run the script without any command or option.***

***TO MANAGE AN EXISTING ENDPOINT, please use the following commands:***
    status  :   Output the current status of the specified VPN Endpoint.
    on      :   Turn on the VPN
    off     :   Turn off the VPN
    toggle  :   Toggle the VPN
   *help    :   Output the help 

    -f [Filename] (Optional)
    You can use the optional -f flag to specify the file which contains the profile of a specific VPN deployment.
    Thus you can have multiple deployments active at the same time, and manage each of them with its profile.
    If the file is not speficied, the program will automatically look for one under the current working directory.
    If multiple profiles are found under the CWD, should the most recent one be used.
```