# Peering
Note: Operating Systems rely on a Route Server for peering. Therefore they are not included in this category.

## Legend
- ✅ = tested, working
- ❎ = tested, not working but expected behaviour
- ❌ = tested, not working
- ❗ = tested, limited functionality
- ❔ = not tested, missing functionality

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
| **Route Server** |              | **BIRD**     | ✅  | ✅  | ❎ |                                               |
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
| **Route Server** |              | **BIRD**     | `GUA`      | ❗           | `next hop prefer global` within channel, currently only used for resolving indirect gateways |
|                  |              | **FRR**      | `LLA`      | ✅           | `set ipv6 next-hop prefer-global` within route-map                                           |
|                  |              | **OpenBGPD** | `GUA`      | ❔           |                                                                                              |