from mininet.link import TCLink
from mininet.net import Mininet

from miniwan.wannet.wanrouter import BgpRouter
from miniwan.wannet.wantopo import WanTopo


class WanNet(Mininet):
    def __init__(self, topo_desc_file='../conf/simple.yaml', **kwargs):
        kwargs['topo'] = WanTopo(topo_desc_file)
        kwargs['link'] = TCLink
        kwargs['switch'] = BgpRouter
        super(WanNet, self).__init__(**kwargs)
