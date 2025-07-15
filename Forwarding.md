# Routing
Note: Route Servers rely on an Operating System for routing. Therefore they are not included in this category.

## Legend
- ✅ = tested, working
- ❎ = tested, not working but expected behaviour
- ❌ = tested, not working
- ❗ = tested, limited functionality
- ❔ = not tested, missing functionality

## Forwarding
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
|            |              | **OpenBSD**  | ❌                             | ❔                             | OpenBGPD does not install routes into the FIB yet[^1]       |

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

## References
[^1]: https://github.com/openbgpd-portable/openbgpd-openbsd/commit/f9365c08c05927510280d3b077392615c5b96026