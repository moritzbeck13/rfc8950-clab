from __future__ import annotations

import asyncio
import ipaddress

import clab.containerlab
import clab.topology



BASE_ASN = 65000



class Bridge(clab.topology.Node):
	KIND = "bridge"
	NAME = "bridge"

	def __init__(self, name: str, **kwargs: dict):
		super().__init__(None, **kwargs)

		self.name: str = name

	def get_name(self) -> str:
		return self.name

	def post_destroy(self):
		clab.containerlab.exec(["sudo", "ip", "link", "delete", self.get_name()])
		clab.containerlab.exec(["sudo iptables -vL FORWARD --line-numbers -n | grep 'set by containerlab' | awk '{print $1}' | sort -r | xargs -I {} sudo iptables -D FORWARD {}"])

	def pre_deploy(self):
		clab.containerlab.exec(["sudo", "ip", "link", "add", self.get_name(), "type", "bridge"])
		clab.containerlab.exec(["sudo", "ip", "link", "set", "dev", self.get_name(), "up"])

class Client(clab.topology.Node):
	NAME = "client"

	def __init__(self, id: int, **kwargs: dict):
		super().__init__(id, **kwargs)

		self.default_gateway: clab.topology.Interface = None

class Alpine(Client):
	KIND = "linux"

	def __init__(self, id: int, **kwargs: dict):
		super().__init__(id, **kwargs)

		self.add_attribute("image", "alpine")

	def export(self):
		exec: list[str] = []

		interface_name: str

		for interface in self.interfaces:
			if interface.number is None:
				interface_name = self.LOOPBACK_PREFIX
			else:
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
			"command": " ".join(cmd),
			"returncode": process.returncode,
			"stdout": data[0].decode().splitlines(),
			"stderr": data[1].decode().splitlines(),
			"kwargs": kwargs}

class Router(clab.topology.Node):
	FILE_EXTENSION = None

	USERNAME = "admin"
	PASSWORD = "admin"

	STATEMENT_IPV4_ADDRESSING = ""
	STATEMENT_NO_IPV4_ADDRESSING = ""
	STATEMENT_IPV6_ADDRESSING = ""
	STATEMENT_NO_IPV6_ADDRESSING = ""
	STATEMENT_BGP_NEIGHBOR = None



	def __init__(self, id: int, **kwargs: dict):
		super().__init__(id, **kwargs)

		self.peers: list[tuple[Router, ipaddress.IPv4Interface | ipaddress.IPv6Interface]] = []

		self.add_attribute("startup-config", "configs/" + self.get_name() + self.FILE_EXTENSION)

	def get_ASN(self) -> int:
		return BASE_ASN + self.id

	def export(self):
		file = open("files/templates/" + self.NAME + self.FILE_EXTENSION)
		config: str = file.read()
		file.close()

		neighbors: list[Router] = []

		for peer, interface in self.peers:
			if peer is not self:
				neighbors.append(self.STATEMENT_BGP_NEIGHBOR \
					.replace("$BGP_NEIGHBOR_IP_ADDRESS",	str(interface.ip)) \
					.replace("$BGP_NEIGHBOR_ASN",			str(peer.get_ASN()))
					.replace("$BGP_NEIGHBOR_ID",			str(peer.id)))

		neighbors: str = "\n".join(neighbors)

		config = config \
			.replace("$BGP_NEIGHBORS",	neighbors) \
			.replace("$BGP_ASN",		str(self.get_ASN())) \
			.replace("$BGP_ROUTER_ID",	"$LOOPBACK_IPV4_IP_ADDRESS") \
			.replace("$BGP_GROUP_NAME",	"$PEERING_LAN_NAME") \

		for interface in self.interfaces:
			prefix: str = "$" + interface.name.upper()

			config = config \
				.replace(prefix + "_INTERFACES", prefix + "_INTERFACE_IPV4" + "\n" + prefix + "_INTERFACE_IPV6") \
				.replace(prefix + "_NAME", interface.name)

			if interface.ipv4 is None:
				config = config \
					.replace(prefix + "_IPV4_ADDRESSING", "") \
					.replace(prefix + "_INTERFACE_IPV4", prefix + "_NO_IPV4_ADDRESSING") \
			  		.replace(prefix + "_NO_IPV4_ADDRESSING", self.STATEMENT_NO_IPV4_ADDRESSING)
			else:
				interface_statement: str = self.STATEMENT_IPV4_ADDRESSING \
					.replace("$INTERFACE", prefix)

				config = config \
					.replace(prefix + "_NO_IPV4_ADDRESSING",	"") \
					.replace(prefix + "_INTERFACE_IPV4",		prefix + "_IPV4_ADDRESSING") \
					.replace(prefix + "_IPV4_ADDRESSING",		interface_statement) \
			  		.replace(prefix + "_IPV4_IP_ADDRESS",		str(interface.ipv4.ip)) \
					.replace(prefix + "_IPV4_PREFIX_LENGTH",	str(interface.ipv4.network.prefixlen)) \
					.replace(prefix + "_IPV4_SUBNET_MASK",		str(interface.ipv4.netmask)) \
					.replace(prefix + "_IPV4_NETWORK_ADDRESS",	str(interface.ipv4.network.network_address))

			if interface.ipv6 is None:
				config = config \
					.replace(prefix + "_IPV6_ADDRESSING", "") \
					.replace(prefix + "_INTERFACE_IPV6", prefix + "_NO_IPV6_ADDRESSING") \
			  		.replace(prefix + "_NO_IPV6_ADDRESSING", self.STATEMENT_NO_IPV6_ADDRESSING)
			else:
				interface_statement: str = self.STATEMENT_IPV6_ADDRESSING \
					.replace("$INTERFACE", prefix)

				config = config \
					.replace(prefix + "_NO_IPV6_ADDRESSING",	"") \
					.replace(prefix + "_INTERFACE_IPV6",		prefix + "_IPV6_ADDRESSING") \
					.replace(prefix + "_IPV6_ADDRESSING",		interface_statement) \
			  		.replace(prefix + "_IPV6_IP_ADDRESS",		str(interface.ipv6.ip)) \
					.replace(prefix + "_IPV6_PREFIX_LENGTH",	str(interface.ipv6.network.prefixlen)) \
					.replace(prefix + "_IPV6_SUBNET_MASK",		str(interface.ipv6.netmask)) \
					.replace(prefix + "_IPV6_NETWORK_ADDRESS",	str(interface.ipv6.network.network_address))

		file = open("files/configs/" + self.get_name() + self.FILE_EXTENSION, "w")
		file.write(config)
		file.close()

