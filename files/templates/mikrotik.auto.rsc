/interface ethernet
set ether1 comment=$PEERING_LAN_NAME_interface
set ether2 comment=$CLIENT_LAN_NAME_interface
/routing bgp instance
add as=$BGP_ASN name=bgp-instance-1 router-id=$BGP_ROUTER_ID
/routing bgp template
set default afi=ip input.filter=default_accept_filter output.filter-chain=accept_$CLIENT_LAN_NAME_filter .network=$CLIENT_LAN_NAME_address_list
/ip address
add address=$CLIENT_LAN_IPV4_IP_ADDRESS/$CLIENT_LAN_IPV4_PREFIX_LENGTH interface=ether3
add address=$LOOPBACK_IPV4_IP_ADDRESS/$LOOPBACK_IPV4_PREFIX_LENGTH interface=lo
/ip firewall address-list
add address=$CLIENT_LAN_IPV4_NETWORK_ADDRESS/$CLIENT_LAN_IPV4_PREFIX_LENGTH list=$CLIENT_LAN_NAME_address_list
/ipv6 address
add address=$PEERING_LAN_IPV6_IP_ADDRESS/$PEERING_LAN_IPV6_PREFIX_LENGTH interface=ether2
/routing bgp connection
$BGP_NEIGHBORS
/routing filter rule
add chain=accept_$CLIENT_LAN_NAME_filter rule="if ( dst == $CLIENT_LAN_IPV4_NETWORK_ADDRESS/$CLIENT_LAN_IPV4_PREFIX_LENGTH ) { accept; } else { reject; }"
add chain=default_accept_filter rule=accept