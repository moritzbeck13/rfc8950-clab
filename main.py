import yaml

from clab import Constants, Containerlab, Kind, Lab, Topology



def representer(dumper, data):
	return dumper.represent_data(data.__repr__())

yaml.add_representer(Containerlab.Lab, representer)
yaml.add_representer(Lab.Topology, representer)
yaml.add_representer(Topology.Link, representer)
yaml.add_multi_representer(Topology.Node, representer)



if __name__ == "__main__":
	lab = Containerlab.Lab("peeringlan")
	topology = lab.getTopology()

	nodes = [
		(Kind.Nokia_SR_Linux, {"image": "ghcr.io/nokia/srlinux"}),
		(Kind.Nokia_SR_OS, {"image": "vrnetlab/nokia_sros:23.10.R6", "license": Constants.LICENSES_DIR + "/SR_OS_VSR-SIM1_license.txt"}),
		(Kind.Arista_cEOS, {"image": "vrnetlab/arista_ceos:4.33.2F"}),
		(Kind.Arista_vEOS, {"image": "vrnetlab/arista_veos:4.33.2F"}),
		(Kind.Cisco_XRv9k, {"image": "vrnetlab/cisco_xrv9k:6.6.3"}),
		(Kind.Juniper_vJunos_router, {"image": "vrnetlab/juniper_vjunos-router:23.2R1.15"}),
		(Kind.Juniper_vJunos_switch, {"image": "vrnetlab/juniper_vjunos-switch:23.1R1.8"}),
		(Kind.Juniper_vJunosEvolved, {"image": "vrnetlab/juniper_vjunosevolved:24.4R1.8"})
	]

	peering_lan = Kind.Bridge(Constants.PEERING_LAN_NAME)
	topology.addNode(peering_lan)

	for Node, attributes in nodes:
		id = topology.getNextID()

		router = Node(id, **attributes)
		client = Kind.Alpine(id)

		topology.addNode(router)
		topology.addNode(client)

		topology.connectNodes(peering_lan, router)
		topology.connectNodes(router, client)

	lab.destroy()
	lab.export()
	lab.deploy()