from __future__ import annotations

import yaml

import clab.containerlab
import clab.topology



class Topology(yaml.YAMLObject):
	def __init__(self):
		self.setNodes([])
		self.setLinks([])
		self.setID(0)

	def __repr__(self) -> dict:
		dict = {
			"nodes": {},
			"links": self.getLinks()}

		for node in self.getNodes():
			dict.get("nodes")[node.getName()] = node

		return dict



	def getLab(self) -> clab.containerlab.Lab:
		return self.lab

	def setLab(self, lab: clab.containerlab.Lab):
		self.lab = lab



	def getNodes(self) -> list[clab.topology.Node]:
		return self.nodes

	def setNodes(self, nodes: list[clab.topology.Node]):
		self.nodes = nodes

	def addNode(self, node: clab.topology.Node):
		node.setTopology(self)

		self.getNodes().append(node)



	def getLinks(self) -> list[clab.topology.Link]:
		return self.links

	def setLinks(self, links: list[clab.topology.Link]):
		self.links = links

	def addLink(self, link: clab.topology.Link):
		self.getLinks().append(link)

	def connectNodes(self, node_from: clab.topology.Node, node_to: clab.topology.Node):
		self.addLink(clab.topology.Link(node_from, node_to))



	def getID(self) -> int:
		return self.id

	def setID(self, id: int):
		self.id = id

	def getNextID(self) -> int:
		self.setID(self.getID()+1)

		return self.getID()