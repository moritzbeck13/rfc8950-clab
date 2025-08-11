# Project Structure
- [acls](acls): ACL examples for different vendors
- [clab](clab): source code for containerlab orchestration
- [files](files): supplementary files for containerlab
- [results](results): results for IPv4 and IPv6 with before and after tests
- [main.py](main.py): topology setup and test cases
- [viewport-containerlab-peering_lan.svg](viewport-containerlab-peering_lan.svg): example topology used for this setup

# Location
There are two possible locations in the network where the ACL can be applied. Each scenario has its own advantages and disadvantages.
1. on the egress interface towards the route server
	- advantages:
		- legitimate customer traffic is never touched
		- ACL needs to be applied only on the route server port
	- disadvantages:
		- illegitimate traffic crosses the whole network before being discarded
		- customer routers are still succeptible, only the route server is protected
2. on the ingress interface towards each customer router
	- advantages:
		- illegitimate traffic is discarded as soon as it enters the network
		- customer routers are protected aswell
	- disadvantages:
		- mistakes can lead to legitimate customer traffic being discarded
		- ACL needs to be applied on each customer port

# Effect
Here is a pseudo code implementation of the ACL with explanations for each rule. It assumes that scenario 1 was chosen. The example ACLs are based on this aswell.
- IPv4:
	```
	// allow ping/traceroute within the peering LAN
	10 allow icmp peering_lan -> peering_lan

	// allow BGP (179) as the source within the peering LAN
	30 allow tcp peering_lan:bgp -> peering_lan:*
	// allow BGP (179) as the destination within the peering LAN
	31 allow tcp peering_lan:* -> peering_lan:bgp
	
	// allows BFD (3784) as the source within the peering LAN
	40 allow udp peering_lan:bfd -> peering_lan:*
	// allow BFD (3784) as the destination within the peering LAN
	41 allow udp peering_lan:* -> peering_lan:bfd

	// drop everything else
	50 drop any any
	```
- IPv6:
	```
	// allow ping/traceroute within the peering LAN
	10 allow icmp peering_lan -> peering_lan
	// allow ping/traceroute from the peering LAN to link-local
	11 allow icmp peering_lan -> link-local
	// allow neighbor discovery from the peering LAN
	12 allow icmp peering_lan -> multicast

	// allow ping/traceroute from link-local to the peering LAN
	20 allow icmp link-local -> peering_lan
	// allow ping/traceroute within link-local
	21 allow icmp link-local -> link-local
	// allow neighbor discovery from link-local
	22 allow icmp link-local -> multicast

	// allow BGP (179) as the source within the peering LAN
	30 allow tcp peering_lan:bgp -> peering_lan:*
	// allow BGP (179) as the destination within the peering LAN
	31 allow tcp peering_lan:* -> peering_lan:bgp
	
	// allows BFD (3784) as the source within the peering LAN
	40 allow udp peering_lan:bfd -> peering_lan:*
	// allow BFD (3784) as the destination within the peering LAN
	41 allow udp peering_lan:* -> peering_lan:bfd

	// drop everything else
	50 drop any any
	```

This implies that BGP/BFD is not used over IPv6 link-local addresses.

# Test Cases
In this setup, scenario 1 was used for testing. The test cases include before and after tests (to make sure that the ACL did actually make a difference). 
From a host on a network outside of the peering LAN...
- the following tests were conducted:
	- open a raw TCP socket on the route server on port 179 (BGP) from a customer router
	- ping the route server from a customer router using ICMP
	- traceroute to the route server from a customer router and make sure that the hops are correct
- the following tests were **not** conducted:
	- customer to customer connectivitiy
		- in scenario 1, the ACL should never come into contact with any legitimate customer traffic
		- therefore it makes no sense to test for this here
	- open a raw UDP socket on the route server on port 3784 (BFD) from a customer router
		- detecting if a UDP port is open or closed is not trivial
		- since the syntax is the same for TCP ports, it is assumed to also work the same
		- therefore it is implicitely tested through the BGP test
	- ARP
		- implicitely tested through general IPv4 connectivity
	- IPv6 neighbor discovery
		- implicitely tested through general IPv6 connectivity

