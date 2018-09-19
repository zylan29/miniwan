import time

from mininet.link import TCLink
from mininet.net import Mininet
from mininet.node import RemoteController

from miniwan.wannet.wanhost import WanHost
from miniwan.wannet.quaggarouter import BGPRouter
from miniwan.wannet.quaggarouter import OSPFRouter
from miniwan.wannet.sdnrouter import SegmentRouter
from miniwan.wannet.wantopo import WanTopo
from miniwan.controller.onos import ONOSRestOptions

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
        elif self.protocol == 'sr':
            kwargs['switch'] = SegmentRouter
        else:
            raise ValueError('Unsupported routing protocol: {}.'.format(protocol))
        kwargs['host'] = WanHost
        kwargs['controller'] = lambda name: RemoteController(name, CONTROLLER_IP, CONTROLLER_PORT)
        super(WanNet, self).__init__(**kwargs)

    def start(self):
        super(WanNet, self).start()
        if self.protocol in ['ospf', 'bgp']:
            print('wait {} seconds for sysctl changes to take effect...'.format(SYSCTL_SLEEP))
            time.sleep(SYSCTL_SLEEP)
            for router in self.switches:
                router.start_route()
        elif self.protocol in ['sr']:
            onos_rest_options = ONOSRestOptions('127.0.0.1', '8181', 'onos', 'rocks')
            for host in self.hosts:
                router = self.getNodeByName(self.topo.get_router_name(host.name))
                print(onos_rest_options.add_host(host, router.dpid))