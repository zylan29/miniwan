from mininet.link import TCLink
from mininet.net import Mininet

from miniwan.wannet.wanhost import WanHost
from miniwan.wannet.wanrouter import BgpRouter
from miniwan.wannet.wanrouter import OspfRouter
from miniwan.wannet.wantopo import WanTopo


class WanNet(Mininet):
    def __init__(self, topo_desc_file='../conf/simple.yaml', protocol='ospf', **kwargs):
        kwargs['topo'] = WanTopo(topo_desc_file)
        kwargs['link'] = TCLink
        if protocol.lower() == 'ospf':
            kwargs['switch'] = OspfRouter
        elif protocol.lower() == 'bgp':
            kwargs['switch'] = BgpRouter
        else:
            raise ValueError('Unsupported routing protocol: {}.'.format(protocol))
        kwargs['host'] = WanHost
        super(WanNet, self).__init__(**kwargs)
