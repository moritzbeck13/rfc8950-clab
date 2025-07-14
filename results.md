# Findings
- Routers:
	- Arista EOS sends ICMP messages from the management interface if it is in the same VRF, leaking the management IP address.
	- Cisco IOS XE only supports a very limited subset of SAFIs.
	- Cisco IOS XR sends ICMP messages from the management interface if it is in the same VRF, leaking the management IP address.
	- Cisco IOS XR prefers link-local next-hops while not providing a way to configure this behaviour. This can cause connectivity issues in cases where `next-hop self` only updates the GUA.
- Route Servers:
	- BIRD has limited functionality for configuring the next-hop type preference.
	- ExaBGP cannot modify the route table.
	- GoBGP cannot modify the route table.
	- OpenBGPD does not install routes into the FIB yet.
- Operating Systems:
	- Linux can install IPv4 routes with an IPv6 next-hop only via Netlink and not e.g. `ip route add`. It can forward IPv4 packets on IPv6 interfaces natively.
	- OpenBSD cannot install IPv4 routes with an IPv6 next-hop. It is unclear if it can forward IPv4 packets on IPv6 interfaces.

# Conclusion
- almost all major vendors support RFC 8950, many smaller ones do not yet
- all vendors that support it do so fully and properly
- not all vendors support RFC 2545 from 1999 (!) properly
- the actual implementation-specific behaviour still differs in almost all aspects from vendor to vendor
- unintuitively, while route servers offer at least some configurability, at least to my knowledge no routers do
- there is a IETF IDR WG draft to address the behaviour and configurability issues

# Further Resources
- https://en.wikipedia.org/wiki/List_of_open-source_routing_platforms
- https://github.com/Exa-Networks/exabgp/wiki/Other-OSS-BGP-implementations
- https://elegantnetwork.github.io/posts/comparing-open-source-bgp-stacks/
- https://datatracker.ietf.org/doc/draft-ietf-idr-linklocal-capability/

# Legend
- ✅ = tested, working
- ❎ = tested, not working but expected behaviour
- ❌ = tested, not working
- ❗ = tested, limited functionality
- ❔ = not tested, missing functionality

# Peering
Note: Operating Systems rely on a Route Server for peering. Therefore they are not included in this category.

## Overview
| <br>Type | <br>Vendor | <br>Platform | Arista<br>EOS | Cisco<br/>IOS XE | Cisco<br/>IOS XR | Cisco<br/>NX-OS | Extreme<br> | Huawei<br> | Juniper<br>Junos OS | Mikrotik<br>RouterOS | Nokia<br/>SR Linux | Nokia<br/>SR OS | <br>BIRD 1 | <br>BIRD 2 | <br>BIRD 3 | <br>FRR | <br>OpenBGPD | <br>Notes |
|------------------|--------------|--------------|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|---------------------------------------------------------------|
| **Router**       | **Arista**   | **EOS**      | ✅ | ❗ | ✅ | ❔ | ❔ | ❔ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ |                                                               |
|                  | **Cisco**    | **IOS XE**   | ❗ | ❗ | ❗ | ❗ | ❗ | ❗ | ❗ | ❗ | ❗ | ❗ | ❌ | ❗ | ❗ | ❗ | ❗ | Cisco IOS XE only supports a very limited subset of SAFIs[^1] |
|                  | **Cisco**    | **IOS XR**   | ✅ | ❗ | ✅ | ❔ | ❔ | ❔ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ |                                                               |
|                  | **Cisco**    | **NX-OS**    | ❔ | ❗ | ❔ | ❔ | ❔ | ❔ | ❔ | ❔ | ❔ | ❔ | ❌ | ❔ | ❔ | ❔ | ❔ |                                                               |
|                  | **Extreme**  |              | ❔ | ❗ | ❔ | ❔ | ❔ | ❔ | ❔ | ❔ | ❔ | ❔ | ❌ | ❔ | ❔ | ❔ | ❔ |                                                               |
|                  | **Huawei**   |              | ❔ | ❗ | ❔ | ❔ | ❔ | ❔ | ❔ | ❔ | ❔ | ❔ | ❌ | ❔ | ❔ | ❔ | ❔ |                                                               |
|                  | **Juniper**  | **Junos OS** | ✅ | ❗ | ✅ | ❔ | ❔ | ❔ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ |                                                               |
|                  | **Mikrotik** | **RouterOS** | ✅ | ❗ | ✅ | ❔ | ❔ | ❔ | ✅ | ✅ | ✅ | ✅ | ❌ | ❔ | ❔ | ❔ | ❔ |                                                               |
|                  | **Nokia**    | **SR Linux** | ✅ | ❗ | ✅ | ❔ | ❔ | ❔ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ |                                                               |
|                  | **Nokia**    | **SR OS**    | ✅ | ❗ | ✅ | ❔ | ❔ | ❔ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ |                                                               |
| **Route Server** |              | **BIRD 1**   | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | BIRD 1 will not support RFC 8950, use later versions instead  |
|                  |              | **BIRD 2**   | ✅ | ❗ | ✅ | ❔ | ❔ | ❔ | ✅ | ❔ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ |                                                               |
|                  |              | **BIRD 3**   | ✅ | ❗ | ✅ | ❔ | ❔ | ❔ | ✅ | ❔ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ |                                                               |
|                  |              | **FRR**      | ✅ | ❗ | ✅ | ❔ | ❔ | ❔ | ✅ | ❔ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ |                                                               |
|                  |              | **OpenBGPD** | ✅ | ❗ | ✅ | ❔ | ❔ | ❔ | ✅ | ❔ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ |                                                               |

