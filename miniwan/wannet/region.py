ROUTER_NAME_FORMATTER = 'r{}'
HOST_NAME_FORMATTER = 'h{}'
INTERFACE_NAME_FORMATTER = '{}-eth{}'

# IPv4 address formatter
LAN_IP_MASK = 24
HOST_GW_FORMATTER = '10.{}.1.1'  # ASN
HOST_IP_FORMATTER = '10.{}.1.2/' + str(LAN_IP_MASK)  # ASN
LAN_IP_FORMATTER = HOST_GW_FORMATTER + '/' + str(LAN_IP_MASK)
LINK_IP_FORMATTER = '99.{}.{}.{}' + '/' + str(LAN_IP_MASK)  # 99.x.y.x, x < y

# IPv6 address formatter
LAN_IPV6_MASK = 112
HOST_GW_IPV6_FORMATTER = '2001::10:{}:1:1'
HOST_IPV6_FORMATTER = '2001::10:{}:1:2' + '/' + str(LAN_IPV6_MASK)
LAN_IPV6_FORMATTER = HOST_GW_IPV6_FORMATTER + '/' + str(LAN_IPV6_MASK)
LINK_IPV6_FORMATTER = '2001::99:{}:{}:{}' + '/' + str(LAN_IPV6_MASK)  # 2001::99:x:y:x, x < y


class Region(object):
    """"
    Generate IP and other configurations for routers and hosts.
    1 router and 1 host per region.
    """
    ASN = 1

    def __init__(self, name, ip_ver='all'):
        self.name = name
        self.ip_ver = ip_ver
        self.asn = Region.ASN
        Region.ASN += 1
        self.num_wan_ip = 0

        self.lan_interfaces = []
        self.wan_interfaces = []
        self.neighbors = []

        self.router_name = ROUTER_NAME_FORMATTER.format(self.asn)
        self.router_id = LAN_IP_FORMATTER.format(self.asn).split('/')[0]

        self.lan_intf_id = -1
        self.lan_intf_ip = LAN_IP_FORMATTER.format(self.asn) if self.ip_ver in ['ipv4', 'all'] else ''
        self.lan_intf_ipv6 = LAN_IPV6_FORMATTER.format(self.asn) if self.ip_ver in ['ipv6', 'all'] else ''

        self.host_name = HOST_NAME_FORMATTER.format(self.asn)
        self.host_gw = HOST_GW_FORMATTER.format(self.asn)
        self.host_ip = HOST_IP_FORMATTER.format(self.asn)
        self.host_gw_ipv6 = HOST_GW_IPV6_FORMATTER.format(self.asn)
        self.host_ipv6 = HOST_IPV6_FORMATTER.format(self.asn)

    def get_router_name(self):
        return self.router_name

    def get_host_name(self):
        return self.host_name

    def get_host_name_ip_gw(self):
        return self.host_name, self.host_ip, self.host_gw

    def add_lan_interface(self, *iface_id_ip_ipv6):
        self.lan_interfaces.append(iface_id_ip_ipv6)

    def add_wan_interface(self, *iface_id_ip_ipv6):
        self.wan_interfaces.append(iface_id_ip_ipv6)

    def add_neighbor(self, *neighbor_asn_ip_ipv6):
        self.neighbors.append(neighbor_asn_ip_ipv6)

    def connect_lan(self, router_interface_id):
        self.lan_intf_id = router_interface_id
        self.add_lan_interface(router_interface_id, self.lan_intf_ip, self.lan_intf_ipv6)

    def connect_wan(self, neighbor, interface_ids):
        assert isinstance(neighbor, Region)
        assert len(interface_ids) == 2
        local_intf_id, remote_intf_id = interface_ids

        x, y = self.asn, neighbor.asn
        if x > y:
            x, y = y, x

        local_ip, remote_ip, local_ipv6, remote_ipv6 = '', '', '', ''
        if self.ip_ver in ['ipv4', 'all']:
            local_ip = LINK_IP_FORMATTER.format(x, y, self.asn)
            remote_ip = LINK_IP_FORMATTER.format(x, y, neighbor.asn)
        if self.ip_ver in ['ipv6', 'all']:
            local_ipv6 = LINK_IPV6_FORMATTER.format(x, y, self.asn)
            remote_ipv6 = LINK_IPV6_FORMATTER.format(x, y, neighbor.asn)

        self.add_wan_interface(local_intf_id, local_ip, local_ipv6)
        neighbor.add_wan_interface(remote_intf_id, remote_ip, remote_ipv6)
        self.add_neighbor(neighbor.asn, remote_ip, remote_ipv6)
        neighbor.add_neighbor(self.asn, local_ip, local_ipv6)

    def get_router_info(self):
        return {
            'router_id': self.router_id,
            'lan_interfaces': self.lan_interfaces,
            'wan_interfaces': self.wan_interfaces,
            'neighbors': self.neighbors,
            'asn': self.asn,
            'local_ip': self.lan_intf_ip,
            'local_ipv6': self.lan_intf_ipv6,
            'local_intf_id': self.lan_intf_id
        }

    def get_host_info(self):
        host_info = {}
        if self.ip_ver in ['ipv4', 'all']:
            host_info['ip'] = self.host_ip
            host_info['defaultRoute'] = 'via {}'.format(self.host_gw)
        if self.ip_ver in ['ipv6', 'all']:
            host_info['ipv6'] = self.host_ipv6
            host_info['defaultIPv6Route'] = 'via {}'.format(self.host_gw_ipv6)
        return host_info
