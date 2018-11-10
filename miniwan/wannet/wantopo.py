import yaml
from mininet.topo import Topo

from miniwan.wannet.region import Region


class WanTopo(Topo):
    def __init__(self, topo_file='../conf/simple.yaml', ip_ver='all'):
        Topo.__init__(self)
        with open(topo_file, 'r') as f:
            topo_desc = yaml.load(f)
        if topo_desc is None:
            raise ValueError('Error: Load topology from {}'.format(topo_file))

        self.ip_ver = ip_ver

        lan_link_defaults = topo_desc['defaults']['lan_link']
        wan_link_defaults = topo_desc['defaults']['wan_link']

        regions = {}
        for region in topo_desc['regions']:
            region_name = region['name']
            regions[region_name] = Region(region_name, self.ip_ver)

        # Connect region host to region router
        for region_name in regions:
            region = regions[region_name]
            host_name = region.get_host_name()
            self.addHost(host_name, **region.get_host_info())
            router_name = region.get_router_name()
            self.addSwitch(router_name)
            bw = lan_link_defaults['default_bw']
            delay = lan_link_defaults['default_delay']
            loss = lan_link_defaults['default_loss']
            self.addLink(host_name, router_name, bw=bw, delay=delay, loss=loss)
            _, router_port_id = self.port(host_name, router_name)
            region.connect_lan(router_port_id)
        for link in topo_desc['links']:
            bw = link['bw'] if 'bw' in link else wan_link_defaults['default_bw']
            delay = str(link['delay']) if 'delay' in link else wan_link_defaults['default_delay']
            loss = link['loss'] if 'loss' in link else wan_link_defaults['default_loss']
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
