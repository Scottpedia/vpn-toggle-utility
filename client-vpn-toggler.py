#!/usr/bin/env python3
import boto3
import os
import sys
import traceback
import string
import random

client = boto3.client("ec2")

'''
So please leave these values below blank if you want to specify the ids with system environment variables.
Otherwise, the values specified here would override the environment variables.
'''
CLIENT_VPN_ENDPOINT_ID = ""
SUBNET_ID = ""
USER_SETTINGS = {}
HELP_SCRIPT = '''
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
'''

# *** THE MANAGEMENT CODE SECTION STARTS ***


def get_association_state():
    response = client.describe_client_vpn_endpoints(
        ClientVpnEndpointIds=[
            CLIENT_VPN_ENDPOINT_ID,
        ]
    )
    if len(response['ClientVpnEndpoints']) > 0:
        return response['ClientVpnEndpoints'][0]['Status']['Code']
    else:
        raise Exception("No existing client vpn endpoint found.")


# This function returns True if the endpoint is associated with the target network, vice versa.
def is_associated():
    state = get_association_state()
    if state == "pending-associate":  # When the subnet is NOT associated
        return False
    elif state == "available":  # When the subnet is associated
        return True
    # the possibility of an endpoint neither assiciated nor available.(Unexpected state)
    else:
        raise Exception("An unexpected state detected.")


def associate_target_network() -> None:
    response = client.associate_client_vpn_target_network(
        ClientVpnEndpointId=CLIENT_VPN_ENDPOINT_ID,
        SubnetId=SUBNET_ID,
    )
    if response["Status"]["Code"] != 'associating':
        raise Exception("Unexpected association state detected : {}".format(
            response['Status']['Code']))


def create_internet_routing_rule() -> None:
    response = client.create_client_vpn_route(
        ClientVpnEndpointId=CLIENT_VPN_ENDPOINT_ID,
        # The CIDR block that allows the traffic in and out of the public internet.
        DestinationCidrBlock='0.0.0.0/0',
        TargetVpcSubnetId=SUBNET_ID,
    )
    if response['Status']['Code'] != 'creating':
        raise Exception("Unexpected state detected after creating the route : {}".format(
            response['Status']['Code']))


def get_current_association_id():
    response = client.describe_client_vpn_target_networks(
        ClientVpnEndpointId=CLIENT_VPN_ENDPOINT_ID
    )
    if len(response['ClientVpnTargetNetworks']) > 0:
        return response['ClientVpnTargetNetworks'][0]['AssociationId']
    else:
        raise Exception(
            "No association ID found, probably there is no terget network associated right now.")


def disassociate_target_network() -> None:
    associationId = get_current_association_id()
    response = client.response = client.disassociate_client_vpn_target_network(
        ClientVpnEndpointId=CLIENT_VPN_ENDPOINT_ID,
        AssociationId=associationId,
    )
    if response['Status']['Code'] != 'disassociating':
        raise Exception("Unexpected status detected after disassociation : {}".format(
            response['Status']['Code']))


def turn_on() -> None:
    print(
        f"Associating the target subnet({SUBNET_ID}) and creating the new route(0.0.0.0/0).")
    print("... ... ...")
    associate_target_network()
    print("... ... ...")
    create_internet_routing_rule()
    print("Done.")


def get_status() -> None:
    print("Getting the association state of the client vpn endpoint : \n{}".format(
        CLIENT_VPN_ENDPOINT_ID))
    print("... ... ...")
    print("Currently, and state of association is : \n{}".format(
        get_association_state()))
    print("Done.")


def disassociate() -> None:
    print(
        f"Disassociating the target subnet({SUBNET_ID})\nfrom the client vpn endpoint({CLIENT_VPN_ENDPOINT_ID}).")
    print("... ... ...")
    disassociate_target_network()
    print("Done.")


def manage():
    # The function is executed when the user wants to manage an existing VPN service.
    global CLIENT_VPN_ENDPOINT_ID
    global SUBNET_ID
    commandInput = sys.argv[1]
    if commandInput == "status":
        get_status()
    elif commandInput == "off":
        disassociate()
    elif commandInput == "on":
        turn_on()
    elif commandInput == "help":
        print(HELP_SCRIPT)
    else:
        raise Exception(
            f"No such command as \"{commandInput}\" is available. Please check you input and try again.\n{HELP_SCRIPT}")

# *** THE MANAGEMENT CODE SECTION ENDS ***
# *** THE DEPLOYMENT CODE SECTION STARTS ***


