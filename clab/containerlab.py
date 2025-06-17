from __future__ import annotations

import asyncio
import os
import yaml

import clab.constants
import clab.kinds
import clab.lab



DEFAULT_PREFIX = "clab"



def exec(cmd: list[str]):
	print(" ".join(cmd))

	os.system(" ".join(cmd))



class Lab(yaml.YAMLObject):
	def __init__(self, name: str, prefix: str = DEFAULT_PREFIX):
		self.name: str = name
		self.prefix: str = prefix

		self.topology: clab.lab.Topology = clab.lab.Topology(self)

	def __repr__(self) -> dict:
		dict = {
			"name": self.name,
			"topology": self.topology}

		if self.prefix != DEFAULT_PREFIX:
			dict["prefix"] = self.prefix

		return dict



	def get_container_prefix(self) -> str:
		if self.prefix == "__lab-name":
			return self.name + "-"
		elif self.prefix == "":
			return ""
		else:
			return self.prefix + "-" + self.name + "-"

	def get_topology_file_path(self) -> str:
		return clab.constants.FILES_DIR + "/" + self.name + ".clab.yml"



	def export(self):
		exec(["rm", clab.constants.FILES_DIR + "/" + clab.constants.CONFIG_DIR + "/*"])

		for node in self.topology.nodes:
			node.export()

		file = open(self.get_topology_file_path(), "w")
		file.write(yaml.dump(self))
		file.close()

	def destroy(self):
		for node in self.topology.nodes:
			node.pre_destroy()

		exec(["clab", "destroy", "--cleanup", "--topo", self.get_topology_file_path()])

		for node in self.topology.nodes:
			node.post_destroy()

	def deploy(self):
		for node in self.topology.nodes:
			node.pre_deploy()

		exec(["clab", "deploy", "--reconfigure", "--topo", self.get_topology_file_path()])

		for node in self.topology.nodes:
			node.post_deploy()

	async def test(self):
		routers: list[clab.kinds.Router] = []

		for node in self.topology.nodes:
			if isinstance(node, clab.kinds.Router):
				routers.append(node)

		matrix = {}
		tasks = []

		for router_from in routers:
			matrix[router_from.get_name()] = {
				"icmp-addresses": {},
				"traceroute": {}}

			for router_to in routers:
				if router_to is not router_from:
					tasks.append(router_from.interfaces[clab.constants.CLIENT_LAN_NAME].connected_to.node.exec(["traceroute", "-I", "-n", "-m", "3", str(router_to.interfaces[clab.constants.CLIENT_LAN_NAME].connected_to.ipv4.ip)], type="traceroute", router_from=router_from, router_to=router_to))

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

			router_from: clab.kinds.Router = kwargs["router_from"]
			router_to: clab.kinds.Router = kwargs["router_to"]

			if returncode != 0:
				test["reasons"].append("non-zero exit code")
			if len(stderr) != 0:
				test["reasons"].append("stderr is not empty")
			if len(stdout) != 4:
				test["reasons"].append("unexpected length of stdout")
			if len(stdout) > 1 and str(router_from.interfaces[clab.constants.CLIENT_LAN_NAME].ipv4.ip) not in stdout[1]:
					test["reasons"].append("incorrect first hop")
			if len(stdout) > 3 and str(router_to.interfaces[clab.constants.CLIENT_LAN_NAME].connected_to.ipv4.ip) not in stdout[3]:
					test["reasons"].append("incorrect last hop")
			if test["reasons"] == []:
				test["result"] = "succeeded"

				address = stdout[2].split(" ")[3]

				if address not in matrix[router_to.get_name()]["icmp-addresses"]:
					interface = "other"

					if address == router_to.interfaces[clab.constants.CLIENT_LAN_NAME]:
						interface = clab.constants.CLIENT_LAN_NAME
					elif address == router_to.interfaces[clab.constants.LOOPBACK_NAME]:
						interface = clab.constants.LOOPBACK_NAME

					matrix[router_to.get_name()]["icmp-addresses"][address] = {
						"as-seen-by": [router_from.get_name()],
						"interface": interface}
				else:
					matrix[router_to.get_name()]["icmp-addresses"][address]["as-seen-by"].append(router_from.get_name())

			matrix[router_from.get_name()]["traceroute"][router_to.get_name()] = test

		file = open("results.yml", "w")
		file.write(yaml.dump(matrix))
		file.close()