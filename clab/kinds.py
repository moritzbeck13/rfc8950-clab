from __future__ import annotations

import asyncio

import clab.constants
import clab.containerlab
import clab.topology



class Bridge(clab.topology.Node):
	KIND = "bridge"
	NAME = "bridge"



	def getName(self) -> str:
		return self.NAME



	def destroy(self):
		clab.containerlab.run(["sudo iptables -vL FORWARD --line-numbers -n | grep 'set by containerlab' | awk '{print $1}' | sort -r | xargs -I {} sudo iptables -D FORWARD {}"])
		clab.containerlab.run(["sudo", "ip", "link", "delete", self.getName()])

	def deploy(self):
		clab.containerlab.run(["sudo", "ip", "link", "add", self.getName(), "type", "bridge"])
		clab.containerlab.run(["sudo", "ip", "link", "set", "dev", self.getName(), "up"])



class Client(clab.topology.Node):
	NAME = "client"



	def getRouter(self) -> Router:
		return self.router

	def setRouter(self, router: Router):
		self.router = router



	def getAddress(self) -> str:
		return clab.constants.CLIENT_LAN_PREFIX + str(self.getID()) + "." + clab.constants.CLIENT_LAN_CLIENT_SUFFIX

class Alpine(Client):
	KIND = "linux"



	def __init__(self, id, **kwargs):
		super().__init__(id, **kwargs)

		self.addAttribute("image", "alpine")



	def generateConfig(self):
		self.addAttribute("exec", [
			"ip address add " + self.getAddress() + "/" + clab.constants.CLIENT_LAN_PREFIX_LENGTH + " dev eth1",
			"ip route del default",
			"ip route add default via " + self.getRouter().getClientLANAddress(),
			"ip link set eth1 up"])



	async def exec(self, cmd: list[str], **kwargs: dict):
		process = await asyncio.create_subprocess_exec(
			*["docker", "exec", self.getContainerName()] + cmd,
			stdout=asyncio.subprocess.PIPE,
			stderr=asyncio.subprocess.PIPE)

		await process.wait()

		data = await process.communicate()

		return {
			"returncode": process.returncode,
			"stdout": data[0].decode().splitlines(),
			"stderr": data[1].decode().splitlines(),
			"kwargs": kwargs}



