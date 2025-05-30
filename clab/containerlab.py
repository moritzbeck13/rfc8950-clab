from __future__ import annotations

import asyncio
import os
import yaml

import clab.constants
import clab.kinds
import clab.lab



def run(cmd: list[str]):
	print(" ".join(cmd))

	os.system(" ".join(cmd))



class Lab(yaml.YAMLObject):
	def __init__(self, name: str, prefix: str = "clab"):
		self.setName(name)
		self.setPrefix(prefix)
		self.setTopology(clab.lab.Topology())

	def __repr__(self) -> dict:
		dict = {
			"name": self.getName(),
			"topology": self.getTopology()}

		prefix = self.getPrefix()

		if prefix != "clab":
			dict["prefix"] = prefix

		return dict



	def getName(self) -> str:
		return self.name

	def setName(self, name: str):
		self.name = name



	def getPrefix(self) -> str:
		return self.prefix

	def setPrefix(self, prefix: str):
		self.prefix = prefix

	def getContainerPrefix(self) -> str:
		prefix = self.getPrefix()

		if prefix == "__lab-name":
			return self.getName() + "-"
		elif prefix == "":
			return ""
		else:
			return prefix + "-" + self.getName() + "-"



	def getTopology(self) -> clab.lab.Topology:
		return self.topology

	def setTopology(self, topology: clab.lab.Topology):
		topology.setLab(self)

		self.topology = topology

	def getTopologyFilePath(self) -> str:
		return clab.constants.FILES_DIR + "/" + self.getName() + ".clab.yml"



	def export(self):
		run(["rm", clab.constants.FILES_DIR + "/" + clab.constants.CONFIG_DIR + "/*"])

		for node in self.getTopology().getNodes():
			node.generateConfig()

		file = open(self.getTopologyFilePath(), "w")
		file.write(yaml.dump(self))
		file.close()

	def destroy(self):
		run(["clab", "destroy", "--cleanup", "--topo", self.getTopologyFilePath()])

		for node in self.getTopology().getNodes():
			node.destroy()

	def deploy(self):
		for node in self.getTopology().getNodes():
			node.deploy()

		run(["clab", "deploy", "--reconfigure", "--topo", self.getTopologyFilePath()])

	async def test(self):
		routers = []

		for node in self.getTopology().getNodes():
			if isinstance(node, clab.kinds.Router):
				routers.append(node)

		matrix = {}
		tasks = []

		for router_from in routers:
			matrix[router_from.NAME] = {
				"icmp-addresses": {},
				"traceroute": {}}

			for router_to in routers:
				if router_to is not router_from:
					tasks.append(router_from.getClient().exec(["traceroute", "-I", "-n", "-m", "3", router_to.getClient().getAddress()], type="traceroute", router_from=router_from, router_to=router_to))

		results = await asyncio.gather(*tasks)

		for result in results:
			returncode = result.get("returncode")
			stderr = result.get("stderr")
			stdout = result.get("stdout")
			kwargs = result.get("kwargs")

			test = {
				"exit-code": returncode,
				"reasons": [],
				"result": "failed",
				"stderr": stderr,
				"stdout": stdout}

			router_from = kwargs["router_from"]
			router_to = kwargs["router_to"]

			if returncode != 0:
				test["reasons"].append("non-zero exit code")
			if len(stderr) != 0:
				test["reasons"].append("stderr is not empty")
			if len(stdout) != 4:
				test["reasons"].append("unexpected length of stdout")
			if len(stdout) > 1 and router_from.getClientLANAddress() not in stdout[1]:
					test["reasons"].append("incorrect first hop")
			if len(stdout) > 3 and router_to.getClient().getAddress() not in stdout[3]:
					test["reasons"].append("incorrect last hop")
			if test["reasons"] == []:
				test["result"] = "succeeded"

				address = stdout[2].split(" ")[3]

				if address not in matrix[router_to.NAME]["icmp-addresses"]:
					interface = "other"

					if address == router_to.getClientLANAddress():
						interface = clab.constants.CLIENT_LAN_NAME
					elif address == router_to.getLoopbackAddress():
						interface = clab.constants.ROUTER_LOOPBACK_NAME

					matrix[router_to.NAME]["icmp-addresses"][address] = {
						"as-seen-by": [router_from.NAME],
						"interface": interface}
				else:
					matrix[router_to.NAME]["icmp-addresses"][address]["as-seen-by"].append(router_from.NAME)

			matrix[router_from.NAME]["traceroute"][router_to.NAME] = test

		file = open("results.yml", "w")
		file.write(yaml.dump(matrix))
		file.close()