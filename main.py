import yaml

from clab import Containerlab, Kind, Lab, Topology



def representer(dumper, data):
	return dumper.represent_data(data.__repr__())

yaml.add_representer(Containerlab.Lab, representer)
yaml.add_representer(Lab.Topology, representer)
yaml.add_representer(Topology.Link, representer)
yaml.add_multi_representer(Topology.Kind, representer)



if __name__ == "__main__":
	lab = Containerlab.Lab("peeringlan")
	topology = lab.getTopology()

	topology.addKind(Topology.Kind(Kind.Nokia_SR_Linux, image="ghcr.io/nokia/srlinux"))
	topology.addKind(Topology.Kind(Kind.Nokia_SR_OS, image="vrnetlab/nokia_sros:23.10.R6", license="licenses/SR_OS_VSR-SIM1_license.txt"))
	topology.addKind(Topology.Kind(Kind.Arista_cEOS, image="vrnetlab/arista_ceos:4.33.2F"))
	topology.addKind(Topology.Kind(Kind.Arista_vEOS, image="vrnetlab/arista_veos:4.33.2F"))
	topology.addKind(Topology.Kind(Kind.Cisco_XRv9k, image="vrnetlab/cisco_xrv9k:6.6.3"))
	topology.addKind(Topology.Kind(Kind.Juniper_vJunos_router, image="vrnetlab/juniper_vjunos-router:23.2R1.15"))
	topology.addKind(Topology.Kind(Kind.Juniper_vJunos_switch, image="vrnetlab/juniper_vjunos-switch:23.1R1.8"))
	topology.addKind(Topology.Kind(Kind.Juniper_vJunosEvolved, image="vrnetlab/juniper_vjunosevolved:24.4R1.8"))
	topology.addKind(Topology.Kind(Kind.Linux, image="alpine"))

	peering_lan = Kind.Bridge(Containerlab.Constants.PEERING_LAN_NAME)
	topology.addNode(peering_lan)

	for kind in topology.getKinds():
		if issubclass(kind.getKind(), Topology.Router):
			id = topology.getNextID()

			router = kind.getKind()(kind.name + "_" + str(id), id)
			host = Kind.Linux("client_" + str(id), id)

			topology.addNode(router)
			topology.addNode(host)

			topology.connectNodes(peering_lan, router)
			topology.connectNodes(router, host)

	lab.destroy()
	lab.export()
	lab.deploy()