import xml.etree.ElementTree as et
from pprint import pprint as pp

class TopologyProcessor ():
    def __init__(self):

        self.topology_file = '../../Configuration/psu_feeder_topology.xml'
    
    def import_topology_from_file (self):
        tree = et.parse(self.topology_file)
        root = tree.getroot()

        return root
    
    def get_substation (self):
        return self.import_topology_from_file().tag
    
    def get_group(self):
        self.group = self.get_elements(self.import_topology_from_file(), 'group', 'name')
        return self.group
    
    def get_feeders(self):
        self.feeders = self.get_elements(self.import_topology_from_file(), 'feeder','name')
        return self.feeders

    def get_segments(self):
        self.segments = self.get_elements(self.import_topology_from_file(), 'segment','name')
        return self.segments

    def get_elements (self, element, tag, attribute):
        attributes = []
        for elem in element.iter(tag):
            attributes.append(elem.get(attribute))
        return attributes

go = TopologyProcessor()

fed = go.get_feeders()
group = go.get_group()
segments = go.get_segments()

for i in fed:
    print(i)
    # feeder = (item for item in fed if item == i)




# print(len(fed))


# for i in group_feeders:
#     print(i)
