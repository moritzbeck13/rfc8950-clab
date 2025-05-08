import clab.Constants
import clab.Containerlab
import clab.Topology



class Bridge(clab.Topology.Node):
	KIND = "bridge"
	NAME = "bridge"

	def destroy(self):
		clab.Containerlab.runOnHost("sudo iptables -vL FORWARD --line-numbers -n | grep 'set by containerlab' | awk '{print $1}' | sort -r | xargs -I {} sudo iptables -D FORWARD {}")
		clab.Containerlab.runOnHost("sudo ip link delete " + self.getName())

	def deploy(self):
		clab.Containerlab.runOnHost("sudo ip link add " + self.getName() + " type bridge")
		clab.Containerlab.runOnHost("sudo ip link set dev " + self.getName() + " up")



class Alpine(clab.Topology.Node):
	KIND = "linux"
	NAME = "client"

	def __init__(self, id: int, **kwargs: dict):
		super().__init__(id, **kwargs)

		id_str = str(id)

		self.addAttribute("exec", [
			"ip address add " + clab.Constants.CLIENT_LAN_PREFIX + id_str + "." + clab.Constants.CLIENT_LAN_CLIENT_SUFFIX + "/" + clab.Constants.CLIENT_LAN_PREFIX_LENGTH + " dev eth1",
			"ip route del default",
			"ip route add default via " + clab.Constants.CLIENT_LAN_PREFIX + id_str + "." + clab.Constants.CLIENT_LAN_ROUTER_SUFFIX,
			"ip link set eth1 up"])
		self.addAttribute("image", "alpine")



class Router(clab.Topology.Node):
	FILE_EXTENSION = None

	def __init__(self, id: int, **kwargs: dict):
		super().__init__(id, **kwargs)

		self.addAttribute("startup-config", clab.Constants.CONFIG_DIR + "/" + self.getName() + self.FILE_EXTENSION)

	def getNeighborStatement(self) -> str:
		return None

	def generateConfig(self, peers: list[clab.Topology.Node]):
		file = open(clab.Constants.FILES_DIR + "/" + clab.Constants.TEMPLATE_DIR + "/" + self.NAME + self.FILE_EXTENSION)
		config = file.read()
		file.close()

		neighbor = self.getNeighborStatement()
		neighbor = neighbor.replace("$PEERING_LAN_NAME", clab.Constants.PEERING_LAN_NAME)

		neighbors = []

		for peer in peers:
			if isinstance(peer, Router) and peer is not self:
				peer_id = peer.getID()

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

		file = open(clab.Constants.FILES_DIR + "/" + clab.Constants.CONFIG_DIR + "/" + self.getName() + self.FILE_EXTENSION, "w")
		file.write(config)
		file.close()



class Nokia_SR_Linux(Router):
	KIND = "nokia_srlinux"
	NAME = "nokia_srlinux"
	INTERFACE_PREFIX = "e1-"
	FILE_EXTENSION = ".json"

	def getNeighborStatement(self) -> str:
		return """\
            neighbor $PEER_ADDRESS {
                peer-group "$PEERING_LAN_NAME_group"
                peer-as $PEER_ASN
            }"""



class Nokia_SR_OS(Router):
	KIND = "nokia_sros"
	NAME = "nokia_sros"
	FILE_EXTENSION = ".partial.txt"

	def getNeighborStatement(self) -> str:
		return """\
            neighbor $PEER_ADDRESS {
                group "$PEERING_LAN_NAME_group"
                peer-as $PEER_ASN
            }"""



class Arista_cEOS(Router):
	KIND = "arista_ceos"
	NAME = "arista_ceos"
	FILE_EXTENSION = ""

	def getNeighborStatement(self) -> str:
		return """\
    neighbor $PEER_ADDRESS peer group $PEERING_LAN_NAME_group
    neighbor $PEER_ADDRESS remote-as $PEER_ASN"""



class Arista_vEOS(Router):
	KIND = "arista_veos"
	NAME = "arista_veos"
	FILE_EXTENSION = ".cfg"

	def getNeighborStatement(self) -> str:
		return """\
    neighbor $PEER_ADDRESS peer group $PEERING_LAN_NAME_group
    neighbor $PEER_ADDRESS remote-as $PEER_ASN"""



class Cisco_XRv9k(Router):
	KIND = "cisco_xrv9k"
	NAME = "cisco_xrv9k"
	FILE_EXTENSION = ".partial.cfg"

	def getNeighborStatement(self) -> str:
		return """\
    neighbor $PEER_ADDRESS peer-group $PEERING_LAN_NAME_group
    neighbor $PEER_ADDRESS remote-as $PEER_ASN"""



class Juniper_vJunos_router(Router):
	KIND = "juniper_vjunosrouter"
	NAME = "juniper_vjunosrouter"
	FILE_EXTENSION = ".cfg"

	def getNeighborStatement(self) -> str:
		return """\
            neighbor $PEER_ADDRESS remote-as $PEER_ASN;"""



class Juniper_vJunos_switch(Router):
	KIND = "juniper_vjunosswitch"
	NAME = "juniper_vjunosswitch"
	FILE_EXTENSION = ".cfg"

	def getNeighborStatement(self) -> str:
		return """\
            neighbor $PEER_ADDRESS remote-as $PEER_ASN;"""



class Juniper_vJunosEvolved(Router):
	KIND = "juniper_vjunosevolved"
	NAME = "juniper_vjunosevolved"
	FILE_EXTENSION = ".cfg"

	def getNeighborStatement(self) -> str:
		return """\
            neighbor $PEER_ADDRESS peer-as $PEER_ASN;"""



class BIRD(Router):
	KIND = "linux"
	NAME = "bird"
	FILE_EXTENSION = ".conf"

	def __init__(self, id: int, **kwargs: dict):
		super().__init__(id, **kwargs)

		id_str = str(id)

		self.addAttribute("binds", [clab.Constants.CONFIG_DIR + "/" + self.getName() + self.FILE_EXTENSION + ":/etc/bird.conf"])
		self.addAttribute("exec", [
			"ip address add " + clab.Constants.PEERING_LAN_PREFIX + id_str + "/" + clab.Constants.PEERING_LAN_PREFIX_LENGTH + " dev eth1",
			"ip link set eth1 up",
			"ip address add " + clab.Constants.CLIENT_LAN_PREFIX + id_str + "." + clab.Constants.CLIENT_LAN_ROUTER_SUFFIX + "/" + clab.Constants.CLIENT_LAN_PREFIX_LENGTH + " dev eth2",
			"ip link set eth2 up"])

	def getNeighborStatement(self) -> str:
		return """\
protocol bgp from $PEERING_LAN_NAME_template {
  	neighbor $PEER_ADDRESS as $PEER_ASN;
}"""



class FRR(Router):
	KIND = "linux"
	NAME = "frr"
	FILE_EXTENSION = ".conf"

	def __init__(self, id: int, **kwargs: dict):
		super().__init__(id, **kwargs)

		self.addAttribute("binds", [
			clab.Constants.CONFIG_DIR + "/" + self.getName() + self.FILE_EXTENSION + ":/etc/frr/frr.conf",
			clab.Constants.TEMPLATE_DIR + "/daemons:/etc/frr/daemons",
			clab.Constants.TEMPLATE_DIR + "/vtysh.conf:/etc/frr/vtysh.conf"])

	def getNeighborStatement(self):
		return """\
    neighbor $PEER_ADDRESS remote-as $PEER_ASN
    neighbor $PEER_ADDRESS peer-group $PEERING_LAN_NAME_group"""