class Arista_EOS(Router):
	STATEMENT_IPV4_ADDRESSING = """\
   ip address $INTERFACE_IPV4_IP_ADDRESS/$INTERFACE_IPV4_PREFIX_LENGTH"""
	STATEMENT_NO_IPV4_ADDRESSING = """\
   ip routing address required disabled"""
	STATEMENT_IPV6_ADDRESSING = """\
   ipv6 address $INTERFACE_IPV6_IP_ADDRESS/$INTERFACE_IPV6_PREFIX_LENGTH"""
	STATEMENT_NO_IPV6_ADDRESSING = """\
   ipv6 enable"""
	STATEMENT_BGP_NEIGHBOR = """\
   neighbor $BGP_NEIGHBOR_IP_ADDRESS peer group $BGP_GROUP_NAME_group
   neighbor $BGP_NEIGHBOR_IP_ADDRESS remote-as $BGP_NEIGHBOR_ASN"""

class Arista_cEOS(Arista_EOS):
	KIND = "arista_ceos"
	NAME = "arista_ceos"

	FILE_EXTENSION = ""

class Arista_vEOS(Arista_EOS):
	KIND = "arista_veos"
	NAME = "arista_veos"

	FILE_EXTENSION = ".cfg"

class Cisco_IOS_XR(Router):
	USERNAME = "clab"
	PASSWORD = "clab@123"

	STATEMENT_IPV4_ADDRESSING = """\
 ipv4 address $INTERFACE_IPV4_IP_ADDRESS $INTERFACE_IPV4_SUBNET_MASK"""
	STATEMENT_NO_IPV4_ADDRESSING = """
 ipv4 forwarding-enable"""
	STATEMENT_IPV6_ADDRESSING = """\
 ipv6 address $INTERFACE_IPV6_IP_ADDRESS/$INTERFACE_IPV6_PREFIX_LENGTH"""
	STATEMENT_NO_IPV6_ADDRESSING = """\
 ipv6 enable"""
	STATEMENT_BGP_NEIGHBOR = """\
 neighbor $BGP_NEIGHBOR_IP_ADDRESS
  remote-as $BGP_NEIGHBOR_ASN
  use neighbor-group $BGP_GROUP_NAME_group
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

class Juniper_Junos_OS(Router):
	FILE_EXTENSION = ".cfg"

	PASSWORD = "admin@123"

	STATEMENT_IPV4_ADDRESSING = """\
            family inet {
                address $INTERFACE_IPV4_IP_ADDRESS/$INTERFACE_IPV4_PREFIX_LENGTH;
            }"""
	STATEMENT_NO_IPV4_ADDRESSING = """\
			family inet;"""
	STATEMENT_IPV6_ADDRESSING = """\
            family inet6 {
                address $INTERFACE_IPV6_IP_ADDRESS/$INTERFACE_IPV6_PREFIX_LENGTH;
            }"""
	STATEMENT_NO_IPV6_ADDRESSING = """\
			family inet6;"""
	STATEMENT_BGP_NEIGHBOR = """\
            neighbor $BGP_NEIGHBOR_IP_ADDRESS {
                peer-as $BGP_NEIGHBOR_ASN;
            }"""

class Juniper_vJunos_router(Juniper_Junos_OS):
	KIND = "juniper_vjunosrouter"
	NAME = "juniper_vjunosrouter"

class Juniper_vJunos_switch(Juniper_Junos_OS):
	KIND = "juniper_vjunosswitch"
	NAME = "juniper_vjunosswitch"

class Juniper_vJunosEvolved(Juniper_Junos_OS):
	KIND = "juniper_vjunosevolved"
	NAME = "juniper_vjunosevolved"

class Linux(Router):
	KIND = "linux"

	def export(self):
		super().export()

		exec: list[str] = []

		interface_name: str

		for interface in self.interfaces:
			if interface.number is None:
				interface_name = self.LOOPBACK_PREFIX
			else:
				interface_name = interface.get_name()

			if interface.ipv4 is not None:
				exec.append("ip address add " + str(interface.ipv4) + " dev " + interface_name)
			if interface.ipv6 is not None:
				exec.append("ip -6 address add " + str(interface.ipv6) + " dev " + interface_name)

			exec.append("ip link set " + interface_name + " up")

		self.add_attribute("exec", exec)

class Linux_BIRD(Linux):
	NAME = "linux_bird"

	FILE_EXTENSION = ".conf"

	STATEMENT_BGP_NEIGHBOR = """\
