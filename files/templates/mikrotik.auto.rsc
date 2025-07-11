/interface set ether1 comment="$PEERING_LAN_NAME_interface"
/interface set ether2 comment="$CLIENT_LAN_NAME_interface"
/interface set lo comment="$LOOPBACK_NAME_interface"

/ipv6/address/add address=$PEERING_LAN_IPV6_IP_ADDRESS/$PEERING_LAN_IPV6_PREFIX_LENGTH interface=ether2
/ip/address/add address=$CLIENT_LAN_IPV4_IP_ADDRESS/$CLIENT_LAN_IPV4_PREFIX_LENGTH interface=ether3
/ip/address/add address=$LOOPBACK_IPV4_IP_ADDRESS/$LOOPBACK_IPV4_PREFIX_LENGTH interface=lo

/routing/bgp/instance/add as=$BGP_ASN router-id=$BGP_ROUTER_ID
$BGP_NEIGHBORS