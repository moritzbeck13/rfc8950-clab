import yaml



class Node(yaml.YAMLObject):
	KIND = None
	NAME = None
	INTERFACE_PREFIX = "eth"



	def __init__(self, id: int, **kwargs: dict):
		self.setID(id)
		self.setName(self.NAME + "_" + str(self.getID()))
		self.setNextInterface(0)

		self.setAttributes(kwargs)
		self.setAttribute("kind", self.KIND)

	def __repr__(self) -> dict:
		return self.getAttributes()



	def getID(self) -> int:
		return self.id

	def setID(self, id: int):
		self.id = id
	


	def getName(self) -> str:
		return self.name

	def setName(self, name: str):
		self.name = name



	def getNextInterface(self) -> str:
		self.setNextInterface(self.next_interface+1)

		return self.INTERFACE_PREFIX + str(self.next_interface)

	def setNextInterface(self, next_interface: int):
		self.next_interface = next_interface



	def getAttributes(self) -> dict:
		return self.attributes

	def setAttributes(self, attributes: dict):
		self.attributes = attributes



	def getAttribute(self, key: str) -> str:
		return self.getAttributes().get(key)

	def setAttribute(self, key: str, value: str):
		self.getAttributes()[key] = value



	def destroy(self):
		pass

	def deploy(self):
		pass



class Link(yaml.YAMLObject):
	def __init__(self, node_from: Node, node_to: Node):
		self.setNodeFrom(node_from)
		self.setNodeTo(node_to)

	def __repr__(self) -> dict:
		return {
			"endpoints": [
				self.getNodeFrom().getName() + ":" + self.getNodeFrom().getNextInterface(),
	 			self.getNodeTo().getName() + ":" + self.getNodeTo().getNextInterface()]}



	def getNodeFrom(self) -> Node:
		return self.node_from

	def setNodeFrom(self, node: Node):
		self.node_from = node



	def getNodeTo(self) -> Node:
		return self.node_to

	def setNodeTo(self, node: Node):
		self.node_to = node