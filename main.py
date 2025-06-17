import asyncio
import ipaddress
import time

from clab import constants, containerlab, kinds, topology

lab = containerlab.Lab("peering_lan")

nodes = [
	(kinds.Arista_cEOS, {"image": "vrnetlab/arista_ceos:4.33.2F"}),
	(kinds.Arista_vEOS, {"image": "vrnetlab/arista_veos:4.33.2F"}),
	(kinds.Cisco_XRd, {"image": "ios-xr/xrd-control-plane:25.1.1"}),
	(kinds.Juniper_vJunosEvolved, {"image": "vrnetlab/juniper_vjunosevolved:24.4R1.8"}),
	(kinds.Nokia_SR_Linux, {"image": "ghcr.io/nokia/srlinux"}),
	(kinds.Nokia_SR_OS, {"image": "vrnetlab/nokia_sros:23.10.R6", "license": constants.LICENSE_DIR + "/SR_OS_VSR-SIM1_license.txt"}),
	(kinds.BIRD2, {"image": "bird:2"}),
	(kinds.BIRD3, {"image": "bird:3"}),
	(kinds.FRR, {"image": "quay.io/frrouting/frr:10.3.0"}),
	(kinds.OpenBGPD, {"image": "openbgpd/openbgpd"})
]

peering_lan = kinds.Bridge(None)
lab.topology.add_node(peering_lan)

id = 0

for Router, attributes in nodes:
	for i in range(1):
		id += 1

		peering_lan.add_interface(constants.PEERING_LAN_NAME + "_" + str(id), topology.Interface(id))

		router: kinds.Router = Router(id, **attributes)
		router.add_interface(constants.LOOPBACK_NAME, topology.Interface(None, ipv4=ipaddress.IPv4Interface((constants.LOOPBACK_PREFIX + str(id) + "." + constants.ROUTER_SUFFIX, constants.LOOPBACK_PREFIX_LENGTH))))
		router.add_interface(constants.PEERING_LAN_NAME, topology.Interface(1, ipv6=ipaddress.IPv6Interface((constants.PEERING_LAN_PREFIX + str(id), constants.PEERING_LAN_PREFIX_LENGTH))))
		router.add_interface(constants.CLIENT_LAN_NAME, topology.Interface(2, ipv4=ipaddress.IPv4Interface((constants.CLIENT_LAN_PREFIX + str(id) + "." + constants.ROUTER_SUFFIX, constants.CLIENT_LAN_PREFIX_LENGTH))))

		client: kinds.Client = kinds.Alpine(id)
		client.add_interface(constants.CLIENT_LAN_NAME, topology.Interface(2, ipv4=ipaddress.IPv4Interface((constants.CLIENT_LAN_PREFIX + str(id) + "." + constants.CLIENT_SUFFIX, constants.CLIENT_LAN_PREFIX_LENGTH))))
		client.default_gateway = client.interfaces[constants.CLIENT_LAN_NAME]

		lab.topology.add_node(router)
		lab.topology.add_node(client)

		lab.topology.connect_interfaces(peering_lan.interfaces[constants.PEERING_LAN_NAME + "_" + str(id)], router.interfaces[constants.PEERING_LAN_NAME])
		lab.topology.connect_interfaces(router.interfaces[constants.CLIENT_LAN_NAME], client.interfaces[constants.CLIENT_LAN_NAME])

#lab.destroy()
#lab.export()
lab.deploy()
#time.sleep(60*10)
#asyncio.run(lab.test())