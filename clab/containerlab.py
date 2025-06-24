from __future__ import annotations

import os
import yaml

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
		return "files/" + self.name + ".clab.yml"



	def export(self):
		exec(["rm", "files/configs/*"])

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