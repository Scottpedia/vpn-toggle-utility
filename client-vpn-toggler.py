#!/usr/bin/env python3
import boto3
import os
import sys

client = boto3.client("ec2")

'''
So please leave these values below blank if you want to specify the ids with system environment variables. 
Otherwise, the values specified here would override the ones as environment variables.
'''
CLIENT_VPN_ENDPOINT_ID = ""
SUBNET_ID = ""
HELP_SCRIPT = '''
Usage: ./client-vpn-toggler command
The followings are the available commands of this utility and the descriptions for them:
    
      get-status : Get the current association state of the client vpn endpoint. 
       associate : Associate the specified client vpn endpoint with the target subnet.
    disassociate : Disassociate the target subnet from the client vpn endpoint.
            help : Display this help message.

Please note that the IDs for both client vpn enpoint and the target subnet are specified by defining the environment variables shown below:
    CLIENT_VPN_ENDPOINT_ID  
    SUBNET_ID
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


def main():
    global CLIENT_VPN_ENDPOINT_ID
    global SUBNET_ID
    try:
        if not CLIENT_VPN_ENDPOINT_ID:
            CLIENT_VPN_ENDPOINT_ID = os.environ['CLIENT_VPN_ENDPOINT_ID']
        if not SUBNET_ID:
            SUBNET_ID = os.environ['SUBNET_ID']
        # A KeyError will be raised if any of these values does not exist.
        if len(sys.argv) > 1:
            commandInput = sys.argv[1]
            if commandInput == "get-status":
                print("Getting the association state of the client vpn endpoint : \n{}".format(
                    CLIENT_VPN_ENDPOINT_ID))
                print("... ... ...")
                print("Currently, and state of association is : \n{}".format(
                    get_association_state()))
                print("Done.")
            elif commandInput == "associate":
                print(
                    f"Associating the client vpn endpoint({CLIENT_VPN_ENDPOINT_ID})\nwith the target subnet({SUBNET_ID}).")
                print("... ... ...")
                associate_target_network()
                print("Done.")
            elif commandInput == "disassociate":
                print(
                    f"Disassociating the target subnet({SUBNET_ID})\nfrom the client vpn endpoint({CLIENT_VPN_ENDPOINT_ID}).")
                print("... ... ...")
                disassociate_target_network()
                print("Done.")
            elif commandInput == "help":
                print(HELP_SCRIPT)
            else:
                raise Exception(
                    f"No such command as \"{commandInput}\" is available. Please check you input and try again.\n{HELP_SCRIPT}")
        else:
            raise Exception("No command specified.\n{}".format(HELP_SCRIPT))
        pass
    except KeyError:
        print("Please specify the IDs of your resources.\n{}".format(HELP_SCRIPT))
    except Exception as e:
        print("Errors occured.")
        print(e)


if __name__ == "__main__":
    main()
