from __future__ import annotations

import asyncio
import yaml

import clab.lab


class Link(yaml.YAMLObject):
	def __init__(self, node_from: Node, node_to: Node):
		self.setNodeFrom(node_from)
		self.setNodeTo(node_to)

	def __repr__(self) -> dict:
		node_from = self.getNodeFrom()
		node_to = self.getNodeTo()

		return {
			"endpoints": [
				node_from.getName() + ":" + node_from.getNextInterface(),
				node_to.getName() + ":" + node_to.getNextInterface()]}



	def getNodeFrom(self) -> Node:
		return self.node_from

	def setNodeFrom(self, node: Node):
		self.node_from = node



	def getNodeTo(self) -> Node:
		return self.node_to

	def setNodeTo(self, node: Node):
		self.node_to = node



class Node(yaml.YAMLObject):
	KIND = None
	NAME = None

	INTERFACE_PREFIX = "eth"



	def __init__(self, id: int, **kwargs: dict):
		self.setID(id)
		self.setInterface(0)
		self.setAttributes({})

		self.addAttribute("kind", self.KIND)
		self.addAttributes(kwargs)

	def __repr__(self) -> dict:
		return self.getAttributes()



	def getTopology(self) -> clab.lab.Topology:
		return self.topology

	def setTopology(self, topology: clab.lab.Topology):
		self.topology = topology



	def getID(self) -> int:
		return self.id

	def setID(self, id: int):
		self.id = id



	def getName(self) -> str:
		return self.NAME + "_" + str(self.getID())

	def getContainerName(self) -> str:
		return self.getTopology().getLab().getContainerPrefix() + self.getName()



	def getInterface(self) -> int:
		return self.interface

	def setInterface(self, interface: int):
		self.interface = interface

	def getNextInterface(self) -> str:
		self.setInterface(self.getInterface()+1)

		return self.INTERFACE_PREFIX + str(self.getInterface())



	def getAttributes(self) -> dict:
		return self.attributes

	def setAttributes(self, attributes: dict):
		self.attributes = attributes

	def addAttributes(self, attributes: dict):
		for key, value in attributes.items():
			self.addAttribute(key, value)



	def getAttribute(self, key: str):
		return self.getAttributes().get(key)

	def setAttribute(self, key: str, value):
		self.getAttributes()[key] = value

	def addAttribute(self, key: str, value):
		attribute = self.getAttribute(key)

		if attribute is None:
			self.setAttribute(key, value)
		else:
			if type(attribute) is list:
				attribute.extend(value)
			elif type(attribute) is dict:
				attribute.update(value)
			else:
				attribute = value



	def generateConfig(self):
		pass

	def destroy(self):
		pass

	def deploy(self):
		pass



	def exec(self, cmd: list[str], **kwargs):
		return asyncio.run(exec(cmd, kwargs))

	async def exec(self, cmd: list[str], **kwargs):
		pass