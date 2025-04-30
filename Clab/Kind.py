import Clab.Containerlab
import Clab.Topology



class Bridge(Clab.Topology.Node):
	name = "bridge"

class Linux(Clab.Topology.Node):
	name = "linux"



	def __init__(self, name: str, id: int, **kwargs):
		super().__init__(name, id, **kwargs)

		id_str = str(id)

		self.setAttribute("exec", [
				"ip address add " + Clab.Containerlab.Constants.CLIENT_LAN_PREFIX + id_str + "." + Clab.Containerlab.Constants.CLIENT_LAN_CLIENT_SUFFIX + "/" + Clab.Containerlab.Constants.CLIENT_LAN_PREFIX_LENGTH + " dev eth1",
				"ip route del default",
				"ip route add default via " + Clab.Containerlab.Constants.CLIENT_LAN_PREFIX + id_str + "." + Clab.Containerlab.Constants.CLIENT_LAN_ROUTER_SUFFIX,
				"ip link set eth1 up"])



class Nokia_SR_Linux(Clab.Topology.Router):
	name = "nokia_srlinux"
	port_prefix = "e1-"
	config_suffix = ".json"



	def getNeighborStatement(self) -> str:
		return """\
            neighbor $PEER_ADDRESS {
                peer-group "$PEERING_LAN_NAME-group"
                peer-as $PEER_ASN
            }"""

class Nokia_SR_OS(Clab.Topology.Router):
	name = "nokia_sros"
	config_suffix = ".partial.txt"



	def getNeighborStatement(self) -> str:
		return """\
            neighbor $PEER_ADDRESS {
                group "$PEERING_LAN_NAME-group"
                peer-as $PEER_ASN
            }"""

class Arista_cEOS(Clab.Topology.Router):
	name = "arista_ceos"
	config_suffix = ""



	def getNeighborStatement(self) -> str:
		return """\
    neighbor $PEER_ADDRESS peer group $PEERING_LAN_NAME-group
    neighbor $PEER_ADDRESS remote-as $PEER_ASN"""

class Arista_vEOS(Clab.Topology.Router):
	name = "arista_veos"
	config_suffix = ".cfg"



	def getNeighborStatement(self) -> str:
		return """\
    neighbor $PEER_ADDRESS peer group $PEERING_LAN_NAME-group
    neighbor $PEER_ADDRESS remote-as $PEER_ASN"""

class Juniper_vJunos_router(Clab.Topology.Router):
	name = "juniper_vjunosrouter"
	config_suffix = ".cfg"



	def getNeighborStatement(self) -> str:
		return """\
            neighbor $PEER_ADDRESS remote-as $PEER_ASN;"""

class Juniper_vJunos_switch(Clab.Topology.Router):
	name = "juniper_vjunosswitch"
	config_suffix = ".cfg"



	def getNeighborStatement(self) -> str:
		return """\
            neighbor $PEER_ADDRESS remote-as $PEER_ASN;"""

class Juniper_vJunosEvolved(Clab.Topology.Router):
	name = "juniper_vjunosevolved"
	config_suffix = ".cfg"



	def getNeighborStatement(self) -> str:
		return """\
            neighbor $PEER_ADDRESS peer-as $PEER_ASN;"""