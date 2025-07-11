# Findings
- Routers:
	- Arista answers ICMP messages from their management interface if it is in the same VRF, leaking the management IP address.
	- Cisco IOS XE only supports a very limited subset of SAFIs.
	- Cisco IOS XR answers ICMP messages from their management interface if it is in the same VRF, leaking the management IP address.
- Route Servers:
	- BIRD has limited functionality for configuring the next-hop type preference
	- ExaBGP cannot modify the route table
	- GoBGP cannot modify the route table
	- Juniper offers specialized route server implemenations
	- OpenBGPD cannot modify the route table yet
	- Quagga has not been updated since 2018, which predates RFC 8950
	- XORP has not been updated since 2012, which predates RFC 8950
	- Zebra has not been updated since 2005, which predates RFC 8950
- Operating Systems:
	- Linux can install IPv4 routes with an IPv6 next hop and forward IPv4 packets on IPv6 interfaces natively.
	- OpenBSD cannot install IPv4 routes with an IPv6 next hop. It is unclear if it can forward IPv4 packets on IPv6 interfaces.

# Conclusion
- almost all major vendors support RFC 8950, many smaller ones do not yet
- all vendors that support it do so fully and properly
- not all vendors properly support RFC 2545 from 1999 (!)
- the actual implementation-specific behaviour still differs in almost all aspects from vendor to vendor
- unintuitively, while route servers offer at least some configurability, at least to my knowledge no routers do
- there is a IETF IDR WG draft to address the behaviour and configurability issues

# Further Resources
- https://en.wikipedia.org/wiki/List_of_open-source_routing_platforms
- https://github.com/Exa-Networks/exabgp/wiki/Other-OSS-BGP-implementations
- https://elegantnetwork.github.io/posts/comparing-open-source-bgp-stacks/
- https://datatracker.ietf.org/doc/draft-ietf-idr-linklocal-capability/

# Peering
Note: Operating Systems rely on a Route Server for peering. Therefore they are not included in this category.

## Overview
| Type              | Vendor             | Arista | Cisco IOS XE | Cisco IOS XR | Cisco NX-OS | Extreme | Huawei | Juniper | Mikrotik | Nokia SR Linux | Nokia SR OS | BIRD 1 | BIRD 2 | BIRD 3 | FRR | OpenBGPD | Notes                                                         |
|------------------ |--------------------|--------|--------------|--------------|-------------|---------|--------|---------|----------|----------------|-------------|--------|--------|--------|-----|----------|---------------------------------------------------------------|
| **Routers**       | **Arista**         | ✅     | ❗          | ✅           | ❔         | ❔      | ❔    | ✅      | ❔      | ✅             | ✅         | ❌     | ✅    | ✅     | ✅ | ✅       |                                                               |
|                   | **Cisco IOS XE**   | ❗     | ❗          | ❗           | ❗         | ❗      | ❗    | ❗      | ❗      | ❗             | ❗         | ❌     | ❗    | ❗     | ❗ | ❗       | Cisco IOS XE only supports a very limited subset of SAFIs[^1] |
|                   | **Cisco IOS XR**   | ✅     | ❗          | ✅           | ❔         | ❔      | ❔    | ✅      | ❔      | ✅             | ✅         | ❌     | ✅    | ✅     | ✅ | ✅       |                                                               |
|                   | **Cisco NX-OS**    | ❔     | ❗          | ❔           | ❔         | ❔      | ❔    | ❔      | ❔      | ❔             | ❔         | ❌     | ❔    | ❔     | ❔ | ❔       |                                                               |
|                   | **Extreme**        | ❔     | ❗          | ❔           | ❔         | ❔      | ❔    | ❔      | ❔      | ❔             | ❔         | ❌     | ❔    | ❔     | ❔ | ❔       |                                                               |
|                   | **Huawei**         | ❔     | ❗          | ❔           | ❔         | ❔      | ❔    | ❔      | ❔      | ❔             | ❔         | ❌     | ❔    | ❔     | ❔ | ❔       |                                                               |
|                   | **Juniper**        | ✅     | ❗          | ✅           | ❔         | ❔      | ❔    | ✅      | ❔      | ✅             | ✅         | ❌     | ✅    | ✅     | ✅ | ✅       |                                                               |
|                   | **Mikrotik**       | ❔     | ❗          | ❔           | ❔         | ❔      | ❔    | ❔      | ❔      | ❔             | ❔         | ❌     | ❔    | ❔     | ❔ | ❔       | Mikrotik has announced support for RouterOS v7.20[^2]         |
|                   | **Nokia SR Linux** | ✅     | ❗          | ✅           | ❔         | ❔      | ❔    | ✅      | ❔      | ✅             | ✅         | ❌     | ✅    | ✅     | ✅ | ✅       |                                                               |
|                   | **Nokia SR OS**    | ✅     | ❗          | ✅           | ❔         | ❔      | ❔    | ✅      | ❔      | ✅             | ✅         | ❌     | ✅    | ✅     | ✅ | ✅       |                                                               |
| **Route Servers** | **BIRD 1**         | ❌     | ❌          | ❌           | ❌         | ❌      | ❌    | ❌      | ❌      | ❌             | ❌         | ❌     | ❌    | ❌     | ❌ | ❌       | BIRD 1 will not support RFC8950, use later versions instead   |
|                   | **BIRD 2**         | ✅     | ❗          | ✅           | ❔         | ❔      | ❔    | ✅      | ❔      | ✅             | ✅         | ❌     | ✅    | ✅     | ✅ | ✅       |                                                               |
|                   | **BIRD 3**         | ✅     | ❗          | ✅           | ❔         | ❔      | ❔    | ✅      | ❔      | ✅             | ✅         | ❌     | ✅    | ✅     | ✅ | ✅       |                                                               |
|                   | **FRR**            | ✅     | ❗          | ✅           | ❔         | ❔      | ❔    | ✅      | ❔      | ✅             | ✅         | ❌     | ✅    | ✅     | ✅ | ✅       |                                                               |
|                   | **OpenBGPD**       | ✅     | ❗          | ✅           | ❔         | ❔      | ❔    | ✅      | ❔      | ✅             | ✅         | ❌     | ✅    | ✅     | ✅ | ✅       |                                                               |