protocol bgp from $BGP_GROUP_NAME_template {
  	neighbor $BGP_NEIGHBOR_IP_ADDRESS as $BGP_NEIGHBOR_ASN;
}"""

	def __init__(self, id: int, **kwargs: dict):
		super().__init__(id, **kwargs)

		self.add_attribute("binds", ["configs/" + self.get_name() + self.FILE_EXTENSION + ":/etc/bird.conf"])

class Linux_FRR(Linux):
	NAME = "linux_frr"

	FILE_EXTENSION = ".conf"

	STATEMENT_BGP_NEIGHBOR = """\
 neighbor $BGP_NEIGHBOR_IP_ADDRESS remote-as $BGP_NEIGHBOR_ASN
 neighbor $BGP_NEIGHBOR_IP_ADDRESS peer-group $BGP_GROUP_NAME_group"""

	def __init__(self, id: int, **kwargs: dict):
		super().__init__(id, **kwargs)

		self.add_attribute("binds", [
			"configs/" + self.get_name() + self.FILE_EXTENSION + ":/etc/frr/frr.conf",
			"mounts/daemons:/etc/frr/daemons",
			"mounts/vtysh.conf:/etc/frr/vtysh.conf"])

class Linux_OpenBGPD(Linux):
	NAME = "linux_openbgpd"

	FILE_EXTENSION = ".conf"

	STATEMENT_BGP_NEIGHBOR = """\
	neighbor $BGP_NEIGHBOR_IP_ADDRESS {
		remote-as $BGP_NEIGHBOR_ASN
	}"""

	def __init__(self, id: int, **kwargs: dict):
		super().__init__(id, **kwargs)

		self.add_attribute("binds", [
			"configs/" + self.get_name() + self.FILE_EXTENSION + ":/etc/bgpd/bgpd.conf"])

class Mikrotik_RouterOS(Router):
	KIND = "mikrotik_ros"
	NAME = "mikrotik"

	FILE_EXTENSION = ".auto.rsc"

	STATEMENT_BGP_NEIGHBOR = "add instance=bgp-instance-1 local.role=ebgp name=bgp-connection-$BGP_NEIGHBOR_ID remote.address=$BGP_NEIGHBOR_IP_ADDRESS templates=default"

class Nokia_SR_Linux(Router):
	KIND = "nokia_srlinux"
	NAME = "nokia_srlinux"

	INTERFACE_PREFIX = "e1-"

	FILE_EXTENSION = ".json"

	PASSWORD = "NokiaSrl1!"

	STATEMENT_IPV4_ADDRESSING = """\
        ipv4 {
            admin-state enable
            address $INTERFACE_IPV4_IP_ADDRESS/$INTERFACE_IPV4_PREFIX_LENGTH {
            }
        }"""
	STATEMENT_IPV6_ADDRESSING = """\
        ipv6 {
            admin-state enable
            address $INTERFACE_IPV6_IP_ADDRESS/$INTERFACE_IPV6_PREFIX_LENGTH {
            }
        }"""
	STATEMENT_BGP_NEIGHBOR = """\
            neighbor $BGP_NEIGHBOR_IP_ADDRESS {
                peer-as $BGP_NEIGHBOR_ASN
                peer-group $BGP_GROUP_NAME_group
            }"""

class Nokia_SR_OS(Router):
	KIND = "nokia_sros"
	NAME = "nokia_sros"
	FILE_EXTENSION = ".partial.txt"

	STATEMENT_IPV4_ADDRESSING = """\
                primary {
                    address $INTERFACE_IPV4_IP_ADDRESS
                    prefix-length $INTERFACE_IPV4_PREFIX_LENGTH
                }"""
	STATEMENT_NO_IPV4_ADDRESSING = """\
                forward-ipv4-packets true"""
	STATEMENT_IPV6_ADDRESSING = """\
                address $INTERFACE_IPV6_IP_ADDRESS {
                    prefix-length $INTERFACE_IPV6_PREFIX_LENGTH
                }"""
	STATEMENT_BGP_NEIGHBOR = """\
            neighbor "$BGP_NEIGHBOR_IP_ADDRESS" {
                group "$BGP_GROUP_NAME_group"
                peer-as $BGP_NEIGHBOR_ASN
            }"""

class Route_Server(Router):
	def export(self):
		super().export()

		exec: list[str] = []

		interface_name: str

		for interface in self.interfaces:
			if interface.number is None:
				interface_name = self.LOOPBACK_PREFIX
			else:
				interface_name = interface.get_name()

			if interface.ipv4 is not None:
				exec.append("ip address add " + str(interface.ipv4) + " dev " + interface_name)
			if interface.ipv6 is not None:
				exec.append("ip -6 address add " + str(interface.ipv6) + " dev " + interface_name)

			exec.append("ip link set " + interface_name + " up")

		self.add_attribute("exec", exec)

class BIRD(Route_Server):
	KIND = "linux"
	NAME = "bird"

	FILE_EXTENSION = ".conf"

	STATEMENT_BGP_NEIGHBOR = """\
