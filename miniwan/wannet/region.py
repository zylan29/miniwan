ROUTER_NAME_FORMATTER = 'r_{}'
HOST_NAME_FORMATTER = 'h_{}'
INTERFACE_NAME_FORMATTER = '{}-eth{}'

LO_IP_FORMATTER = '{}.{}.0.1/32'  # ASN, ASN
WAN_IP_FORMATTER = '{}.0.0.{}/30'  # ASN, Interface_ID
LAN_MASK = '/24'
HOST_GW_FORMATTER = '{}.0.1.1'  # ASN
HOST_IP_FORMATTER = '{}.0.1.2' + LAN_MASK  # ASN


class Region(object):
    """"
    1 router and 1 host per region.
    """
    ASN = 1

    def __init__(self, name):
        self.name = name
        self.asn = Region.ASN
        Region.ASN += 1
        self.num_wan_ip = 0
        self.router = None

        self.interfaces = [(0, LO_IP_FORMATTER.format(self.asn, self.asn))]
        self.neighbors = []
        self.asn_table = {}

        self.router_name = ROUTER_NAME_FORMATTER.format(self.name)
        self.host_name = HOST_NAME_FORMATTER.format(self.name)
        self.host_gw = HOST_GW_FORMATTER.format(self.asn)
        self.host_ip = HOST_IP_FORMATTER.format(self.asn)
        self.lo_ip = LO_IP_FORMATTER.format(self.asn, self.asn)

    def get_router_name(self):
        return self.router_name

    def get_host_name_ip_gw(self):
        return (self.host_name, self.host_ip, self.host_gw)

    def get_next_wan_ip(self):
        self.num_wan_ip += 1
        return WAN_IP_FORMATTER.format(self.asn, self.num_wan_ip)

    def add_interface(self, *iface_id_ip):
        self.interfaces.append(iface_id_ip)

    def add_neighbor(self, *neighbor_ip_asn):
        self.neighbors.append(neighbor_ip_asn)

    def connect_lan(self, router_interface_id):
        self.add_interface(router_interface_id, self.host_gw + LAN_MASK)

    def connect_wan(self, neighbor, interface_ids):
        assert isinstance(neighbor, Region)
        assert len(interface_ids) == 2
        local_intf_id, remote_intf_id = interface_ids
        if self.asn < neighbor.asn:
            local_ip = self.get_next_wan_ip()
            remote_ip = self.get_next_wan_ip()
        else:
            local_ip = neighbor.get_next_wan_ip()
            remote_ip = neighbor.get_next_wan_ip()

        self.add_interface(local_intf_id, local_ip)
        neighbor.add_interface(remote_intf_id, remote_ip)
        self.add_neighbor(remote_ip.split('/')[0], neighbor.asn)
        neighbor.add_neighbor(local_ip.split('/')[0], self.asn)

    def get_router_info(self):
        router_info = {
            'interfaces': self.interfaces,
            'neighbors': self.neighbors,
            'asn': self.asn,
            'router_id': self.lo_ip.split('/')[0]
        }
        return router_info
