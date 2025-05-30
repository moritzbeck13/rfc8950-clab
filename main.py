import asyncio
import time

from clab import constants, containerlab, kinds

lab = containerlab.Lab("peering_lan")
topology = lab.getTopology()

nodes = [
	(kinds.Nokia_SR_Linux, {"image": "ghcr.io/nokia/srlinux"}),
	(kinds.Nokia_SR_OS, {"image": "vrnetlab/nokia_sros:23.10.R6", "license": constants.LICENSE_DIR + "/SR_OS_VSR-SIM1_license.txt"}),
	(kinds.Arista_cEOS, {"image": "vrnetlab/arista_ceos:4.33.2F"}),
	(kinds.Arista_vEOS, {"image": "vrnetlab/arista_veos:4.33.2F"}),
	(kinds.Cisco_XRd, {"image": "ios-xr/xrd-control-plane:25.1.1"}),
	(kinds.Juniper_vJunosEvolved, {"image": "vrnetlab/juniper_vjunosevolved:24.4R1.8"}),
	(kinds.BIRD2, {"image": "bird:2"}),
	(kinds.BIRD3, {"image": "bird:3"}),
	(kinds.FRR, {"image": "quay.io/frrouting/frr:10.3.0"})
]

peering_lan = kinds.Bridge(None)
topology.addNode(peering_lan)

for Router, attributes in nodes:
	id = topology.getNextID()

	router = Router(id, **attributes)
	client = kinds.Alpine(id)

	router.setClient(client)
	client.setRouter(router)

	topology.addNode(router)
	topology.addNode(client)

	topology.connectNodes(peering_lan, router)
	topology.connectNodes(router, client)

#lab.destroy()
lab.export()
#lab.deploy()
#time.sleep(60*10)
asyncio.run(lab.test())