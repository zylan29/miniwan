import time

from mininet.link import TCLink
from mininet.net import Mininet
from mininet.node import RemoteController

from miniwan.wannet.sflow import enable_sflow
from miniwan.wannet.wanhost import WanHost
from miniwan.wannet.wanrouter import BGPRouter
from miniwan.wannet.wanrouter import OSPFRouter
from miniwan.wannet.wanrouter import OpenflowRouter
from miniwan.wannet.wantopo import WanTopo

SYSCTL_SLEEP = 5


class WanNet(Mininet):
    def __init__(self, topo_desc_file='../conf/simple.yaml', protocol='ospf', **kwargs):
        kwargs['topo'] = WanTopo(topo_desc_file)
        kwargs['link'] = TCLink
        self.protocol = protocol.lower()
        if self.protocol == 'ospf':
            kwargs['switch'] = OSPFRouter
        elif self.protocol == 'bgp':
            kwargs['switch'] = BGPRouter
        elif self.protocol == 'openflow':
            kwargs['switch'] = OpenflowRouter
        else:
            raise ValueError('Unsupported routing protocol: {}.'.format(protocol))
        kwargs['host'] = WanHost
        # TODO: To support controller
        kwargs['controller'] = lambda name: RemoteController(name, '127.0.0.1', 6633)
        super(WanNet, self).__init__(**kwargs)

    def start(self):
        super(WanNet, self).start()
        if self.protocol in ['ospf', 'bgp']:
            for router in self.switches:
                router.enable_route()
            print('wait {} seconds for sysctl changes to take effect...'.format(SYSCTL_SLEEP))
            time.sleep(SYSCTL_SLEEP)
            for router in self.switches:
                router.start_route()
        elif self.protocol in ['openflow']:
            enable_sflow(self)
