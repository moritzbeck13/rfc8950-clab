import yaml

from Clab import Containerlab, Kind, Lab, Topology



def representer(dumper, data):
	return dumper.represent_data(data.__repr__())

yaml.add_representer(Containerlab.Lab, representer)
yaml.add_representer(Lab.Topology, representer)
yaml.add_representer(Topology.Link, representer)
yaml.add_multi_representer(Topology.Kind, representer)



if __name__ == "__main__":
	lab = Containerlab.Lab("peeringlan")
	topology = lab.getTopology()

	nokia_srlinux = Topology.Kind(Kind.Nokia_SR_Linux, **{
		"image": "ghcr.io/nokia/srlinux",
		"startup-config": Containerlab.Constants.CONFIG_DIR + "/__clabNodeName__" + Kind.Nokia_SR_Linux.config_suffix})
	nokia_sros = Topology.Kind(Kind.Nokia_SR_OS, **{
		"image": "vrnetlab/nokia_sros:23.10.R6",
		"license": "licenses/SR_OS_VSR-SIM1_license.txt",
		"startup-config": Containerlab.Constants.CONFIG_DIR + "/__clabNodeName__" + Kind.Nokia_SR_OS.config_suffix})
	arista_ceos = Topology.Kind(Kind.Arista_cEOS, **{
		"image": "vrnetlab/ceos:4.33.2F",
		"startup-config": Containerlab.Constants.CONFIG_DIR + "/__clabNodeName__" + Kind.Arista_cEOS.config_suffix})
	linux = Topology.Kind(Kind.Linux, image="alpine")

	topology.addKind(nokia_srlinux)
	topology.addKind(nokia_sros)
	topology.addKind(arista_ceos)
	topology.addKind(linux)

	peering_lan = Kind.Bridge(Containerlab.Constants.PEERING_LAN_NAME)
	topology.addNode(peering_lan)

	nodes = [
		{"kind": Kind.Nokia_SR_Linux, "count": 1},
		{"kind": Kind.Nokia_SR_OS, "count": 2},
		{"kind": Kind.Arista_cEOS, "count": 1}]

	for node in nodes:
		for i in range(node.get("count", 1)):
			id = topology.getNextID()
			kind = node.get("kind")

			router = kind(kind.name + str(i+1), id)
			host = Kind.Linux("client" + str(id), id)

			topology.addNode(router)
			topology.addNode(host)

			topology.connectNodes(peering_lan, router)
			topology.connectNodes(router, host)

	lab.export()