# Adjustments
The ACL was originally written for the DE-CIX Frankfurt peering LAN. Therefore you **MUST** adjust the address range to your location accordingly. This also means that the provided examples only serve as a common starting point. It is entirely possible, if not likely, that the ACL does not fit your use case as-is. Depending on what scenario you chose before, you **MAY** and in some cases even **MUST** make some further adjustments.
1. If you chose to apply the ACL on the egress interface towards the route server, you **MAY** use them as-is. You **MAY** also narrow down the source and destination address range to just the route server, because no other legitimate traffic should ever flow through that interface. In that case you also **MUST** duplicate every rule to allow the route server to be both on the sending and the receiving side. You **SHALL NOT** narrow down the address range to just the route server for both the source and destination in the same rule. Otherwise the route server will be isolated. For example, `allow peering_lan -> peering_lan` becomes:
	1. `allow peering_lan -> route_server`
	2. `allow route_server -> peering_lan`
2. If you chose to apply the ACL on the ingress interface towards each customer router, you **MUST** adjust it as follows. You **MAY** additionally narrow down the adress range as described above.
	1. First, remove the `drop any -> any` rule. Otherwise all customer traffic will be discarded.
	2. Then, allow traffic that is both originating from and destined to outside the peering LAN, while discarding traffic that is originating from or destined to the peering LAN. You can choose one of the following options, depending on if your vendor supports negation in ACLs:
		-	1. predefined rules
			2. `drop peering_lan -> any`
			3. `drop any -> peering_lan`
			4. `allow any -> any`
		-	1. predefined rules
			2. `allow !peering_lan -> !peering_lan`
			3. `drop any -> any`

For both scenario, ICMP/ICMPv6 **MAY** be narrowed down to types used in `ping`/`traceroute` for unicast addresses. IPv6 unicast might additionally need duplicate address detection (DAD) and path MTU discovery (PMTUD). For IPv6 multicast, neighbor discovery (ND) is needed aswell, but not on the whole multicast address range.

# Limitations
- In any case, source IP spoofing is still possible if the customer routers do not implement any mitigation techniques, e.g. reverse path forwarding (RPF). Therefore it is also recommended to apply a rate limit with a sensible maximum bandwith. This should happen on a per customer/address basis in order to not affect other customers if one is misbehaving.
- There are also some special cases where, depending on your setup and which option you chose, it is not guaranteed that the ACL is sufficiently effective. These include, but are not limited to:
	- IPv4 mapped IPv6 addresses
	- adressless forwarding on an interface of a different address family
- Be careful to not apply the ACL on layer 2, as this might result in all frames getting dropped by default.
- If you use the peering LAN for your management traffic (you really shouldn't), this will cause further issues.

# Notes
- General:
	1. Using `traceroute` in ICMP mode (`-I`) for testing fails for some unkown reason, but only for IPv6 and only on the first hop. This happens regardless of the ACL.
	2. When using `traceroute`'s default UDP mode, replies to different traceroutes that are running simultaniously might get mixed up. This is because Python subprocesses are not network isolated against each other by default. This happens regardless of the ACL.
	3. Due to limitations of some vendors, the IPv4 and IPv6 ACLs cannot be tested at the same time automatically. Change [main.py#L55-L56](main.py#L55-L56), [main.py#L142](main.py#L142) and [main.py#L163](main.py#L163) inbetween tests accordingly.
- Cisco IOS XR:
	1. In order to test Cisco IOS XR, the XRD image is used. As this is a control plane only image, the data plane is handled by the underlying virtualization host, which the image has no control over anymore. This means that an ACL applied on an egress is not effective. To test the ACL, it is therefore applied on the ingress, since this is the only place where the traffic actually hits the image.
- Juniper Junos OS:
	1. Depending on what type of interface (`ethernet-switching`, `inet`/`inet6`, `mpls`, `vpls` etc.) you apply the ACL to, its syntax might vary a lot or not be compatible at all.
	2. Deployment of the config fails silently if the `inet` and `inet6` address families are configured for a BGP peer simultaneously (MP-BGP) and the peer address is of type `inet6`. Either disable the `inet` family or configure `bgp family inet unicast local-ipv4-address`. On the other hand, if the peer address is of type `inet`, the IPv6 next hop will be the IPv4 mapped address and not the address of the `inet6` interface.
- Nokia SROS:
	1. Deployment of the config fails silently if using MD CLI and `filter md-auto-id filter-id-range` is not configured.