[^1]: https://www.cisco.com/c/en/us/td/docs/routers/ios/config/17-x/ip-routing/b-ip-routing/m-support-bgp-vpn-evpn-nexthop.pdf
[^2]: https://help.mikrotik.com/docs/spaces/ROS/pages/28606515/Routing+Protocol+Overview

## Advertising
- GUA = global unique adress
- LLA = link local address
- :: = zero/null/unspecified address

| Type                  | Vendor             | GUA | LLA | :: | Notes                                         |
|-----------------------|--------------------|-----|-----|----|-----------------------------------------------|
| **Routers**           | **Arista**         | ✅  | ❌ | ❌ | RFC 2545 non-compliant                        |
|                       | **Cisco IOS XE**   | ❔  | ❔ | ❔ | not tested due to other missing functionality |
|                       | **Cisco IOS XR**   | ✅  | ✅ | ❎ |                                               |
|                       | **Cisco NX-OS**    | ❔  | ❔ | ❔ | not tested due to other missing functionality |
|                       | **Extreme**        | ❔  | ❔ | ❔ | not tested due to other missing functionality |
|                       | **Huawei**         | ❔  | ❔ | ❔ | not tested due to other missing functionality |
|                       | **Juniper**        | ✅  | ✅ | ❎ |                                               |
|                       | **Mikrotik**       | ❔  | ❔ | ❔ | not tested due to other missing functionality |
|                       | **Nokia SR Linux** | ✅  | ❌ | ❌ | RFC 2545 non-compliant                        |
|                       | **Nokia SR OS**    | ✅  | ❌ | ❌ | RFC 2545 non-compliant                        |
| **Route Servers**     | **BIRD 1**         | ❔  | ❔ | ❔ | not tested due to other missing functionality |
|                       | **BIRD 2**         | ✅  | ✅ | ❎ |                                               |
|                       | **BIRD 3**         | ✅  | ✅ | ❎ |                                               |
|                       | **FRR**            | ✅  | ✅ | ❎ |                                               |
|                       | **OpenBGPD**       | ✅  | ❌ | ❌ | RFC 2545 non-compliant                        |

