"""
Helper functions to generate payloads to be sent to Apstra via batch APIs.
"""
import os

from collections import defaultdict
from netaddr import IPNetwork
from slugify import slugify

BASE_DIR = os.path.dirname(__file__)

# base subnet for peer links or loopbacks
link_subnet = IPNetwork("192.168.0.0/16").subnet(31)
loopback_subnet = IPNetwork("10.0.0.0/16").subnet(32)

# dictionary mapping station ID and vDUT interfaces currently used for it.
device_interfaces_in_use = defaultdict(list)

# dictionary containing the list of adjacent stations for a given station
adjacency_list = defaultdict(list)


def get_next_available_interface_for_node_system(station_id):
    used_interfaces_for_station = device_interfaces_in_use[station_id]

    if not used_interfaces_for_station:
        device_interfaces_in_use[station_id].append(0)
        return 0
    else:
        next_available_interface = used_interfaces_for_station[-1] + 1
        device_interfaces_in_use[station_id].append(next_available_interface)
        return next_available_interface


def update_adjacency_list(node_a, node_b):
    """
    Function to update adjacency list for node_a and node_b.
    Note that this is not a directed graph, so if node_a and node_b are adjacent, we
    update both the keys for node_a and node_b by appending the other endpoint.

    Returns True if node_a is not found in the original adjacency list. This is
    useful to help de-duplicating link whenever we invoke twice this function
    with node_a and node_b in reverse order
    """
    is_updated = False
    node_a_adj = adjacency_list[node_a]
    node_b_adj = adjacency_list[node_b]
    if node_b not in node_a_adj:
        adjacency_list[node_a].append(node_b)
        is_updated = True
    if node_a not in node_b_adj:
        adjacency_list[node_b].append(node_a)

    return is_updated


def build_nodes_payload(tfl_json, device_profile_id):
    """
    Payload to populate all nodes onto the canvas, one node per station. Hostnames
    are normalized with slugify
    """
    payload = []
    for station in tfl_json['stations']:
        payload.append(
            {
                'method': 'POST',
                'path': '/generic-systems',
                'lid': '##sys%d##' % station['id'],
                'payload': {
                    'system_type': 'internal',
                    'device_profile_id': device_profile_id,
                    'label': station['name'],
                    'hostname': slugify(station['name']),
                    'tags': [],
                }
            }
        )
    return payload


def build_links_payload(tfl_json):
    """
    Payload to populate link objects. Here vEX is assumed
    """
    payload = []
    # i4n: interface for node. shorter alias to function to get next
    # available interface, since we call it often inline later
    i4n = get_next_available_interface_for_node_system

    iface_prefix = 'ge-0/0/' # assume vEX
    for connection in tfl_json['connections']:
        c_from = connection['from']
        c_to = connection['to']
        latency = str(connection['latency'])
        if not update_adjacency_list(c_from, c_to):
            # the link already exists because has been defined earlier, but
            # with source and dst in reverse order. Nothing to do here.
            continue

        # get next available /31 subnet and later assign the two IP addresses
        # to both endpoints of this link
        link_addr = next(link_subnet)
        payload.append(
            {
                'method': 'POST',
                'path': '/links',
                'lid': '##sys%dsys%dlink1##' % (c_from, c_to),
                'payload': {
                    'endpoints': [
                        {
                            'system': {
                                'id': '##sys%d##' % c_from
                            },
                            'interface': {
                                'if_name': '%s%d' % (iface_prefix, i4n(c_from)),
                                'transformation_id': 1,
                                'ipv4_addr': "%s/31" % str(link_addr[0]),
                            }
                        },
                        {
                            'system': {
                                'id': '##sys%d##' % c_to
                            },
                            'interface': {
                                'if_name': '%s%d' % (iface_prefix, i4n(c_to)),
                                'transformation_id': 1,
                                'ipv4_addr': "%s/31" % str(link_addr[1]),
                            }
                        }
                    ],
                    'label': 'sys%d <-> sys%d' % (c_from, c_to),
                    'tags': [latency]
                }
            }
        )
    return payload


def build_config_templates_payload():
    """
    Payload to create config-templates object
    """
    # Config templates are version-controlled in this repo. We take the content
    # of those files and create them into the blueprint.
    template_files = ['main', 'system', 'interfaces', 'protocols']
    payload = []
    for template_file in template_files:
        filename = '%s.jinja' % template_file
        with open(os.path.join(BASE_DIR, '../config_templates', filename), 'r') as f:
            content = f.read()
            payload.append(
                {
                    'method': 'POST',
                    'path': '/config-templates',
                    'lid': '##%s##' % template_file,
                    'payload': {
                        'label': filename,
                        'text': content,
                        'tags': [],
                    }
                }
            )
    return payload


def build_static_host_mappings_config_template(links_map):
    """
    Create the config_template for static host mapping separately, since it's
    a bit large and generated from different input data (cabling map)
    """
    payload = []

    static_mapping_str = ""
    for host, ips in sorted(links_map.items(), key=lambda i: i[0]):
        ips_str = " ".join(ips)
        static_mapping_str += "        %s [%s];\n" % (slugify(host), ips_str)

    content = """
    static-host-mapping {
%s
    }
""" % static_mapping_str

    payload.append(
        {
            'method': 'POST',
            'path': '/config-templates',
            'lid': '##static-host-mappings##',
            'payload': {
                'label': 'static_host_mapping.jinja',
                'text': content,
                'tags': [],
            }
        }
    )
    return payload

def build_config_templates_assignments_payload(tfl_json):
    """
    Payload to define assignment of config templates to each station/node of the
    topology
    """
    # simply we have the same config-template for every node
    assignments = {}
    for station in tfl_json['stations']:
        assignments.update({
            '##sys%d##' % station['id']: '##main##'
        })

    payload = [{
        'method': 'PATCH',
        'path': '/config-templates-assignments',
        'payload': {
            'assignments': assignments
        }
    }]
    return payload


def build_property_sets_payload(tfl_json):
    """
    Property sets will be the repository for ASN numbers and loopback IPs of each
    node in the topology, keyed by hostname, e.g.:
    {
      "cannon-street": {
        "asn": 241,
        "loopback": "10.0.0.237"
      },
      "kentish-town": {
        "asn": 134,
        "loopback": "10.0.0.130"
      },
    ...
    """
    ps_values = {}
    for station in tfl_json['stations']:
        loopback = next(loopback_subnet)
        ps_values.update(
            {
                slugify(station['name']):
                    {
                        'asn': station['id'],
                        'loopback': str(loopback.ip),
                    }
            })

    payload = [
        {
            'method': 'POST',
            'path': '/property-sets',
            'lid': '##ps1##',
            'payload': {
                'label': 'data',
                'values': ps_values
            }
        }
    ]
    return payload

