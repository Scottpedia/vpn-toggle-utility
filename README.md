# vpn-toggle-utility
The python scripts used to basically turn on and off the client vpn service on aws.

----------------------------------------------

```
Usage: ./client-vpn-toggler command
The followings are the available commands of this utility and the descriptions for them:
    
      get-status : Get the current association state of the client vpn endpoint. 
       associate : Associate the specified client vpn endpoint with the target subnet.
    disassociate : Disassociate the target subnet from the client vpn endpoint.
            help : Display this help message.
Please note that the IDs for both client vpn enpoint and the target subnet are specified by defining the environment variables shown below:
    CLIENT_VPN_ENDPOINT_ID  
    SUBNET_ID
```
