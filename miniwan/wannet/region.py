ROUTER_NAME_FORMATTER = 'r{}'
HOST_NAME_FORMATTER = 'h{}'
INTERFACE_NAME_FORMATTER = '{}-eth{}'

IP_BITS = 32
WAN_IP_MASK = 30
WAN_IP_FORMATTER = '10.255.{}.{}/' + str(WAN_IP_MASK)  # ASN, Interface_ID
LAN_IP_MASK = 24
HOST_GW_FORMATTER = '10.{}.0.1'  # ASN
HOST_IP_FORMATTER = '10.{}.0.2/' + str(LAN_IP_MASK)  # ASN


class Region(object):
    """"
    Generate IP and other configurations for routers and hosts.
    1 router and 1 host per region.
    """
    ASN = 1
    WAN_LINKS = 0

    def __init__(self, name):
        self.name = name
        self.asn = Region.ASN
        Region.ASN += 1
        self.num_wan_ip = 0

        self.lan_interfaces = []
        self.wan_interfaces = []
        self.neighbors = []

        self.router_name = ROUTER_NAME_FORMATTER.format(self.asn)
        self.host_name = HOST_NAME_FORMATTER.format(self.asn)
        self.host_gw = HOST_GW_FORMATTER.format(self.asn)
        self.host_ip = HOST_IP_FORMATTER.format(self.asn)

    def get_router_name(self):
        return self.router_name

    def get_host_name_ip_gw(self):
        return (self.host_name, self.host_ip, self.host_gw)

    @staticmethod
    def get_wan_ip_pair():
        ip_3th = Region.WAN_LINKS * 2 ** (IP_BITS - WAN_IP_MASK) / 255
        ip_4th = Region.WAN_LINKS * 2 ** (IP_BITS - WAN_IP_MASK) % 255
        Region.WAN_LINKS += 1
        return WAN_IP_FORMATTER.format(ip_3th, ip_4th + 1), WAN_IP_FORMATTER.format(ip_3th, ip_4th + 2)

    def add_lan_interface(self, *iface_id_ip):
        self.lan_interfaces.append(iface_id_ip)

    def add_wan_interface(self, *iface_id_ip):
        self.wan_interfaces.append(iface_id_ip)

    def add_neighbor(self, *neighbor_ip_asn):
        self.neighbors.append(neighbor_ip_asn)

    def connect_lan(self, router_interface_id):
        self.add_lan_interface(router_interface_id, self.host_gw + '/' + str(LAN_IP_MASK))

    def connect_wan(self, neighbor, interface_ids):
        assert isinstance(neighbor, Region)
        assert len(interface_ids) == 2
        local_intf_id, remote_intf_id = interface_ids
        local_ip, remote_ip = self.get_wan_ip_pair()

        self.add_wan_interface(local_intf_id, local_ip)
        neighbor.add_wan_interface(remote_intf_id, remote_ip)
        self.add_neighbor(remote_ip, neighbor.asn)
        neighbor.add_neighbor(local_ip, self.asn)

    def get_router_info(self):
        router_info = {
            'lan_interfaces': self.lan_interfaces,
            'wan_interfaces': self.wan_interfaces,
            'neighbors': self.neighbors,
            'asn': self.asn,
            'local_ip': self.host_gw + '/' + str(LAN_IP_MASK)
        }
        return router_info