## Receiving
| Type                  | Vendor             | Preference | Configurable | Notes                                                                                            |
|-----------------------|--------------------|------------|--------------|--------------------------------------------------------------------------------------------------|
| **Routers**           | **Arista**         | GUA        | ❓           |                                                                                                  |
|                       | **Cisco IOS XE**   | ❔         | ❔          | not tested due to other missing functionality                                                    |
|                       | **Cisco IOS XR**   | LLA        | ❓           |                                                                                                  |
|                       | **Cisco NX-OS**    | ❔         | ❔          | not tested due to other missing functionality                                                    |
|                       | **Extreme**        | ❔         | ❔          | not tested due to other missing functionality                                                    |
|                       | **Huawei**         | ❔         | ❔          | not tested due to other missing functionality                                                    |
|                       | **Juniper**        | GUA        | ❓           |                                                                                                  |
|                       | **Mikrotik**       | ❔         | ❔          | not tested due to other missing functionality                                                    |
|                       | **Nokia SR Linux** | GUA        | ❓           |                                                                                                  |
|                       | **Nokia SR OS**    | GUA        | ❓           |                                                                                                  |
| **Route Servers**     | **BIRD 1**         | ❔         | ❔          | not tested due to other missing functionality                                                    |
|                       | **BIRD 2**         | GUA        | ❗           | ```next hop prefer global``` within channel, currently only used for resolving indirect gateways |
|                       | **BIRD 3**         | GUA        | ❗           | ```next hop prefer global``` within channel, currently only used for resolving indirect gateways |
|                       | **FRR**            | LLA        | ✅           | ```set ipv6 next-hop prefer-global``` within route-map                                           |
|                       | **OpenBGPD**       | GUA        | ❔           |                                                                                                  |

# Forwarding
Note: Route Servers rely on an Operating System for forwarding. Therefore they are not included in this category.

## Overview
| Type                  | Vendor             | install IPv4 routes with IPv6 next hop | forward IPv4 packets on IPv6 interface | Notes                                                           |
|-----------------------|--------------------|----------------------------------------|----------------------------------------|-----------------------------------------------------------------|
| **Routers**           | **Arista**         | ✅                                     | ✅                                    | ```interface * ip routing address required disabled```          |
|                       | **Cisco IOS XE**   | ❔                                     | ❔                                    | not tested due to other missing functionality                   |
|                       | **Cisco IOS XR**   | ✅                                     | ✅                                    | ```interface * ipv4 forwarding-enable```                        |
|                       | **Cisco NX-OS**    | ❔                                     | ❔                                    | not tested due to other missing functionality                   |
|                       | **Extreme**        | ❔                                     | ❔                                    | not tested due to other missing functionality                   |
|                       | **Huawei**         | ❔                                     | ❔                                    | not tested due to other missing functionality                   |
|                       | **Juniper**        | ✅                                     | ✅                                    | ```set interfaces * unit * family inet```                       |
|                       | **Mikrotik**       | ❔                                     | ❔                                    | not tested due to other missing functionality                   |
|                       | **Nokia SR Linux** | ✅                                     | ✅                                    | ```network-instance * ip-forwarding receive-ipv4-check false``` |
|                       | **Nokia SR OS**    | ✅                                     | ✅                                    | ```router * interface * ipv6 forward-ipv4-packets```            |
| **Operating Systems** | **Linux**          | ✅                                     | ✅                                    | no special configuration needed                                 |
|                       | **OpenBSD**        | ❌ [^3]                                | ❔                                    | not fully tested due to other missing functionality             |

[^3]: https://github.com/openbgpd-portable/openbgpd-openbsd/commit/f9365c08c05927510280d3b077392615c5b96026

## ICMP
- lo = Loopback interface
- mgmt = Management interface
- out = the interface the packet will be forwarded out of

| Type                  | Vendor             | Interface | Notes                                         |
|-----------------------|--------------------|-----------|-----------------------------------------------|
| **Routers**           | **Arista**         | mgmt      | if management interface is in same VRF        |
|                       | **Cisco IOS XE**   | ❔        | not tested due to other missing functionality |
|                       | **Cisco IOS XR**   | mgmt      | probably similar to Arista, not confirmed     |
|                       | **Cisco NX-OS**    | ❔        | not tested due to other missing functionality |
|                       | **Extreme**        | ❔        | not tested due to other missing functionality |
|                       | **Huawei**         | ❔        | not tested due to other missing functionality |
|                       | **Juniper**        | lo        |                                               |
|                       | **Mikrotik**       | ❔        | not tested due to other missing functionality |
|                       | **Nokia SR Linux** | out       |                                               |
|                       | **Nokia SR OS**    | out       |                                               |
| **Operating Systems** | **Linux**          | lo        |                                               |
|                       | **OpenBSD**        | ❔        | not tested due to other missing functionality |