import os
import yaml

import clab.Constants
import clab.Kind
import clab.Lab



class Lab(yaml.YAMLObject):
	def __init__(self, name: str):
		self.setName(name)
		self.setTopology(clab.Lab.Topology())

	def __repr__(self) -> dict:
		return {
			"name": self.getName(),
			"topology": self.getTopology()}



	def getName(self) -> str:
		return self.name

	def setName(self, name: str):
		self.name = name



	def getTopology(self) -> clab.Lab.Topology:
		return self.topology

	def setTopology(self, topology: clab.Lab.Topology):
		self.topology = topology



	def export(self):
		os.system("rm " + clab.Constants.FILES_DIR + "/" + clab.Constants.CONFIG_DIR + "/*")

		file = open(clab.Constants.FILES_DIR + "/" + self.getName() + ".clab.yml", "w")
		file.write(yaml.dump(self))
		file.close()

		nodes = self.getTopology().getNodes()

		for node in nodes:
			if isinstance(node, clab.Kind.Router):
				node.generateConfig(nodes)


	def destroy(self):
		os.system("sudo iptables -vL FORWARD --line-numbers -n | grep 'set by containerlab' | awk '{print $1}' | sort -r | xargs -I {} sudo iptables -D FORWARD {}")
		os.system("sudo ip link delete " + clab.Constants.PEERING_LAN_NAME)

		os.system("clab destroy --cleanup --topo " + clab.Constants.FILES_DIR + "/" + self.getName() + ".clab.yml")

	def deploy(self):
		os.system("sudo ip link add " + clab.Constants.PEERING_LAN_NAME + " type bridge")
		os.system("sudo ip link set dev " + clab.Constants.PEERING_LAN_NAME + " up")

		os.system("clab deploy --reconfigure --topo " + clab.Constants.FILES_DIR + "/" + self.getName() + ".clab.yml")