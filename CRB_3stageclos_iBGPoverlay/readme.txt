===========================
Apstra FreeForm
Apstra 4.1.1 evaluation

CRB Signaling 
- BGP underlay
- BGP overlay

version 01

Usman Latif
June 2022
Juniper Networks
Professional Services
===========================


Topology:

spine1 spine2
   |\  /|
   | \/ |
   | /\ |
   |/  \|
leaf1  leaf2
    \  /
     \/
   Generic
   System



property_sets:
--------------

name: fabricbgp
{
  "spine1": {
    "localas": 65001,
    "rid": "1.1.1.1"
  },
  "spine2": {
    "localas": 65002,
    "rid": "2.2.2.2"
  },
  "leaf1": {
    "localas": 65011,
    "rid": "3.3.3.3"
  },
  "leaf2": {
    "localas": 65012,
    "rid": "4.4.4.4"
  }
}

name: noderole
{
  "spine1": "spine",
  "spine2": "spine",
  "leaf1": "leaf",
  "leaf2": "leaf"
}

name: overlaybgp
{
  "model": "crb",
  "bgpasn": "64512"
}


j2 templates
------------

name: junos_underlaybgp.jinja
///////////////////////////////////////////////////////////////////////////

{# Contributor: Usman Latif #}
{# Juniper Networks PS      #}
{# June, 2022               #}
{#                          #}
{% if property_sets.fabricbgp[hostname] is defined %}
protocols {
    bgp {
       group UNDERLAY {
         family inet {
            unicast;
         }
         tcp-mss 4000;
         type external;
         export UNDERLAY-EXPORT;
         multipath {
           multiple-as;
         }
         bfd-liveness-detection {
            minimum-interval 1000;
            multiplier 3;
         }
         local-as {{ property_sets.fabricbgp[hostname].localas }};
 {% for intf,iface in interfaces.items() %}
   {% if iface.role == 'internal' %}
         neighbor {{iface.neighbor_interface.ipv4_address}} {
         description "bgp to {{iface.neighbor_interface.system_hostname}}";
         peer-as {{ property_sets.fabricbgp[iface.neighbor_interface.system_hostname].localas }};
         }
   {% else %}
   {% endif %}
 {% endfor %}
       }
    }   
}
policy-options {
  policy-statement UNDERLAY-EXPORT {
    term 10 {
      from {
        protocol direct;
        route-filter 0/0 prefix-length-range /32-/32;
      }
      then accept;
    }
  }
}
{% else %}
{% endif %}

///////////////////////////////////////////////////////////////////////////



name: junos_overlaycrb.jinja
///////////////////////////////////////////////////////////////////////////
{# Contributor: Usman Latif #}
{# Juniper Networks PS      #}
{# June, 2022               #}
{#                          #}
{% if property_sets.overlaybgp.model is defined and property_sets.overlaybgp.model == 'crb' %}
protocols {
    bgp {
  {% if property_sets.noderole[hostname] == 'spine' %}
       group RR-CLIENTS {
         family evpn {
            signaling;
         }
         tcp-mss 4000;
         type internal;
         bfd-liveness-detection {
            minimum-interval 3000;
            multiplier 3;
         }
         local-address {{ property_sets.fabricbgp[hostname].rid }};
         cluster {{ property_sets.fabricbgp[hostname].rid }};
    {% for nodes,device in property_sets.fabricbgp.items() %}
      {% if nodes != hostname and property_sets.noderole[nodes] != 'spine' %}
         neighbor {{device.rid}};
      {% else %}
      {% endif %}
    {% endfor %}
       }
  {% else %}     
       group RR {
         family evpn {
            signaling;
         }
         tcp-mss 4000;
         type internal;
         local-address {{ property_sets.fabricbgp[hostname].rid }};
    {% for nodes,device in property_sets.fabricbgp.items() %}
      {% if nodes != hostname and property_sets.noderole[nodes] != 'leaf' %}
         neighbor {{device.rid}};
      {% else %}
      {% endif %}
    {% endfor %}
       }
  {% endif %}
    }
}
interfaces {
  lo0 {
    unit 0 {
      family inet {
        address {{ property_sets.fabricbgp[hostname].rid }}/32;
      }
    }
  }
}
routing-options {
  router-id {{ property_sets.fabricbgp[hostname].rid }};
  autonomous-system {{ property_sets.overlaybgp.bgpasn }};
  forwarding-table {
    export PFE-LB;
    ecmp-fast-reroute;
    chained-composite-next-hop {
        ingress {
          evpn;                   
        }
    }
  }
}
policy-options {
  policy-statement PFE-LB {
    then {
      load-balance per-packet;
    }
  }
}
{% else %}
{% endif %}

///////////////////////////////////////////////////////////////////////////



Updates to main jinja:

name: junos_overlaycrb.jinja
///////////////////////////////////////////////////////////////////////////
{% block underlaybgp %}
{%- include "junos_underlaybgp.jinja" %}
{% endblock underlaybgp %}

{% block overlaycrb %}
{%- include "junos_overlaycrb.jinja" %}
{% endblock overlaycrb %}
///////////////////////////////////////////////////////////////////////////




/------------------------------------------------------------------------/

Rendered Config Example - spine1

system {
    host-name spine1;
}
interfaces {
    replace: et-2/0/0 {
        description "facing_leaf1:et-0/2/0";
        mtu 9216;
        unit 0 {
            family inet {
                address 10.1.1.1/31;
            }
        }
    }
    replace: et-2/0/1 {
        description "facing_leaf2:et-0/2/1";
        mtu 9216;
        unit 0 {
            family inet {
                address 10.1.1.5/31;
            }
        }
    }
}
protocols {
    lldp {
        port-id-subtype interface-name;
        port-description-type interface-description;
        neighbour-port-info-display port-id;
        interface all;
    }
    replace: rstp {
    bridge-priority 0;
        bpdu-block-on-edge;
    }
}
protocols {
    bgp {
       group UNDERLAY {
         family inet {
            unicast;
         }
         tcp-mss 4000;
         type external;
         export UNDERLAY-EXPORT;
         multipath {
           multiple-as;
         }
         bfd-liveness-detection {
            minimum-interval 1000;
            multiplier 3;
         }
         local-as 65001;
         neighbor 10.1.1.0 {
         description "bgp to leaf1";
         peer-as 65011;
         }
         neighbor 10.1.1.4 {
         description "bgp to leaf2";
         peer-as 65012;
         }
       }
    }   
}
policy-options {
  policy-statement UNDERLAY-EXPORT {
    term 10 {
      from {
        protocol direct;
        route-filter 0/0 prefix-length-range /32-/32;
      }
      then accept;
    }
  }
}
protocols {
    bgp {
       group RR-CLIENTS {
         family evpn {
            signaling;
         }
         tcp-mss 4000;
         type internal;
         bfd-liveness-detection {
            minimum-interval 3000;
            multiplier 3;
         }
         local-address 1.1.1.1;
         cluster 1.1.1.1;
         neighbor 3.3.3.3;
         neighbor 4.4.4.4;
       }
    }
}
interfaces {
  lo0 {
    unit 0 {
      family inet {
        address 1.1.1.1/32;
      }
    }
  }
}
routing-options {
  router-id 1.1.1.1;
  autonomous-system 64512;
  forwarding-table {
    export PFE-LB;
    ecmp-fast-reroute;
    chained-composite-next-hop {
        ingress {
          evpn;                   
        }
    }
  }
}
policy-options {
  policy-statement PFE-LB {
    then {
      load-balance per-packet;
    }
  }
}

