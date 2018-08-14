from mininet.link import TCLink
from mininet.net import Mininet

from miniwan.wannet.wanhost import WanHost
from miniwan.wannet.wanrouter import OspfRouter
from miniwan.wannet.wantopo import WanTopo


class WanNet(Mininet):
    def __init__(self, topo_desc_file='../conf/simple.yaml', **kwargs):
        kwargs['topo'] = WanTopo(topo_desc_file)
        kwargs['link'] = TCLink
        # TODO: generalize switch to a L3 router.
        # TODO: may change BgpRouter to ovs with a controller.
        kwargs['switch'] = OspfRouter
        kwargs['host'] = WanHost
        super(WanNet, self).__init__(**kwargs)
