import clab.Containerlab
import clab.Topology



class Bridge(clab.Topology.Node):
	name = "bridge"

class Linux(clab.Topology.Node):
	name = "linux"



	def __init__(self, name: str, id: int, **kwargs):
		super().__init__(name, id, **kwargs)

		id_str = str(id)

		self.setAttribute("exec", [
				"ip address add " + clab.Containerlab.clab.Constants.CLIENT_LAN_PREFIX + id_str + "." + clab.Containerlab.clab.Constants.CLIENT_LAN_CLIENT_SUFFIX + "/" + clab.Containerlab.clab.Constants.CLIENT_LAN_PREFIX_LENGTH + " dev eth1",
				"ip route del default",
				"ip route add default via " + clab.Containerlab.clab.Constants.CLIENT_LAN_PREFIX + id_str + "." + clab.Containerlab.clab.Constants.CLIENT_LAN_ROUTER_SUFFIX,
				"ip link set eth1 up"])



class Nokia_SR_Linux(clab.Topology.Router):
	name = "nokia_srlinux"
	port_prefix = "e1-"
	config_suffix = ".json"



	def getNeighborStatement(self) -> str:
		return """\
            neighbor $PEER_ADDRESS {
                peer-group "$PEERING_LAN_NAME-group"
                peer-as $PEER_ASN
            }"""

class Nokia_SR_OS(clab.Topology.Router):
	name = "nokia_sros"
	config_suffix = ".partial.txt"



	def getNeighborStatement(self) -> str:
		return """\
            neighbor $PEER_ADDRESS {
                group "$PEERING_LAN_NAME-group"
                peer-as $PEER_ASN
            }"""

class Arista_cEOS(clab.Topology.Router):
	name = "arista_ceos"
	config_suffix = ""



	def getNeighborStatement(self) -> str:
		return """\
    neighbor $PEER_ADDRESS peer group $PEERING_LAN_NAME-group
    neighbor $PEER_ADDRESS remote-as $PEER_ASN"""

class Arista_vEOS(clab.Topology.Router):
	name = "arista_veos"
	config_suffix = ".cfg"



	def getNeighborStatement(self) -> str:
		return """\
    neighbor $PEER_ADDRESS peer group $PEERING_LAN_NAME-group
    neighbor $PEER_ADDRESS remote-as $PEER_ASN"""

class Cisco_XRv9k(clab.Topology.Router):
	name = "cisco_xrv9k"
	config_suffix = ".partial.cfg"



	def getNeighborStatement(self) -> str:
		return """\
    neighbor $PEER_ADDRESS peer-group $PEERING_LAN_NAME-group
    neighbor $PEER_ADDRESS remote-as $PEER_ASN"""

class Juniper_vJunos_router(clab.Topology.Router):
	name = "juniper_vjunosrouter"
	config_suffix = ".cfg"



	def getNeighborStatement(self) -> str:
		return """\
            neighbor $PEER_ADDRESS remote-as $PEER_ASN;"""

class Juniper_vJunos_switch(clab.Topology.Router):
	name = "juniper_vjunosswitch"
	config_suffix = ".cfg"



	def getNeighborStatement(self) -> str:
		return """\
            neighbor $PEER_ADDRESS remote-as $PEER_ASN;"""

class Juniper_vJunosEvolved(clab.Topology.Router):
	name = "juniper_vjunosevolved"
	config_suffix = ".cfg"



	def getNeighborStatement(self) -> str:
		return """\
            neighbor $PEER_ADDRESS peer-as $PEER_ASN;"""