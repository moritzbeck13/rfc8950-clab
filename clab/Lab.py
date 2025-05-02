import yaml

import clab.Topology



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




	def getNodes(self) -> list[clab.Topology.Node]:
		return self.nodes

	def setNodes(self, nodes: list[clab.Topology.Node]):
		self.nodes = nodes


	def addNode(self, node: clab.Topology.Node):
		self.getNodes().append(node)



	def getLinks(self) -> list[clab.Topology.Link]:
		return self.links

	def setLinks(self, links: list[clab.Topology.Link]):
		self.links = links


	def addLink(self, link: clab.Topology.Link):
		self.getLinks().append(link)


	def connectNodes(self, node_from: clab.Topology.Node, node_to: clab.Topology.Node):
		self.addLink(clab.Topology.Link(node_from, node_to))



	def getID(self) -> int:
		return self.id

	def setID(self, id: int):
		self.id = id


	def getNextID(self) -> int:
		self.setID(self.getID()+1)

		return self.getID()