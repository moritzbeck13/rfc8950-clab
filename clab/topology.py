from __future__ import annotations

import asyncio
import ipaddress
import yaml

import clab.lab



class Interface:
	def __init__(self,
			  number: int, connected_to: Interface = None,
			  ipv4: ipaddress.IPv4Interface = None, ipv6: ipaddress.IPv6Interface = None):
		self.number: int = number

		self.node: Node = None
		self.connected_to: Interface = connected_to

		self.ipv4: ipaddress.IPv4Interface = ipv4
		self.ipv6: ipaddress.IPv6Interface = ipv6

	def get_name(self) -> str:
		return self.node.INTERFACE_PREFIX + str(self.number)

	def export(self) -> str:
		pass



class Link(yaml.YAMLObject):
	def __init__(self, interface_from: Interface, interface_to: Interface):
		interface_from.connected_to = interface_to
		interface_to.connected_to = interface_from

		self.interface_from: Interface = interface_from
		self.interface_to: Interface = interface_to

	def __repr__(self) -> dict:
		return {"endpoints": [
			self.interface_from.node.get_name() + ":" + self.interface_from.get_name(),
			self.interface_to.node.get_name() + ":" + self.interface_to.get_name()]}



class Node(yaml.YAMLObject):
	KIND = None
	NAME = None

	INTERFACE_PREFIX = "eth"



	def __init__(self, id: int, **kwargs: dict):
		self.id: int = id
		self.topology: clab.lab.Topology = None

		self.interfaces: dict[str, Interface] = {}
		self.attributes: dict[str: any] = {"kind": self.KIND}

		for key, value in kwargs.items():
			self.add_attribute(key, value)

	def __repr__(self) -> dict:
		return self.attributes



	def get_name(self) -> str:
		return self.NAME + "_" + str(self.id)

	def get_container_name(self) -> str:
		return self.topology.lab.get_container_prefix() + self.get_name()



	def add_interface(self, kind: str, interface: Interface):
		interface.node = self

		self.interfaces[kind] = interface
	
	def add_attribute(self, key: str, value):
		attribute = self.attributes.get(key)

		if attribute is None:
			self.attributes[key] = value
		else:
			attribute_type = type(attribute)

			if attribute_type is list:
				attribute.extend(value)
			elif attribute_type is dict:
				attribute.update(value)
			else:
				attribute = value



	def export(self):
		pass


	def pre_deploy(self):
		pass

	def post_deploy(self):
		pass


	def pre_destroy(self):
		pass

	def post_destroy(self):
		pass



	def exec(self, cmd: list[str], **kwargs):
		return asyncio.run(exec(cmd, kwargs))

	async def exec(self, cmd: list[str], **kwargs):
		pass