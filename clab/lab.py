from __future__ import annotations

import yaml

import clab.containerlab
import clab.topology



class Topology(yaml.YAMLObject):
	def __init__(self, lab: clab.containerlab.Lab):
		self.lab: clab.containerlab.Lab = lab

		self.nodes: list[clab.topology.Node] = []
		self.links: list[clab.topology.Link] = []

	def __repr__(self) -> dict:
		dict = {
			"nodes": {},
			"links": self.links}

		nodes: list[clab.topology.Node] = dict["nodes"]

		for node in self.nodes:
			nodes[node.get_name()] = node

		return dict



	def add_node(self, node: clab.topology.Node):
		node.topology = self

		self.nodes.append(node)

	def connect_interfaces(self, interface_from: clab.topology.Interface, interface_to: clab.topology.Interface):
		self.links.append(clab.topology.Link(interface_from, interface_to))