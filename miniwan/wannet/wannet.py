import time

from mininet.link import TCLink
from mininet.net import Mininet
from mininet.node import RemoteController

from miniwan.wannet.wanhost import WanHost
from miniwan.wannet.quaggarouter import BGPRouter
from miniwan.wannet.quaggarouter import OSPFRouter
from miniwan.wannet.wantopo import WanTopo


SYSCTL_SLEEP = 5

# TODO: parse from commandline later
CONTROLLER_IP = '127.0.0.1'
CONTROLLER_PORT = 6633

class WanNet(Mininet):
    def __init__(self, topo_desc_file='../conf/simple.yaml', protocol='ospf', **kwargs):
        kwargs['topo'] = WanTopo(topo_desc_file)
        kwargs['link'] = TCLink
        self.protocol = protocol.lower()
        if self.protocol == 'ospf':
            kwargs['switch'] = OSPFRouter
        elif self.protocol == 'bgp':
            kwargs['switch'] = BGPRouter
        else:
            raise ValueError('Unsupported routing protocol: {}.'.format(protocol))
        kwargs['host'] = WanHost
        super(WanNet, self).__init__(**kwargs)

    def start(self):
        super(WanNet, self).start()
        if self.protocol in ['ospf', 'bgp']:
            print('wait {} seconds for sysctl changes to take effect...'.format(SYSCTL_SLEEP))
            time.sleep(SYSCTL_SLEEP)
            for router in self.switches:
                router.start_route()