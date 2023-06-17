import glm
from dicttoxml import dicttoxml
from pprint import pprint as pp
import xml.etree.ElementTree as et
from collections import defaultdict
from xml.dom.minidom import parseString as ps

nodes = ['N684', 'N680','N633','N692','N675','N671','N632','N611','N645','N652']


# feeder = glm.load("./model_base.glm")
feeder = glm.load("./original_basecase.glm")

def get_nodes (feeder, nodes):
    main_nodes = [obj['attributes']['name'] for obj in feeder['objects'] if obj['name'] == 'node' and obj['attributes']['name'].startswith('N') and obj['attributes']['name'] in nodes]
    return main_nodes

def get_feeders(feeder):
    feeders = [obj['attributes']['name'] for obj in feeder['objects'] if obj['name'] == 'meter' and obj['attributes']['name'].startswith('meter')]
    return feeders

def get_ol (feeder):
    segments = [obj['attributes']['name'] for obj in feeder['objects'] if obj['name'] == 'overhead_line' and obj['attributes']['to'].startswith('xfmr')]
    return segments

def get_xfmers (feeder):
    xfmrs = [obj['attributes']['name'] for obj in feeder['objects'] if obj['name'] == 'transformer' and obj['attributes']['name'].startswith('xfmr')]
    return xfmrs

def service_point (feeder):
    sps = [obj['attributes']['name'] for obj in feeder['objects'] if obj['name'] == 'triplex_load' and obj['attributes']['name'].startswith('tlx')]
    return sps

def nodes_feeders_dict(main_nodes, feeders):
    
    
    data = defaultdict(dict)

    for node in range(len(main_nodes)):
        for feeder in feeders:
            if main_nodes[node].split('N')[1] in feeder:
                group_name = f'{main_nodes[node]}'
                if not group_name in data['SourceBus']:
                    data['SourceBus'][group_name] = {}
                data['SourceBus'][group_name][feeder] = {}
    return data


def insert_segments (data, segments):
    
    for item in data['SourceBus']:
        feeders = data['SourceBus'][item]
        for fed in feeders:
            for seg in range(len(segments)):
                if fed.split('_')[1] in segments[seg] and fed.split('_')[2] in segments[seg]:
                    seg_name = f'{segments[seg]}'
                    if not seg_name in feeders[fed]:
                        feeders[fed][seg_name] = {}

    return data

def insert_xfmrs (data, xfmrs):
    for item in data['SourceBus']:
        feeders = data['SourceBus'][item]
        for fed in feeders:
            segments = data['SourceBus'][item][fed]
            for seg in segments:
                for xf in range(len(xfmrs)):
                    if seg.split('_')[1] in xfmrs[xf] and seg.split('_')[2] in xfmrs[xf] and seg.split('_')[3] == xfmrs[xf].split("_")[3]:
                        data['SourceBus'][item][fed][seg][xfmrs[xf]] = {}
    return data

def service_points (data,service_points):
    counter = 8
    k = 8
    i = 0
    # starting = 0
    # ending = 8
    # num_loads_per_xfmr = 8
    for item in data['SourceBus']:
        for fed in data['SourceBus'][item]:
            for seg in data['SourceBus'][item][fed]:
                xfmrs = data['SourceBus'][item][fed][seg]
                for key, value in enumerate(xfmrs):
                    data['SourceBus'][item][fed][seg][value] = [sps for sps in service_points[i:counter]]
                    i = counter
                    counter += k
    
    return data
                    
def dict_xml(data):
    xml_string = dicttoxml(data, attr_type=False)
    dom = ps(xml_string)

    with open ('xml_output.xml', 'w') as f:
        f.write(dom.toprettyxml(indent='   '))
    
    finalize_xml()

def finalize_xml():
    tree = et.parse("./xml_output.xml")
    source_bus_child = tree.getroot().find('SourceBus')
    tree._setroot(source_bus_child)
    tree.write('xml_output.xml')



    
def main(feeder, nodes):

    main_nodes = get_nodes(feeder, nodes)
    feeders = get_feeders(feeder)
    segments = get_ol (feeder)
    xfmrs = get_xfmers(feeder)
    sps = service_point(feeder)
    data = nodes_feeders_dict (main_nodes, feeders)
    data = insert_segments(data, segments)
    data = insert_xfmrs (data, xfmrs)
    data = service_points (data, sps)
    data = dict_xml(data)
    


    
main(feeder, nodes)