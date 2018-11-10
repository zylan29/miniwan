from mininet.link import TCLink
from mininet.net import Mininet

from miniwan.wanhost import WanHost
from miniwan.quaggarouter import BgpRouter
from miniwan.quaggarouter import OspfRouter
from miniwan.wantopo import WanTopo
from miniwan.ipv6patch import applyIPv6Patch

SYSCTL_SLEEP = 5

# TODO: parse from commandline later
CONTROLLER_IP = '127.0.0.1'
CONTROLLER_PORT = 6633


class WanNet(Mininet):
    def __init__(self, topo_desc_file='../conf/simple.yaml', protocol='ospf', ip_ver='all', **kwargs):
        if ip_ver in ['ipv6', 'all']:
            applyIPv6Patch()
        self.ip_ver = ip_ver
        kwargs['topo'] = WanTopo(topo_desc_file, ip_ver)
        kwargs['link'] = TCLink
        kwargs['host'] = WanHost
        self.protocol = protocol.lower()
        if self.protocol == 'ospf':
            kwargs['switch'] = OspfRouter
        elif self.protocol == 'bgp':
            kwargs['switch'] = BgpRouter
        else:
            raise ValueError('Unsupported routing protocol: {}.'.format(protocol))
        super(WanNet, self).__init__(**kwargs)