class Router(clab.topology.Node):
	FILE_EXTENSION = None
	USERNAME = "admin"
	PASSWORD = "admin"
	ROUTE_TABLE = None



	def __init__(self, id: int, **kwargs: dict):
		super().__init__(id, **kwargs)

		self.addAttribute("startup-config", clab.constants.CONFIG_DIR + "/" + self.getName() + self.FILE_EXTENSION)



	def getClient(self) -> Client:
		return self.client

	def setClient(self, client: Client):
		self.client = client



	def getClientLANAddress(self) -> str:
		return clab.constants.CLIENT_LAN_PREFIX + str(self.getID()) + "." + clab.constants.CLIENT_LAN_ROUTER_SUFFIX

	def getPeeringLANAddress(self) -> str:
		return clab.constants.PEERING_LAN_PREFIX + str(self.getID())

	def getLoopbackAddress(self) -> str:
		return clab.constants.ROUTER_LOOPBACK_PREFIX + str(self.getID()) + "." + clab.constants.ROUTER_LOOPBACK_SUFFIX

	def getASN(self) -> int:
		return clab.constants.BASE_ASN + self.getID()



	def getNeighborStatement(self) -> str:
		return None

	def generateConfig(self):
		file = open(clab.constants.FILES_DIR + "/" + clab.constants.TEMPLATE_DIR + "/" + self.NAME + self.FILE_EXTENSION)
		config = file.read()
		file.close()

		neighbor = self.getNeighborStatement()
		neighbor = neighbor.replace("$PEERING_LAN_NAME", clab.constants.PEERING_LAN_NAME)

		neighbors = []

		for peer in self.getTopology().getNodes():
			if isinstance(peer, Router) and peer is not self:
				neighbors.append(neighbor \
					.replace("$PEER_ADDRESS",	peer.getPeeringLANAddress()) \
					.replace("$PEER_ASN",		str(peer.getASN())))

		neighbors = "\n".join(neighbors)

		config = config \
			.replace("$ASN",							str(self.getASN())) \
			.replace("$PEERING_LAN_NAME",				clab.constants.PEERING_LAN_NAME) \
			.replace("$PEERING_LAN_ADDRESS",			self.getPeeringLANAddress()) \
			.replace("$PEERING_LAN_PREFIX_LENGTH",		clab.constants.PEERING_LAN_PREFIX_LENGTH) \
			.replace("$ROUTER_LOOPBACK_NAME",			clab.constants.ROUTER_LOOPBACK_NAME) \
			.replace("$ROUTER_LOOPBACK_ADDRESS",		self.getLoopbackAddress()) \
			.replace("$ROUTER_LOOPBACK_PREFIX_LENGTH",	clab.constants.ROUTER_LOOPBACK_PREFIX_LENGTH) \
			.replace("$ROUTER_LOOPBACK_SUBNET_MASK",	clab.constants.ROUTER_LOOPBACK_SUBNET_MASK) \
			.replace("$CLIENT_LAN_NAME",				clab.constants.CLIENT_LAN_NAME) \
			.replace("$CLIENT_LAN_ADDRESS",				self.getClientLANAddress()) \
			.replace("$CLIENT_LAN_NETWORK",				clab.constants.CLIENT_LAN_PREFIX + str(self.getID()) + ".0") \
			.replace("$CLIENT_LAN_PREFIX_LENGTH",		clab.constants.CLIENT_LAN_PREFIX_LENGTH) \
			.replace("$CLIENT_LAN_SUBNET_MASK",			clab.constants.CLIENT_LAN_SUBNET_MASK) \
			.replace("$NEIGHBORS",						neighbors)

		file = open(clab.constants.FILES_DIR + "/" + clab.constants.CONFIG_DIR + "/" + self.getName() + self.FILE_EXTENSION, "w")
		file.write(config)
		file.close()



class Nokia_SR_Linux(Router):
	KIND = "nokia_srlinux"
	NAME = "nokia_srlinux"
	INTERFACE_PREFIX = "e1-"
	FILE_EXTENSION = ".json"
	PASSWORD = "NokiaSrl1!"
	ROUTE_TABLE = ["show", "network-instance", "route-table", "all"]



	def getNeighborStatement(self) -> str:
		return """\
            neighbor $PEER_ADDRESS {
                peer-as $PEER_ASN
                peer-group $PEERING_LAN_NAME_group
            }"""



class Nokia_SR_OS(Router):
	KIND = "nokia_sros"
	NAME = "nokia_sros"
	FILE_EXTENSION = ".partial.txt"
	ROUTE_TABLE = ["show", "router", "route-table", "all"]



	def getNeighborStatement(self) -> str:
		return """\
            neighbor "$PEER_ADDRESS" {
                group "$PEERING_LAN_NAME_group"
                peer-as $PEER_ASN
            }"""



class Arista(Router):
	ROUTE_TABLE = ["show", "ip", "route", "detail"]



	def getNeighborStatement(self) -> str:
		return """\
   neighbor $PEER_ADDRESS peer group $PEERING_LAN_NAME_group
   neighbor $PEER_ADDRESS remote-as $PEER_ASN"""

class Arista_cEOS(Arista):
	KIND = "arista_ceos"
	NAME = "arista_ceos"
	FILE_EXTENSION = ""

class Arista_vEOS(Arista):
	KIND = "arista_veos"
	NAME = "arista_veos"
	FILE_EXTENSION = ".cfg"



