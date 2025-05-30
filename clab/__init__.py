import yaml

import clab.containerlab
import clab.lab
import clab.topology



def representer(dumper, data):
	return dumper.represent_data(data.__repr__())

yaml.add_representer(clab.containerlab.Lab, representer)
yaml.add_representer(clab.lab.Topology, representer)
yaml.add_representer(clab.topology.Link, representer)
yaml.add_multi_representer(clab.topology.Node, representer)