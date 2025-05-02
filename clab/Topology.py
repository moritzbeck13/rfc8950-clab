from __future__ import annotations

import yaml

import clab.Constants



class Node(yaml.YAMLObject):
	kind = None
	port_prefix = "eth"



	def __init__(self, name: str, id: int, **kwargs: dict):
		self.setName(name)
		self.setID(id)
		self.setPortNumber(0)

		self.setAttributes(kwargs)
		self.setAttribute("kind", self.kind)

	def __repr__(self) -> dict:
		return self.getAttributes()



	def getName(self) -> str:
		return self.name

	def setName(self, name: str):
		self.name = name



	def getID(self) -> int:
		return self.id

	def setID(self, id: int):
		self.id = id



	def getPortNumber(self) -> int:
		return self.port_number

	def setPortNumber(self, port_number: int):
		self.port_number = port_number


	def getNextPort(self) -> str:
		self.setPortNumber(self.getPortNumber()+1)

		return self.port_prefix + str(self.getPortNumber())



	def getAttributes(self) -> dict:
		return self.attributes

	def setAttributes(self, attributes: dict):
		self.attributes = attributes



	def getAttribute(self, key: str) -> str:
		return self.getAttributes().get(key)

	def setAttribute(self, key: str, value: str):
		self.getAttributes()[key] = value



	def generateConfig(self, nodes: list[Node]):
		pass



class Router(Node):
	config_suffix = None



	def __init__(self, name, id, **kwargs):
		super().__init__(name, id, **kwargs)

		self.setAttribute("startup-config", clab.Constants.CONFIG_DIR + "/" + self.getName() + self.config_suffix)



	def getNeighborStatement(self) -> str:
		return ""

	def generateConfig(self, peers: list[Node]):
		file = open(clab.Constants.FILES_DIR + "/" + clab.Constants.TEMPLATE_DIR + "/" + self.kind + self.config_suffix)
		config = file.read()
		file.close()

		neighbor = self.getNeighborStatement()
		neighbor = neighbor.replace("$PEERING_LAN_NAME", clab.Constants.PEERING_LAN_NAME)

		neighbors = []

		for peer in peers:
			peer_id = peer.getID()

			if isinstance(peer, Router) and peer is not self:
				neighbors.append(neighbor \
					.replace("$PEER_ADDRESS",	clab.Constants.PEERING_LAN_PREFIX + str(peer_id)) \
					.replace("$PEER_ASN",		str(clab.Constants.BASE_ASN + peer_id)))

		neighbors = "\n".join(neighbors)

		id = self.getID()
		id_str = str(id)

		config = config \
			.replace("$ASN",							str(clab.Constants.BASE_ASN + id)) \
			.replace("$PEERING_LAN_NAME",				clab.Constants.PEERING_LAN_NAME) \
			.replace("$PEERING_LAN_ADDRESS",			clab.Constants.PEERING_LAN_PREFIX + id_str) \
			.replace("$PEERING_LAN_PREFIX_LENGTH",		clab.Constants.PEERING_LAN_PREFIX_LENGTH) \
			.replace("$ROUTER_LOOPBACK_NAME",			clab.Constants.ROUTER_LOOPBACK_NAME) \
			.replace("$ROUTER_LOOPBACK_ADDRESS",		clab.Constants.ROUTER_LOOPBACK_PREFIX + id_str + "." + clab.Constants.ROUTER_LOOPBACK_SUFFIX) \
			.replace("$ROUTER_LOOPBACK_PREFIX_LENGTH",	clab.Constants.ROUTER_LOOPBACK_PREFIX_LENGTH) \
			.replace("$ROUTER_LOOPBACK_SUBNET_MASK",	clab.Constants.ROUTER_LOOPBACK_SUBNET_MASK) \
			.replace("$CLIENT_LAN_NAME",				clab.Constants.CLIENT_LAN_NAME) \
			.replace("$CLIENT_LAN_ADDRESS",				clab.Constants.CLIENT_LAN_PREFIX + id_str + "." + clab.Constants.CLIENT_LAN_ROUTER_SUFFIX) \
			.replace("$CLIENT_LAN_NETWORK",				clab.Constants.CLIENT_LAN_PREFIX + id_str + ".0") \
			.replace("$CLIENT_LAN_PREFIX_LENGTH",		clab.Constants.CLIENT_LAN_PREFIX_LENGTH) \
			.replace("$CLIENT_LAN_SUBNET_MASK",			clab.Constants.CLIENT_LAN_SUBNET_MASK) \
			.replace("$NEIGHBORS",						neighbors)

		file = open(clab.Constants.FILES_DIR + "/" + clab.Constants.CONFIG_DIR + "/" + self.getName() + self.config_suffix, "w")
		file.write(config)
		file.close()



class Link(yaml.YAMLObject):
	def __init__(self, node_from: Node, node_to: Node):
		self.setNodeFrom(node_from)
		self.setNodeTo(node_to)

	def __repr__(self) -> dict:
		return {
			"endpoints": [
				self.getNodeFrom().getName() + ":" + self.getNodeFrom().getNextPort(),
	 			self.getNodeTo().getName() + ":" + self.getNodeTo().getNextPort()]}



	def getNodeFrom(self) -> Node:
		return self.node_from

	def setNodeFrom(self, node: Node):
		self.node_from = node



	def getNodeTo(self) -> Node:
		return self.node_to

	def setNodeTo(self, node: Node):
		self.node_to = node