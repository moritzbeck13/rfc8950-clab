import yaml
import Clab.Topology



class Topology(yaml.YAMLObject):
	def __init__(self):
		self.setKinds([])
		self.setNodes([])
		self.setLinks([])

		self.setID(0)

	def __repr__(self) -> dict:
		dict = {"kinds": {}, "nodes": {}, "links": self.getLinks()}

		for kind in self.getKinds():
			dict.get("kinds")[kind.getName()] = kind

		for node in self.getNodes():
			dict.get("nodes")[node.getName()] = node

		return dict



	def getKinds(self) -> list[Clab.Topology.Kind]:
		return self.kinds

	def setKinds(self, kinds: list[Clab.Topology.Kind]):
		self.kinds = kinds


	def addKind(self, kind: Clab.Topology.Kind):
		self.getKinds().append(kind)



	def getNodes(self) -> list[Clab.Topology.Node]:
		return self.nodes

	def setNodes(self, nodes: list[Clab.Topology.Node]):
		self.nodes = nodes


	def addNode(self, node: Clab.Topology.Node):
		self.getNodes().append(node)



	def getLinks(self) -> list[Clab.Topology.Link]:
		return self.links

	def setLinks(self, links: list[Clab.Topology.Link]):
		self.links = links


	def connectNodes(self, node_from: Clab.Topology.Node, node_to: Clab.Topology.Node):
		self.addLink(Clab.Topology.Link(node_from, node_to))


	def addLink(self, link: Clab.Topology.Link):
		self.getLinks().append(link)



	def getID(self) -> int:
		return self.id

	def setID(self, id: int):
		self.id = id


	def getNextID(self) -> int:
		self.setID(self.getID()+1)

		return self.getID()