def get_user_settings():
    global USER_SETTINGS
    USER_SETTINGS = {
        'friendlyName': '',
        'isSplitTunneled': False,
        'region': ''
    }
    print("Getting user settings...")
    friendlyName = input(
        "Please give your new VPN Service a friendly name:\n[Default: auto-generated random characters]> ")
    if friendlyName == '':
        print("Empty string detected! Your VPN friendly name is now:")
        friendlyName = ''.join(random.SystemRandom().choice(
            string.ascii_letters + string.digits) for _ in range(10))
        print(friendlyName)
    else:
        print("Your current VPN friendly name is:\n{}".format(friendlyName))
    USER_SETTINGS['friendlyName'] = friendlyName

    isSplitTunneled = input(
        "Do you want to enable split tunnel for your VPN?\n[Default: Nn] <Yy or Nn> ").capitalize()
    while True:
        if isSplitTunneled == 'Y':
            USER_SETTINGS['isSplitTunneled'] = True
            print("The VPN will be split-tunnel enabled.")
            break
        elif isSplitTunneled == 'N':
            USER_SETTINGS['isSplitTunneled'] = False
            print("The VPN will be split-tunnel disabled.")
            break
        elif isSplitTunneled == '':
            USER_SETTINGS['isSplitTunneled'] = False
            print("The VPN will be split-tunnel disabled as default.")
            break
        else:
            print("Unrecognized input, please try again!")
            isSplitTunneled = input(
                "Do you want to enable split tunnel for your VPN?\n[Default: Nn] <Yy or Nn> ").capitalize()

    print("The following AWS regions support Client VPN Endpoint:")
    availableRegions = '''
    1. US East (N. Virginia)
    2. US East (Ohio)
    3. US West (N. California)
    4. US West (Oregon)
    5. Asia Pacific (Mumbai)
    6. Asia Pacific (Seoul)
    7. Aisa Pacific (Singapore)
    8. Aisa Pacific (Sydney)
    9. Asia Pacific (Tokyo)
    10. Canada (Central)
    11. Europe (Frankfurt)
    12. Europe (Ireland)
    13. Europe (London)
    14. Europe (Stockholm)
    '''
    regionsMapping = [
        "",
        "us-east-1",
        "us-east-2",
        "us-west-1",
        "us-west-2",
        "ap-south-1",
        "ap-northeast-2",
        "ap-southeast-1",
        "ap-southeast-2",
        "ap-northeast-1",
        "ca-central-1",
        "eu-central-1",
        "eu-west-1",
        "eu-west-2",
        "eu-north-1"
    ]
    print(availableRegions)
    while True:
        regionNumber = input(
            "Please select one from the list above. Enter the number only:\n[no Default] <1-14> ")
        try:
            regionNumberInteger = int(regionNumber)
            if regionNumberInteger <= 14 and regionNumberInteger >= 1:
                USER_SETTINGS['region'] = regionsMapping[regionNumberInteger]
            else:
                raise Exception(
                    "Value ({}) not found. Please re-enter your region number.".format(regionNumber))
        except Exception as e:
            print(e)
        else:
            print("Your choice is {}".format(USER_SETTINGS['region']))
            break

    print("Please review your settings:\n {}".format(USER_SETTINGS))
    if input("Please press ENTER to proceed, any other key to abort.\n> ").capitalize() != "":
        print("Abort.")
        sys.exit(1)


def generate_credentials():
    # This function first clones https://github.com/openvpn/easy-rsa.git and generates certificates for both server and clients.
    # And saves it under the current directory.
    commandsToRun = [
        'cd '
        'git clone https://github.com/openvpn/easy-rsa.git',
        'cd easy-rsa/easyrsa3',
        './easyrsa init-pki',
        './easyrsa build-ca nopass',
        './easyrsa build-server-full server nopass',
        './easyrsa build-client-full client1.domain.tld nopass'
    ]

# def download_cloudformation_template():

# def deploy_cloudformation_template():

# def download_connection_profile():

# def modify_and_save_connection_profile():

# def save_the_setup_results():


# *** THE DEPLOYMENT CODE SECTION ENDS ***

if __name__ == "__main__":
    if len(sys.argv) > 1:  # To see if the command is present.
        try:
            # get_configuration()
            manage()
        except Exception as e:
            print("Errors occured.", file=sys.stderr)
            traceback.print_exc()
    else:  # manage the vpn when there is no commands or options.
        print("No commands or options detected in the command line. Let's setup a brand-new VPN service!")
        # Before we initiate the deployment sequence, we need to know the following parameters:
        # - the AWS region where the endpoint will be created. (no Default, mandatory)
        # - the friendly name of this vpn service. (Default: timestampt/UUID)
        # - if the vpn service should be split-tunnelled. (Default: non-split-tunnel)
        # The user will be prompted to speficy these parameters. The job is done within the following function:
        get_user_settings()
        try:
            generate_credentials()
            # download_cloudformation_template()
            # save the aws-generated private keys at the same time.
            # deploy_cloudformation_template()
            # download_connection_profile()
            # # Insert the generated credential into the .ovpn file.
            # modify_and_save_connection_profile()
            # save_the_setup_results()
        except Exception as e:
            print(
                "Errors occured during the deployment process.\n Program Exits.", file=sys.stderr)
            traceback.print_exc()
