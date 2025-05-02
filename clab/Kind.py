import clab.Constants
import clab.Topology



class Bridge(clab.Topology.Node):
	kind = "bridge"

class Linux(clab.Topology.Node):
	kind = "linux"



	def __init__(self, name: str, id: int, **kwargs):
		super().__init__(name, id, **kwargs)

		id_str = str(id)

		self.setAttribute(
			"exec", [
				"ip address add " + clab.Constants.CLIENT_LAN_PREFIX + id_str + "." + clab.Constants.CLIENT_LAN_CLIENT_SUFFIX + "/" + clab.Constants.CLIENT_LAN_PREFIX_LENGTH + " dev eth1",
				"ip route del default",
				"ip route add default via " + clab.Constants.CLIENT_LAN_PREFIX + id_str + "." + clab.Constants.CLIENT_LAN_ROUTER_SUFFIX,
				"ip link set eth1 up"])



class Router(clab.Topology.Node):
	config_suffix = None



	def __init__(self, name, id, **kwargs):
		super().__init__(name, id, **kwargs)

		self.setAttribute("startup-config", clab.Constants.CONFIG_DIR + "/" + self.getName() + self.config_suffix)



	def getNeighborStatement(self) -> str:
		return ""

	def generateConfig(self, peers: list[clab.Topology.Node]):
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



class BIRD(Linux, Router):
	config_suffix = ".conf"


	def __init__(self, name, id, **kwargs):
		super().__init__(name, id, **kwargs)



	def getNeighborStatement(self) -> str:
		return """\
    neighbor $PEER_ADDRESS as $PEER_ASN;"""



class Nokia_SR_Linux(Router):
	kind = "nokia_srlinux"
	port_prefix = "e1-"
	config_suffix = ".json"



	def getNeighborStatement(self) -> str:
		return """\
            neighbor $PEER_ADDRESS {
                peer-group "$PEERING_LAN_NAME-group"
                peer-as $PEER_ASN
            }"""

class Nokia_SR_OS(Router):
	kind = "nokia_sros"
	config_suffix = ".partial.txt"



	def getNeighborStatement(self) -> str:
		return """\
            neighbor $PEER_ADDRESS {
                group "$PEERING_LAN_NAME-group"
                peer-as $PEER_ASN
            }"""

class Arista_cEOS(Router):
	kind = "arista_ceos"
	config_suffix = ""



	def getNeighborStatement(self) -> str:
		return """\
    neighbor $PEER_ADDRESS peer group $PEERING_LAN_NAME-group
    neighbor $PEER_ADDRESS remote-as $PEER_ASN"""

class Arista_vEOS(Router):
	kind = "arista_veos"
	config_suffix = ".cfg"



	def getNeighborStatement(self) -> str:
		return """\
    neighbor $PEER_ADDRESS peer group $PEERING_LAN_NAME-group
    neighbor $PEER_ADDRESS remote-as $PEER_ASN"""

class Cisco_XRv9k(Router):
	kind = "cisco_xrv9k"
	config_suffix = ".partial.cfg"



	def getNeighborStatement(self) -> str:
		return """\
    neighbor $PEER_ADDRESS peer-group $PEERING_LAN_NAME-group
    neighbor $PEER_ADDRESS remote-as $PEER_ASN"""

class Juniper_vJunos_router(Router):
	kind = "juniper_vjunosrouter"
	config_suffix = ".cfg"



	def getNeighborStatement(self) -> str:
		return """\
            neighbor $PEER_ADDRESS remote-as $PEER_ASN;"""

class Juniper_vJunos_switch(Router):
	kind = "juniper_vjunosswitch"
	config_suffix = ".cfg"



	def getNeighborStatement(self) -> str:
		return """\
            neighbor $PEER_ADDRESS remote-as $PEER_ASN;"""

class Juniper_vJunosEvolved(Router):
	kind = "juniper_vjunosevolved"
	config_suffix = ".cfg"



	def getNeighborStatement(self) -> str:
		return """\
            neighbor $PEER_ADDRESS peer-as $PEER_ASN;"""