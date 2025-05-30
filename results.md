# Findings
- Routers:
	- Cisco IOS XE does not fully support RFC 8950
	- Cisco IOS XR requires a license
	- Huawei does not support RFC 8950 yet
	- Nokia SR OS requires a license
- Route Servers:
	- BIRD has limited functionality for configuring the next-hop type preference 
	- ExaBGP cannot modify the route table
	- GoBGP cannot modify the route table
	- Juniper offers specialized route server implemenations
	- OpenBGPD does not support RFC 8950 yet
	- Quagga has not been updated since 2018, which predates RFC 8950
	- XORP has not been updated since 2012, which predates RFC 8950
	- Zebra has not been updated since 2005, which predates RFC 8950

# Results
| Vendor  | Version  | ICMP interface | GUA | LLA | Preference | Configurable                                       |
|---------|----------|----------------|-----|-----|------------|----------------------------------------------------|
| Arista  | cEOS     | management     | yes | no  | GUA        | no?                                                |
| Arista  | vEOS     | management     | yes | no  | GUA        | no?                                                |
| Cisco   | IOS XR   | management     | yes | yes | LLA        | no?                                                |
| Juniper | Junos OS | loopback       | yes | yes | GUA        | no?                                                |
| Nokia   | SR Linux | outgoing       | yes | no  | GUA        | no?                                                |
| Nokia   | SR OS    | outgoing       | yes | no  | GUA        | no?                                                |
| BIRD    | 2        | loopback       | yes | yes | GUA        | "next hop prefer global" within channel            |
| BIRD    | 3        | loopback       | yes | yes | GUA        | "next hop prefer global" within channel            |
| FRR     | 10       | loopback       | yes | yes | LLA        | "set ipv6 next-hop prefer-global" within route-map |

# Conclusion
- almost all major vendors support RFC 8950, only some don't
- all vendors that support it do so fully and properly
- all vendors that don't support it do so for a good reason
- not all vendors properly support RFC 2545 from 1999 (!)
- the actual implementation-specific behaviour still differs in almost all aspects from vendor to vendor
- unintuitively, while route servers offer at least some configurability, at least to my knowledge no routers do
- there is a IETF IDR WG draft to address the behaviour and configurability issues

# Links
- https://en.wikipedia.org/wiki/List_of_open-source_routing_platforms
- https://github.com/Exa-Networks/exabgp/wiki/Other-OSS-BGP-implementations
- https://elegantnetwork.github.io/posts/comparing-open-source-bgp-stacks/
- https://datatracker.ietf.org/doc/draft-ietf-idr-linklocal-capability/