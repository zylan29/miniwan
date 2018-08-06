import yaml
from mininet.topo import Topo

from miniwan.wannet.region import Region


class WanTopo(Topo):
    def __init__(self, topo_file='../conf/simple.yaml'):
        Topo.__init__(self)
        with open(topo_file, 'r') as f:
            topo_desc = yaml.load(f)
        if topo_desc is None:
            raise ValueError('Error: Load topology from {}'.format(topo_file))
        regions = {}
        for region in topo_desc['regions']:
            region_name = region['name']
            regions[region_name] = Region(region_name)

        # Connect region host to region router
        for region_name in regions:
            region = regions[region_name]
            host_name, host_ip, host_gw = region.get_host_name_ip_gw()
            self.addHost(host_name, ip=host_ip, defaultRoute='via {}'.format(host_gw))
            router_name = region.get_router_name()
            self.addSwitch(router_name)
            # TODO:set LAN bw, delay and loss
            self.addLink(host_name, router_name)
            _, router_port_id = self.port(host_name, router_name)
            region.connect_lan(router_port_id)
        for link in topo_desc['links']:
            # TODO: use defaults
            bw = link['bw'] if 'bw' in link else 100
            delay = str(link['delay']) + 'ms' if 'delay' in link else '0.1ms'
            loss = link['loss'] if 'loss' in link else 0.01
            src_region = regions[link['src']]
            dst_region = regions[link['dst']]
            src_router = src_region.get_router_name()
            dst_router = dst_region.get_router_name()
            self.addLink(src_router, dst_router, bw=bw, delay=delay, loss=loss)
            src_port_id, dst_port_id = self.port(src_router, dst_router)
            src_region.connect_wan(dst_region, (src_port_id, dst_port_id))
        for region_name in regions:
            router_name = regions[region_name].get_router_name()
            router_info = regions[region_name].get_router_info()
            router_info.update(self.nodeInfo(router_name))
            self.setNodeInfo(router_name, router_info)
