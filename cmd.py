import boto3
import os

client = boto3.client("ec2")

CLIENT_VPN_ENDPOINT_ID = ''
SUBNET_ID = ''

def is_associated(): #This function returns True if the endpoint is associated with the target network, vice versa.
    response = client.describe_client_vpn_endpoints(
        ClientVpnEndpointIds = [
            CLIENT_VPN_ENDPOINT_ID,
        ]
    )
    if len(response['ClientVpnEndpoints']) > 0:
        if response['ClientVpnEndpoints'][0]['Status']['Code'] == "pending-associate": #When the subnet is NOT associated
            return False
        elif response['ClientVpnEndpoints'][0]['Status']['Code'] == "available": #When the subnet is associated 
            return True 
        else: #the possibility of an endpoint neither assiciated or available.(Unexpected state)
            raise Exception("An unexpected state detected.")
    else:
        raise Exception("No existing client vpn endpoint found.")
        
def associate_target_network() -> None:
    response = client.associate_client_vpn_target_network(
        ClientVpnEndpointId = CLIENT_VPN_ENDPOINT_ID,
        SubnetId = SUBNET_ID,
    )
    if response["Status"]["Code"] != 'associating':
        raise Exception("Unexpected association state detected : {}".format(response['Status']['Code']))

def create_internet_routing_rule() -> None:
    response = client.create_client_vpn_route(
        ClientVpnEndpointId = CLIENT_VPN_ENDPOINT_ID,
        DestinationCidrBlock = '0.0.0.0/0', #The CIDR block that allows the traffic in and out of the public internet.
        TargetVpcSubnetId = SUBNET_ID,
    )
    if response['Status']['Code'] != 'creating':
        raise Exception("Unexpected state detected after creating the route : {}".format(response['Status']['Code']))

def get_current_association_id():
    response = client.describe_client_vpn_target_networks(
        ClientVpnEndpointId = CLIENT_VPN_ENDPOINT_ID
    )
    if len(response['ClientVpnTargetNetworks']) > 0:
        return response['ClientVpnTargetNetworks'][0]['AssociationId']
    else:
        raise Exception("No association ID found, probably there is no terget network associated right now.")

def disassociate_target_network() -> None:
    associationId = get_current_association_id()
    response = client.response = client.disassociate_client_vpn_target_network(
        ClientVpnEndpointId = CLIENT_VPN_ENDPOINT_ID,
        AssociationId = associationId,
    )
    if response['Status']['Code'] != 'disassociating':
        raise Exception("Unexpected status detected after disassociation : {}".format(response['Status']['Code']))

def main():

    try:
        CLIENT_VPN_ENDPOINT_ID = os.environ['ENDPOINT_ID']
        SUBNET_ID = os.environ['SUBNET_ID']
        # A KeyError will be raised if any of these values does not exist.

        pass
    except Exception as e:
        print("Errors occured.")
        print(e)

if __name__ == "__main__":
    main()