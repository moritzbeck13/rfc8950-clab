import yaml

import clab.Containerlab
import clab.Lab
import clab.Topology



def representer(dumper, data):
	return dumper.represent_data(data.__repr__())

yaml.add_representer(clab.Containerlab.Lab, representer)
yaml.add_representer(clab.Lab.Topology, representer)
yaml.add_representer(clab.Topology.Link, representer)
yaml.add_multi_representer(clab.Topology.Node, representer)