## Advertising
Wich types of IPv6 addresses are included in the BGP next-hop field?
- GUA = global unique adress
- LLA = link local address
- :: = zero/null/unspecified address

| Type             | Vendor       | Platform     | GUA | LLA | :: | Notes                                         |
|------------------|--------------|--------------|-----|-----|----|-----------------------------------------------|
| **Router**       | **Arista**   | **EOS**      | ✅  | ❌  | ❌ | RFC 2545 non-compliant                        |
|                  | **Cisco**    | **IOS XE**   | ❔  | ❔  | ❔ |                                               |
|                  | **Cisco**    | **IOS XR**   | ✅  | ✅  | ❎ |                                               |
|                  | **Cisco**    | **NX-OS**    | ❔  | ❔  | ❔ |                                               |
|                  | **Extreme**  |              | ❔  | ❔  | ❔ |                                               |
|                  | **Huawei**   |              | ❔  | ❔  | ❔ |                                               |
|                  | **Juniper**  | **Junos OS** | ✅  | ✅  | ❎ |                                               |
|                  | **Mikrotik** | **RouterOS** | ✅  | ❌  | ❌ | RFC 2545 non-compliant                        |
|                  | **Nokia**    | **SR Linux** | ✅  | ❌  | ❌ | RFC 2545 non-compliant                        |
|                  | **Nokia**    | **SR OS**    | ✅  | ❌  | ❌ | RFC 2545 non-compliant                        |
| **Route Server** |              | **BIRD 1**   | ❔  | ❔  | ❔ |                                               |
|                  |              | **BIRD 2**   | ✅  | ✅  | ❎ |                                               |
|                  |              | **BIRD 3**   | ✅  | ✅  | ❎ |                                               |
|                  |              | **FRR**      | ✅  | ✅  | ❎ |                                               |
|                  |              | **OpenBGPD** | ✅  | ❌  | ❌ | RFC 2545 non-compliant                        |

## Receiving
Wich type of IPv6 address is installed in the FIB? Is this behaviour configurable?
- `GUA` = global unique adress
- `LLA` = link local address

| Type             | Vendor       | Platform     | Preference | Configurable | Notes                                                                                        |
|------------------|--------------|--------------|------------|--------------|----------------------------------------------------------------------------------------------|
| **Router**       | **Arista**   | **EOS**      | `GUA`      | ❌           |                                                                                              |
|                  | **Cisco**    | **IOS XE**   | ❔         | ❔           |                                                                                              |
|                  | **Cisco**    | **IOS XR**   | `LLA`      | ❌           |                                                                                              |
|                  | **Cisco**    | **NX-OS**    | ❔         | ❔           |                                                                                              |
|                  | **Extreme**  |              | ❔         | ❔           |                                                                                              |
|                  | **Huawei**   |              | ❔         | ❔           |                                                                                              |
|                  | **Juniper**  | **Junos OS** | `GUA`      | ❌           |                                                                                              |
|                  | **Mikrotik** | **RouterOS** | `GUA`      | ❌           |                                                                                              |
|                  | **Nokia**    | **SR Linux** | `GUA`      | ❌           |                                                                                              |
|                  | **Nokia**    | **SR OS**    | `GUA`      | ❌           |                                                                                              |
| **Route Server** |              | **BIRD 1**   | ❔         | ❔           |                                                                                              |
|                  |              | **BIRD 2**   | `GUA`      | ❗           | `next hop prefer global` within channel, currently only used for resolving indirect gateways |
|                  |              | **BIRD 3**   | `GUA`      | ❗           | `next hop prefer global` within channel, currently only used for resolving indirect gateways |
|                  |              | **FRR**      | `LLA`      | ✅           | `set ipv6 next-hop prefer-global` within route-map                                           |
|                  |              | **OpenBGPD** | `GUA`      | ❔           |                                                                                              |