class Cisco(Router):
	USERNAME = "clab"
	PASSWORD = "clab@123"

class Cisco_IOS_XR(Cisco):
	def getNeighborStatement(self) -> str:
		return """\
 neighbor $PEER_ADDRESS
  remote-as $PEER_ASN
  use neighbor-group $PEERING_LAN_NAME_group
 """

class Cisco_XRd(Cisco_IOS_XR):
	KIND = "cisco_xrd"
	NAME = "cisco_xrd"
	FILE_EXTENSION = ".cfg"
	INTERFACE_PREFIX = "Gi0-0-0-"

class Cisco_XRv9k(Cisco_IOS_XR):
	KIND = "cisco_xrv9k"
	NAME = "cisco_xrv9k"
	FILE_EXTENSION = ".partial.cfg"
	INTERFACE_PREFIX = "Gi0/0/0/"



class Juniper(Router):
	FILE_EXTENSION = ".cfg"
	PASSWORD = "admin@123"
	ROUTE_TABLE = ["show", "route", "all", "detail"]



	def getNeighborStatement(self) -> str:
		return """\
            neighbor $PEER_ADDRESS {
                peer-as $PEER_ASN;
            }"""

class Juniper_vJunos_router(Juniper):
	KIND = "juniper_vjunosrouter"
	NAME = "juniper_vjunosrouter"

class Juniper_vJunos_switch(Juniper):
	KIND = "juniper_vjunosswitch"
	NAME = "juniper_vjunosswitch"

class Juniper_vJunosEvolved(Juniper):
	KIND = "juniper_vjunosevolved"
	NAME = "juniper_vjunosevolved"



class BIRD(Router):
	KIND = "linux"
	FILE_EXTENSION = ".conf"
	ROUTE_TABLE = ["show", "route", "all"]



	def __init__(self, id: int, **kwargs: dict):
		super().__init__(id, **kwargs)

		self.addAttribute("binds", [clab.constants.CONFIG_DIR + "/" + self.getName() + self.FILE_EXTENSION + ":/etc/bird.conf"])



	def getNeighborStatement(self) -> str:
		return """\
protocol bgp from $PEERING_LAN_NAME_template {
  	neighbor $PEER_ADDRESS as $PEER_ASN;
}"""

	def generateConfig(self):
		super().generateConfig()

		self.addAttribute("exec", [
			"ip address add " + self.getLoopbackAddress() + "/" + clab.constants.ROUTER_LOOPBACK_PREFIX_LENGTH + " dev lo",
			"ip link set lo up",
			"ip address add " + self.getPeeringLANAddress() + "/" + clab.constants.PEERING_LAN_PREFIX_LENGTH + " dev eth1",
			"ip link set eth1 up",
			"ip address add " + self.getClientLANAddress() + "/" + clab.constants.CLIENT_LAN_PREFIX_LENGTH + " dev eth2",
			"ip link set eth2 up"])

class BIRD2(BIRD):
	NAME = "bird2"

class BIRD3(BIRD):
	NAME = "bird3"



class FRR(Router):
	KIND = "linux"
	NAME = "frr"
	FILE_EXTENSION = ".conf"
	ROUTE_TABLE = ["vtysh", "show", "ip", "route"]



	def __init__(self, id: int, **kwargs: dict):
		super().__init__(id, **kwargs)

		self.addAttribute("binds", [
			clab.constants.CONFIG_DIR + "/" + self.getName() + self.FILE_EXTENSION + ":/etc/frr/frr.conf",
			clab.constants.TEMPLATE_DIR + "/daemons:/etc/frr/daemons",
			clab.constants.TEMPLATE_DIR + "/vtysh.conf:/etc/frr/vtysh.conf"])



	def getNeighborStatement(self):
		return """\
 neighbor $PEER_ADDRESS remote-as $PEER_ASN
 neighbor $PEER_ADDRESS peer-group $PEERING_LAN_NAME_group"""