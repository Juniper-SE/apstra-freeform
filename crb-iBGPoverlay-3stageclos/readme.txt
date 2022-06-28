===========================
Apstra FreeForm
Apstra 4.1.1 evaluation

CRB Signaling 
- BGP underlay
- BGP overlay

version 01

Usman Latif
ulatif@juniper.net
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

- junos_underlaybgp.jinja
- junos_overlaycrb.jinja
- junos_crbvxlan.jinja


: Updates to be added to main jinja :

name: junos_configuration.jinja
///////////////////////////////////////////////////////////////////////////
{% block underlaybgp %}
{%- include "junos_underlaybgp.jinja" %}
{% endblock underlaybgp %}

{% block overlaycrb %}
{%- include "junos_overlaycrb.jinja" %}
{% endblock overlaycrb %}

{% block crbvxlan %}
{%- include "junos_crbvxlan.jinja" %}
{% endblock crbvxlan %}
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

