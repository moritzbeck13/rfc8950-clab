import asyncio
import ipaddress
import time
import yaml

from clab import containerlab, kinds, topology



async def test(lab: containerlab.Lab):
	routers: list[kinds.Router] = []

	for node in lab.topology.nodes:
		if isinstance(node, kinds.Router) and not isinstance(node, kinds.Route_Server):
			routers.append(node)

	matrix = {}
	tasks = []

	for router_from in routers:
		matrix[router_from.get_name()] = {
			"icmp-addresses": {},
			"traceroute": {}}

		for router_to in routers:
			if router_to is not router_from:
				tasks.append(router_from.interfaces[2].connected_to.node.exec(["traceroute", "-I", "-n", "-m", "3", str(router_to.interfaces[2].connected_to.ipv4.ip)], type="traceroute", router_from=router_from, router_to=router_to))

	results = await asyncio.gather(*tasks)

	for result in results:
		returncode = result.get("returncode")
		stderr = result.get("stderr")
		stdout = result.get("stdout")
		kwargs = result.get("kwargs")

		test = {
			"exit-code": returncode,
			"reasons": [],
			"result": "failed",
			"stderr": stderr,
			"stdout": stdout}

		router_from: kinds.Router = kwargs["router_from"]
		router_to: kinds.Router = kwargs["router_to"]

		if returncode != 0:
			test["reasons"].append("non-zero exit code")
		if len(stderr) != 0:
			test["reasons"].append("stderr is not empty")
		if len(stdout) != 4:
			test["reasons"].append("unexpected length of stdout")
		if len(stdout) > 1 and str(router_from.interfaces[2].ipv4.ip) not in stdout[1]:
				test["reasons"].append("incorrect first hop")
		if len(stdout) > 3 and str(router_to.interfaces[2].connected_to.ipv4.ip) not in stdout[3]:
				test["reasons"].append("incorrect last hop")
		if test["reasons"] == []:
			test["result"] = "succeeded"

			address = stdout[2].split(" ")[3]

			if address not in matrix[router_to.get_name()]["icmp-addresses"]:
				interface_name = "other"

				for interface in router_to.interfaces:
					if interface.ipv4 is not None and address == str(interface.ipv4.ip):
						interface_name = interface.name
						break

				matrix[router_to.get_name()]["icmp-addresses"][address] = {
					"as-seen-by": [router_from.get_name()],
					"interface": interface_name}
			else:
				matrix[router_to.get_name()]["icmp-addresses"][address]["as-seen-by"].append(router_from.get_name())

		matrix[router_from.get_name()]["traceroute"][router_to.get_name()] = test

	file = open("results.yml", "w")
	file.write(yaml.dump(matrix))
	file.close()

def main():
	route_servers: dict[type[kinds.Route_Server], dict] = {
		kinds.BIRD_2: {"image": "bird:2"},
		kinds.BIRD_3: {"image": "bird:3"},
		kinds.FRR: {"image": "quay.io/frrouting/frr:10.3.0"},
		kinds.OpenBGPD: {"image": "openbgpd/openbgpd"}
	}

	routers: dict[type[kinds.Router], dict] = {
		kinds.Arista_cEOS: {"image": "vrnetlab/arista_ceos:4.33.2F"},
		kinds.Arista_vEOS: {"image": "vrnetlab/arista_veos:4.33.2F"},
		kinds.Cisco_XRd: {"image": "ios-xr/xrd-control-plane:25.1.1"},
		kinds.Juniper_vJunosEvolved: {"image": "vrnetlab/juniper_vjunosevolved:24.4R1.8"},
		kinds.Linux: {"image": "quay.io/frrouting/frr:10.3.0"},
		kinds.Nokia_SR_Linux: {"image": "ghcr.io/nokia/srlinux"},
		kinds.Nokia_SR_OS: {"image": "vrnetlab/nokia_sros:23.10.R6", "license": "licenses/SR_OS_VSR-SIM1_license.txt"}
	}

	lab: containerlab.Lab = containerlab.Lab("peering_lan")
	peering_lan: kinds.Bridge = kinds.Bridge(None)
	peering_lan.add_interface(topology.Interface(None, None))
	lab.topology.add_node(peering_lan)

	id: int = 0
	r: list[tuple[kinds.Router, ipaddress.IPv4Interface | ipaddress.IPv6Interface]] = []
	rs: list[tuple[kinds.Router, ipaddress.IPv4Interface | ipaddress.IPv6Interface]] = []



	id += 1

	route_server: kinds.Route_Server = kinds.BIRD_2(id, **route_servers[kinds.BIRD_2])
	route_server.add_interface(topology.Interface("loopback", None, ipv4=ipaddress.IPv4Interface(("172.16." + str(id) + ".1", 32))))
	route_server.add_interface(topology.Interface("peering_lan", 1, ipv6=ipaddress.IPv6Interface(("c1ab::" + str(id), 64))))
	rs.append((route_server, route_server.interfaces[1].ipv6))
	route_server.peers = r

	lab.topology.add_node(route_server)

	peering_lan.add_interface(topology.Interface("peering_lan_" + str(id), id))
	lab.topology.connect_interfaces(peering_lan.interfaces[id], route_server.interfaces[1])



	for Router, attributes in routers.items():
		for _ in range(1):
			id += 1

			router: kinds.Router = Router(id, **attributes)
			router.add_interface(topology.Interface("loopback", None, ipv4=ipaddress.IPv4Interface(("172.16." + str(id) + ".1", 32))))
			router.add_interface(topology.Interface("peering_lan", 1, ipv6=ipaddress.IPv6Interface(("c1ab::" + str(id), 64))))
			router.add_interface(topology.Interface("client_lan", 2, ipv4=ipaddress.IPv4Interface(("192.168." + str(id) + ".1", 24))))
			r.append((router, router.interfaces[1].ipv6))
			router.peers = rs

			client: kinds.Client = kinds.Alpine(id)
			client.add_interface(topology.Interface("loopback", None))
			client.add_interface(topology.Interface("client_lan", 1, ipv4=ipaddress.IPv4Interface(("192.168." + str(id) + ".254", 24))))
			client.default_gateway = client.interfaces[1]

			lab.topology.add_node(router)
			lab.topology.add_node(client)

			peering_lan.add_interface(topology.Interface("peering_lan_" + str(id), id))
			lab.topology.connect_interfaces(peering_lan.interfaces[id], router.interfaces[1])
			lab.topology.connect_interfaces(router.interfaces[2], client.interfaces[1])

	lab.destroy()
	lab.export()
	lab.deploy()
	time.sleep(60*10)
	asyncio.run(test(lab))

if __name__ == "__main__":
	main()