import Clab.Containerlab
import Clab.Topology



class Bridge(Clab.Topology.Node):
	name = "bridge"
	port_prefix = "eth"

class Linux(Clab.Topology.Node):
	name = "linux"
	port_prefix = "eth"



	def __init__(self, name: str, id: int, **kwargs):
		super().__init__(name, id, **kwargs)

		id_str = str(id)

		self.setAttribute("exec", [
				"ip address add " + Clab.Containerlab.Constants.CLIENT_LAN_PREFIX + id_str + "." + Clab.Containerlab.Constants.CLIENT_LAN_CLIENT_SUFFIX + "/" + Clab.Containerlab.Constants.CLIENT_LAN_PREFIX_LENGTH + " dev eth1",
				"ip route del default",
				"ip route add default via " + Clab.Containerlab.Constants.CLIENT_LAN_PREFIX + id_str + "." + Clab.Containerlab.Constants.CLIENT_LAN_ROUTER_SUFFIX,
				"ip link set eth1 up"])



class Nokia_SR_Linux(Clab.Topology.Router):
	#"route-table": "show network-instance default route-table ipv4-unicast prefix $PREFIX",
	#"bgp-routes": "show network-instance default protocols bgp routes ipv4 prefix $PREFIX",
	#"bgp-received-routes": "show network-instance default protocols bgp neighbor $NEIGHBOR received-routes ipv4"

	name = "nokia_srlinux"
	port_prefix = "e1-"
	config_suffix = ".json"



	def getNeighborStatement(self) -> str:
		return """
            neighbor $PEER_ADDRESS {
                peer-group "$PEERING_LAN_NAME-group"
                peer-as $PEER_ASN
            }"""

class Nokia_SR_OS(Clab.Topology.Router):
	name = "nokia_sros"
	port_prefix = "eth"
	config_suffix = ".partial.cfg"



	def getNeighborStatement(self) -> str:
		return """
            neighbor $PEER_ADDRESS {
                group "$PEERING_LAN_NAME-group"
                peer-as $PEER_ASN
            }"""

class Arista_cEOS(Clab.Topology.Router):
	name = "arista_ceos"
	port_prefix = "eth"
	config_suffix = ".conf"



	def getNeighborStatement(self) -> str:
			return """
    neighbor $PEER_ADDRESS peer group $PEERING_LAN_NAME-group
    neighbor $PEER_ADDRESS remote-as $PEER_ASN"""

class Arista_vEOS(Clab.Topology.Router):
	name = "arista_veos"
	port_prefix = "eth"
	config_suffix = ".conf"



	def getNeighborStatement(self) -> str:
			return """
    neighbor $PEER_ADDRESS peer group $PEERING_LAN_NAME-group
    neighbor $PEER_ADDRESS remote-as $PEER_ASN"""