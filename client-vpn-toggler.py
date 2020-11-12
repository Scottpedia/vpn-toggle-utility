#!/usr/bin/env python3
import boto3
import os
import sys

client = boto3.client("ec2")

'''
So please leave these values below blank if you want to specify the ids with system environment variables.
Otherwise, the values specified here would override the environment variables.
'''
CLIENT_VPN_ENDPOINT_ID = ""
SUBNET_ID = ""
HELP_SCRIPT = '''
Usage: ./client-vpn-manager [command] -f [the_config_file]
The python script to deploy and manage the vpn service based on AWS Client VPN Endpoints.

NOTE: PLEASE HAVE YOUR AWS CLI SETUP WITH YOUR AWS ACCOUNT BEFORE YOU RUN THIS SCRIPT.
      THE SCRIPT WILL NOT RUN WITHOUT AN AWS ACCOUNT SETUP WITH THE CLI.

    Please run the script without any options or commands to setup a new vpn service.
    You will be asked of the AWS Region in which you want to deploy your VPN Endpoint.

    To manage the existing VPN Endpoints, please use the following commands:
    status  :   Output the current status of the specified VPN Endpoint.
    on      :   Turn on the VPN
    off     :   Turn off the VPN
    toggle  :   Toggle the VPN

    -f [Filename] (Optional)
    You can use the optional -f flag to specify the file which contains the profile of a specific VPN deployment.
    Thus you can have multiple deployments active at the same time, and manage each of them with its profile.
    If the file is not speficied, the program will look for one under the current working directory.

'''


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
    print(f"Associating the target subnet({SUBNET_ID}) and creating the new route(0.0.0.0/0).")
    print("... ... ...")
    associate_target_network()
    print("... ... ...")
    create_internet_routing_rule()
    print("Done.")

def get_status() -> None:
    print("Getting the association state of the client vpn endpoint : \n{}".format(CLIENT_VPN_ENDPOINT_ID))
    print("... ... ...")
    print("Currently, and state of association is : \n{}".format(
        get_association_state()))
    print("Done.")

def associate() -> None:
    print(f"Associating the client vpn endpoint({CLIENT_VPN_ENDPOINT_ID})\nwith the target subnet({SUBNET_ID}).")
    print("... ... ...")
    associate_target_network()
    print("Done.")

def create_new_route() -> None:
    print("Creating new route(0.0.0.0/0) for the endpoint.")
    print("... ... ...")
    create_internet_routing_rule()
    print("Done.")

def disassociate() -> None:
    print(f"Disassociating the target subnet({SUBNET_ID})\nfrom the client vpn endpoint({CLIENT_VPN_ENDPOINT_ID}).")
    print("... ... ...")
    disassociate_target_network()
    print("Done.")

def turn_off() -> None:
    disassociate()

if __name__ == "__main__":
    if ACTION is 1: #setup the vpn
        generate_credentials()
        download_cloudformation_template()
        deploy_cloudformation_template() # save the aws-generated private keys at the same time.
        download_connection_profile()
        modify_and_save_connection_profile() # Insert the generated credential into the .ovpn file.
        save_the_setup_results()
    elif ACTION is 2: #manage the vpn
        