# Forwarding
Note: Route Servers rely on an Operating System for forwarding. Therefore they are not included in this category.

## Overview
| Type       | Vendor       | Platform     | IPv4 routes with IPv6 next-hop | IPv4 packets on IPv6 interface | Notes                                                       |
|------------|--------------|--------------|--------------------------------|--------------------------------|-------------------------------------------------------------|
| **Router** | **Arista**   | **EOS**      | ✅                             | ✅                             | `interface * ip routing address required disabled`          |
|            | **Cisco**    | **IOS XE**   | ❔                             | ❔                             |                                                             |
|            | **Cisco**    | **IOS XR**   | ✅                             | ✅                             | `interface * ipv4 forwarding-enable`                        |
|            | **Cisco**    | **NX-OS**    | ❔                             | ❔                             |                                                             |
|            | **Extreme**  |              | ❔                             | ❔                             |                                                             |
|            | **Huawei**   |              | ❔                             | ❔                             |                                                             |
|            | **Juniper**  | **Junos OS** | ✅                             | ✅                             | `set interfaces * unit * family inet`                       |
|            | **Mikrotik** | **RouterOS** | ✅                             | ✅                             |                                                             |
|            | **Nokia**    | **SR Linux** | ✅                             | ✅                             | `network-instance * ip-forwarding receive-ipv4-check false` |
|            | **Nokia**    | **SR OS**    | ✅                             | ✅                             | `router * interface * ipv6 forward-ipv4-packets`            |
| **OS**     |              | **Linux**    | ✅                             | ✅                             | no special configuration needed. only via Netlink, not CLI  |
|            |              | **OpenBSD**  | ❌                             | ❔                             | OpenBGPD does not install routes into the FIB yet[^3]       |

## ICMP
The IPv4 address of which interface is used for sending ICMP messages?
- `lo` = Loopback interface
- `mgmt` = Management interface
- `out` = interface the packet will be forwarded out of

| Type       | Vendor       | Platform     | Interface | Notes                                |
|------------|--------------|--------------|-----------|--------------------------------------|
| **Router** | **Arista**   | **EOS**      | `mgmt`    | if mgmt interface is in the same VRF |
|            | **Cisco**    | **IOS XE**   | ❔        |                                      |
|            | **Cisco**    | **IOS XR**   | `mgmt`    | if mgmt interface is in the same VRF |
|            | **Cisco**    | **NX-OS**    | ❔        |                                      |
|            | **Extreme**  |              | ❔        |                                      |
|            | **Huawei**   |              | ❔        |                                      |
|            | **Juniper**  | **Junos OS** | `lo`      |                                      |
|            | **Mikrotik** | **RouterOS** | `lo`      |                                      |
|            | **Nokia**    | **SR Linux** | `out`     |                                      |
|            | **Nokia**    | **SR OS**    | `out`     |                                      |
| **OS**     |              | **Linux**    | `lo`      |                                      |
|            |              | **OpenBSD**  | ❔        |                                      |

[^1]: https://www.cisco.com/c/en/us/td/docs/routers/ios/config/17-x/ip-routing/b-ip-routing/m-support-bgp-vpn-evpn-nexthop.pdf
[^2]: https://help.mikrotik.com/docs/spaces/ROS/pages/28606515/Routing+Protocol+Overview
[^3]: https://github.com/openbgpd-portable/openbgpd-openbsd/commit/f9365c08c05927510280d3b077392615c5b96026