from __future__ import annotations

import asyncio

import clab.constants
import clab.containerlab
import clab.topology



class Bridge(clab.topology.Node):
	KIND = "bridge"
	NAME = "bridge"

	def get_name(self) -> str:
		return self.topology.lab.name

	def post_destroy(self):
		#clab.containerlab.exec(["sudo", "ip", "link", "delete", self.get_name()])
		#clab.containerlab.exec(["sudo iptables -vL FORWARD --line-numbers -n | grep 'set by containerlab' | awk '{print $1}' | sort -r | xargs -I {} sudo iptables -D FORWARD {}"])
		pass

	def pre_deploy(self):
		clab.containerlab.exec(["sudo", "ip", "link", "add", self.get_name(), "type", "bridge"])
		clab.containerlab.exec(["sudo", "ip", "link", "set", "dev", self.get_name(), "up"])

class Client(clab.topology.Node):
	NAME = "client"

	def __init__(self, id, **kwargs):
		super().__init__(id, **kwargs)

		self.default_gateway: clab.topology.Interface = None

class Alpine(Client):
	KIND = "linux"

	def __init__(self, id, **kwargs):
		super().__init__(id, **kwargs)

		self.add_attribute("image", "alpine")

	def export(self):
		exec = []

		for _, interface in self.interfaces.items():
			interface_name = interface.get_name()

			if interface.ipv4 is not None:
				exec.append("ip address add " + str(interface.ipv4) + " dev " + interface_name)
			if interface.ipv6 is not None:
				exec.append("ip -6 address add " + str(interface.ipv6) + " dev " + interface_name)

			exec.append("ip link set " + interface_name + " up")

		if self.default_gateway is not None:
			if self.default_gateway.ipv4 is not None:
				exec.append("ip route del default")
				exec.append("ip route add default via " + str(self.default_gateway.connected_to.ipv4.ip))
			if self.default_gateway.ipv6 is not None:
				exec.append("ip -6 route del default")
				exec.append("ip -6 route add default via " + str(self.default_gateway.connected_to.ipv6.ip))
 
		self.add_attribute("exec", exec)

	async def exec(self, cmd: list[str], **kwargs: dict):
		process = await asyncio.create_subprocess_exec(
			*["docker", "exec", self.get_container_name()] + cmd,
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

	def __init__(self, id: int, **kwargs: dict):
		super().__init__(id, **kwargs)

		self.add_attribute("startup-config", clab.constants.CONFIG_DIR + "/" + self.get_name() + self.FILE_EXTENSION)

	def get_ASN(self) -> int:
		return clab.constants.BASE_ASN + self.id

	def get_IPv4_interface_statement(self) -> str:
		pass

	def get_IPv6_interface_statement(self) -> str:
		pass

	def get_BGP_neighbor_statement(self) -> str:
		pass

	def export(self):
		file = open(clab.constants.FILES_DIR + "/" + clab.constants.TEMPLATE_DIR + "/" + self.NAME + self.FILE_EXTENSION)
		config = file.read()
		file.close()

		neighbor_statement = self.get_BGP_neighbor_statement() \
			.replace("$PEERING_LAN_NAME", clab.constants.PEERING_LAN_NAME)

		neighbors = []

		for node in self.topology.nodes:
			if isinstance(node, Router) and node is not self:
				neighbors.append(neighbor_statement \
					.replace("$NEIGHBOR_ADDRESS",	str(node.interfaces[clab.constants.PEERING_LAN_NAME].ipv6.ip)) \
					.replace("$NEIGHBOR_ASN",		str(node.get_ASN())))

		neighbors = "\n".join(neighbors)

		config = config \
			.replace("$ASN",				str(self.get_ASN())) \
			.replace("$PEERING_LAN_NAME",	clab.constants.PEERING_LAN_NAME) \
			.replace("$LOOPBACK_NAME",		clab.constants.LOOPBACK_NAME) \
			.replace("$CLIENT_LAN_NAME",	clab.constants.CLIENT_LAN_NAME) \
			.replace("$NEIGHBORS",			neighbors)

		for kind, interface in self.interfaces.items():
			interface_prefix = "$" + kind.upper()

			if interface.ipv4 is None:
				config = config \
					.replace(interface_prefix + "_IPv4_INTERFACE", "")
			else:
				interface_statement = self.get_IPv4_interface_statement() \
					.replace("$INTERFACE", interface_prefix)

				config = config \
					.replace(interface_prefix + "_IPv4_INTERFACE",			interface_statement) \
			  		.replace(interface_prefix + "_IPv4_IP_ADDRESS",			str(interface.ipv4.ip)) \
					.replace(interface_prefix + "_IPv4_PREFIX_LENGTH",		str(interface.ipv4.network.prefixlen)) \
					.replace(interface_prefix + "_IPv4_SUBNET_MASK",		str(interface.ipv4.netmask)) \
					.replace(interface_prefix + "_IPv4_NETWORK_ADDRESS",	str(interface.ipv4.network.network_address))

			if interface.ipv6 is None:
				config = config \
					.replace(interface_prefix + "_IPv6_INTERFACE", "")
			else:
				interface_statement = self.get_IPv6_interface_statement() \
					.replace("$INTERFACE", interface_prefix)

				config = config \
					.replace(interface_prefix + "_IPv6_INTERFACE",			interface_statement) \
			  		.replace(interface_prefix + "_IPv6_IP_ADDRESS",			str(interface.ipv6.ip)) \
					.replace(interface_prefix + "_IPv6_PREFIX_LENGTH",		str(interface.ipv6.network.prefixlen)) \
					.replace(interface_prefix + "_IPv6_SUBNET_MASK",		str(interface.ipv6.netmask)) \
					.replace(interface_prefix + "_IPv6_NETWORK_ADDRESS",	str(interface.ipv6.network.network_address))

		file = open(clab.constants.FILES_DIR + "/" + clab.constants.CONFIG_DIR + "/" + self.get_name() + self.FILE_EXTENSION, "w")
		file.write(config)
		file.close()

class Arista(Router):
	def get_IPv4_interface_statement(self) -> str:
		return """\
   ip address $INTERFACE_IPv4_IP_ADDRESS/$INTERFACE_IPv4_PREFIX_LENGTH"""

	def get_IPv6_interface_statement(self) -> str:
		return """\
   ipv6 address $INTERFACE_IPv6_IP_ADDRESS/$INTERFACE_IPv6_PREFIX_LENGTH"""

	def get_BGP_neighbor_statement(self) -> str:
		return """\
   neighbor $NEIGHBOR_ADDRESS peer group $PEERING_LAN_NAME_group
   neighbor $NEIGHBOR_ADDRESS remote-as $NEIGHBOR_ASN"""

class Arista_cEOS(Arista):
	KIND = "arista_ceos"
	NAME = "arista_ceos"
	FILE_EXTENSION = ""

class Arista_vEOS(Arista):
	KIND = "arista_veos"
	NAME = "arista_veos"
	FILE_EXTENSION = ".cfg"

class Cisco_IOS_XR(Router):
	USERNAME = "clab"
	PASSWORD = "clab@123"

	def get_IPv4_interface_statement(self) -> str:
		return """\
 ipv4 address $INTERFACE_IPv4_IP_ADDRESS $INTERFACE_IPv4_SUBNET_MASK"""

	def get_IPv6_interface_statement(self) -> str:
		return """\
 ipv6 address $INTERFACE_IPv6_IP_ADDRESS/$INTERFACE_IPv6_PREFIX_LENGTH"""

	def get_BGP_neighbor_statement(self) -> str:
		return """\
 neighbor $NEIGHBOR_ADDRESS
  remote-as $NEIGHBOR_ASN
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

	def get_IPv4_interface_statement(self) -> str:
		return """\
            family inet {
                address $INTERFACE_IPv4_IP_ADDRESS/$INTERFACE_IPv4_PREFIX_LENGTH;
            }"""
	
	def get_IPv6_interface_statement(self) -> str:
		return """\
            family inet6 {
                address $INTERFACE_IPv6_IP_ADDRESS/$INTERFACE_IPv6_PREFIX_LENGTH;
            }"""

	def get_BGP_neighbor_statement(self) -> str:
		return """\
            neighbor $NEIGHBOR_ADDRESS {
                peer-as $NEIGHBOR_ASN;
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

class Nokia_SR_Linux(Router):
	KIND = "nokia_srlinux"
	NAME = "nokia_srlinux"
	INTERFACE_PREFIX = "e1-"
	FILE_EXTENSION = ".json"
	PASSWORD = "NokiaSrl1!"

	def get_IPv4_interface_statement(self) -> str:
		return """\
        ipv4 {
            admin-state enable
            address $INTERFACE_IPv4_IP_ADDRESS/$INTERFACE_IPv4_PREFIX_LENGTH {
            }
        }"""

	def get_IPv6_interface_statement(self) -> str:
		return """\
        ipv6 {
            admin-state enable
            address $INTERFACE_IPv6_IP_ADDRESS/$INTERFACE_IPv6_PREFIX_LENGTH {
            }
        }"""

	def get_BGP_neighbor_statement(self) -> str:
		return """\
            neighbor $NEIGHBOR_ADDRESS {
                peer-as $NEIGHBOR_ASN
                peer-group $PEERING_LAN_NAME_group
            }"""

class Nokia_SR_OS(Router):
	KIND = "nokia_sros"
	NAME = "nokia_sros"
	FILE_EXTENSION = ".partial.txt"

	def get_IPv4_interface_statement(self) -> str:
		return """\
            ipv4 {
                primary {
                    address $INTERFACE_IPv4_IP_ADDRESS
                    prefix-length $INTERFACE_IPv4_PREFIX_LENGTH
                }
            }"""

	def get_IPv6_interface_statement(self) -> str:
		return """\
            ipv6 {
                forward-ipv4-packets true
                address $INTERFACE_IPv6_IP_ADDRESS {
                    prefix-length $INTERFACE_IPv6_PREFIX_LENGTH
                }
            }"""

	def get_BGP_neighbor_statement(self) -> str:
		return """\
            neighbor "$NEIGHBOR_ADDRESS" {
                group "$PEERING_LAN_NAME_group"
                peer-as $NEIGHBOR_ASN
            }"""

class Route_Server(Router):
	def export(self):
		super().export()

		self.add_attribute("exec", [
			"ip address add " + str(self.interfaces[clab.constants.LOOPBACK_NAME].ipv4) + " dev lo",
			"ip link set lo up",
			"ip address add " + str(self.interfaces[clab.constants.PEERING_LAN_NAME].ipv6) + " dev eth1",
			"ip link set eth1 up",
			"ip address add " + str(self.interfaces[clab.constants.CLIENT_LAN_NAME].ipv4) + " dev eth2",
			"ip link set eth2 up"])

	def get_IPv4_interface_statement(self):
		return ""

	def get_IPv6_interface_statement(self):
		return ""

class BIRD(Route_Server):
	KIND = "linux"
	FILE_EXTENSION = ".conf"

	def __init__(self, id: int, **kwargs: dict):
		super().__init__(id, **kwargs)

		self.add_attribute("binds", [clab.constants.CONFIG_DIR + "/" + self.get_name() + self.FILE_EXTENSION + ":/etc/bird.conf"])

	def get_BGP_neighbor_statement(self) -> str:
		return """\
protocol bgp from $PEERING_LAN_NAME_template {
  	neighbor $NEIGHBOR_ADDRESS as $NEIGHBOR_ASN;
}"""

class BIRD2(BIRD):
	NAME = "bird2"

class BIRD3(BIRD):
	NAME = "bird3"

class FRR(Route_Server):
	KIND = "linux"
	NAME = "frr"
	FILE_EXTENSION = ".conf"

	def __init__(self, id: int, **kwargs: dict):
		super().__init__(id, **kwargs)

		self.add_attribute("binds", [
			clab.constants.CONFIG_DIR + "/" + self.get_name() + self.FILE_EXTENSION + ":/etc/frr/frr.conf",
			clab.constants.TEMPLATE_DIR + "/daemons:/etc/frr/daemons",
			clab.constants.TEMPLATE_DIR + "/vtysh.conf:/etc/frr/vtysh.conf"])

	def get_BGP_neighbor_statement(self):
		return """\
 neighbor $NEIGHBOR_ADDRESS remote-as $NEIGHBOR_ASN
 neighbor $NEIGHBOR_ADDRESS peer-group $PEERING_LAN_NAME_group"""

class OpenBGPD(Route_Server):
	KIND = "linux"
	NAME = "openbgpd"
	FILE_EXTENSION = ".conf"

	def __init__(self, id: int, **kwargs: dict):
		super().__init__(id, **kwargs)

		self.add_attribute("binds", [
			clab.constants.CONFIG_DIR + "/" + self.get_name() + self.FILE_EXTENSION + ":/etc/bgpd/bgpd.conf"])

	def get_BGP_neighbor_statement(self):
		return """\
	neighbor $NEIGHBOR_ADDRESS {
		remote-as $NEIGHBOR_ASN
	}"""