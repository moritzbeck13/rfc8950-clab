import os
import yaml
import Clab.Lab



class Constants:
	FILES_DIR = "files"

	CONFIG_DIR = "configs"
	LICENSES_DIR = "licenses"
	TEMPLATE_DIR = "templates"

	BASE_ASN = 65000

	PEERING_LAN_NAME = "peering-lan"
	PEERING_LAN_PREFIX = "c1ab::"
	PEERING_LAN_PREFIX_LENGTH = "64"

	ROUTER_LOOPBACK_NAME = "loopback"
	ROUTER_LOOPBACK_PREFIX = "172.16."
	ROUTER_LOOPBACK_SUFFIX = "1"
	ROUTER_LOOPBACK_PREFIX_LENGTH = "32"

	CLIENT_LAN_NAME = "client-lan"
	CLIENT_LAN_PREFIX = "192.168."
	CLIENT_LAN_ROUTER_SUFFIX = "1"
	CLIENT_LAN_CLIENT_SUFFIX = "254"
	CLIENT_LAN_PREFIX_LENGTH = "24"



class Lab(yaml.YAMLObject):
	def __init__(self, name: str):
		self.setName(name)
		self.setTopology(Clab.Lab.Topology())

	def __repr__(self) -> dict:
		return {"name": self.getName(), "topology": self.getTopology()}



	def getName(self) -> str:
		return self.name

	def setName(self, name: str):
		self.name = name



	def getTopology(self) -> Clab.Lab.Topology:
		return self.topology

	def setTopology(self, topology: Clab.Lab.Topology):
		self.topology = topology



	def export(self):
		file = open(Constants.FILES_DIR + "/" + self.getName() + ".clab.yml", "w")
		file.write(yaml.dump(self))
		file.close()

		nodes = self.getTopology().getNodes()

		for node in nodes:
			node.generateConfig(nodes)

	def destroy(self):
#		os.system("iptables -vL FORWARD --line-numbers -n | grep 'set by containerlab' | awk '{print $1}' | sort -r | xargs -I {} sudo iptables -D FORWARD {}")
#		os.system("sudo ip link delete dev " + Constants.PEERING_LAN_NAME + " type bridge")

#		os.system("rm " + Constants.CONFIG_DIR + "/*")

#		os.system("clab destroy --cleanup")
		pass

	def deploy(self):
#		os.system("sudo ip link add name " + Constants.PEERING_LAN_NAME + " type bridge")
#		os.system("sudo ip link set dev " + Constants.PEERING_LAN_NAME + " up")

#		os.system("clab deploy --reconfigure")
		pass