protocol bgp from $BGP_GROUP_NAME_template {
  	neighbor $BGP_NEIGHBOR_IP_ADDRESS as $BGP_NEIGHBOR_ASN;
}"""

	def __init__(self, id: int, **kwargs: dict):
		super().__init__(id, **kwargs)

		self.add_attribute("binds", ["configs/" + self.get_name() + self.FILE_EXTENSION + ":/etc/bird.conf"])

class FRR(Route_Server):
	KIND = "linux"
	NAME = "frr"

	FILE_EXTENSION = ".conf"

	STATEMENT_BGP_NEIGHBOR = """\
 neighbor $BGP_NEIGHBOR_IP_ADDRESS remote-as $BGP_NEIGHBOR_ASN
 neighbor $BGP_NEIGHBOR_IP_ADDRESS peer-group $BGP_GROUP_NAME_group"""

	def __init__(self, id: int, **kwargs: dict):
		super().__init__(id, **kwargs)

		self.add_attribute("binds", [
			"configs/" + self.get_name() + self.FILE_EXTENSION + ":/etc/frr/frr.conf",
			"mounts/daemons:/etc/frr/daemons",
			"mounts/vtysh.conf:/etc/frr/vtysh.conf"])

class OpenBGPD(Route_Server):
	KIND = "linux"
	NAME = "openbgpd"

	FILE_EXTENSION = ".conf"

	STATEMENT_BGP_NEIGHBOR = """\
	neighbor $BGP_NEIGHBOR_IP_ADDRESS {
		remote-as $BGP_NEIGHBOR_ASN
	}"""

	def __init__(self, id: int, **kwargs: dict):
		super().__init__(id, **kwargs)

		self.add_attribute("binds", [
			"configs/" + self.get_name() + self.FILE_EXTENSION + ":/etc/bgpd/bgpd.conf"])