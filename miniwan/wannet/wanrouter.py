import os

from mininet.node import Switch

NETWORK_FORMATTER = '{}.0.0.0/8'  # ASN


class WanRouter(Switch):
    def __init__(self, name, **kwargs):
        kwargs['inNamespace'] = True
        super(WanRouter, self).__init__(name, **kwargs)
        # Enable forwarding on the router

    def enable_route(self):
        self.cmd('sysctl -w net.ipv4.ip_forward=1')
        self.waitOutput()

    def start_route(self):
        raise NotImplementedError()

    @staticmethod
    def setup():
        return

    def start(self, controllers):
        pass

    def stop(self):
        self.deleteIntfs()


class ZebraRouter(WanRouter):
    def __init__(self, name, **kwargs):
        self.lan_interfaces = kwargs['lan_interfaces']
        self.wan_interfaces = kwargs['wan_interfaces']
        super(ZebraRouter, self).__init__(name, **kwargs)
        self.zebra_cfg_file = ''

    def generate_zebra_cfg(self, dst_path='/etc/quagga/miniwan'):
        host_str = 'hostname {}\n'.format(self.name)
        passwd_str = 'password en\n' + \
                     'enable password en\n'
        lo_str = 'interface lo\n' + \
                 '    ip address 127.0.0.1/8\n'
        intf_str = ''
        for intf_id, intf_ip in self.lan_interfaces + self.wan_interfaces:
            if intf_id == 0:
                lo_str += '    ip address {}\n'.format(intf_ip)
            else:
                intf_name = self.intfs[intf_id]
                intf_str += 'interface {}\n'.format(intf_name) + \
                            '    ip address {}\n'.format(intf_ip)
        log_str = 'log file /tmp/{}-zebra.log\n'.format(self.name) + \
                  'log stdout\n'
        zebra_cfg_str = host_str + passwd_str + lo_str + intf_str + log_str

        if not os.path.exists(dst_path):
            if os.path.exists(os.path.abspath(dst_path + '/..')):
                os.system('mkdir -p {}'.format(dst_path))
            else:
                raise ValueError('{} does NOT exist and cannot be created.'.format(dst_path))
        self.zebra_cfg_file = dst_path + '/zebra-{}.conf'.format(self.name)
        with open(self.zebra_cfg_file, 'w') as f:
            f.write(zebra_cfg_str)

    def start_zebra(self):
        if self.zebra_cfg_file == '' or not os.path.exists(self.zebra_cfg_file):
            raise Exception('Should generate zebra configuration file first.')
        self.cmd('/usr/lib/quagga/zebra -f {} -d -i /tmp/zebra-{}.pid > logs/{}-zebra-stdout 2>&1'.format(
            self.zebra_cfg_file, self.name, self.name))
        self.waitOutput()
        print("Starting zebra on %s" % self.name)

    def stop_quagga(self):
        self.cmd('killall -9 zebra bgpd ospfd')
        self.waitOutput()

    def stop(self):
        self.stop_quagga()
        self.deleteIntfs()


class OspfRouter(ZebraRouter):
    def __init__(self, name, **kwargs):
        self.neighbors = kwargs['neighbors']
        self.local_ip = kwargs['local_ip']
        self.router_id = self.local_ip.split('/')[0]
        self.asn = kwargs['asn']
        super(OspfRouter, self).__init__(name, **kwargs)
        self.ospf_cfg_file = ''

    def start_route(self):
        self.generate_zebra_cfg()
        self.generate_ospf_cfg()
        self.start_zebra()
        self.start_ospfd()

    def generate_ospf_cfg(self, dst_path='/etc/quagga/miniwan'):
        host_name_str = 'hostname {}\n'.format(self.name)
        passwd_str = 'password en\n'
        router_str = 'router ospf\n' + \
                     '    ospf router-id {}\n'.format(self.router_id) + \
                     '    redistribute connected\n'
        router_str += '    network {} area 0\n'.format(self.local_ip)
        for _, network_ip in self.wan_interfaces:
            router_str += '    network {} area 0\n'.format(network_ip)
        log_str = 'log file /tmp/{}-ospfd.log\n'.format(self.name) + \
                  'log stdout\n'
        ospf_cfg_str = host_name_str + passwd_str + router_str + log_str
        if not os.path.exists(dst_path):
            if os.path.exists(os.path.abspath(dst_path + '/..')):
                os.system('mkdir -p {}'.format(dst_path))
            else:
                raise ValueError('{} does NOT exist and cannot be created.'.format(dst_path))
        self.ospf_cfg_file = dst_path + '/ospfd-{}.conf'.format(self.name)
        with open(self.ospf_cfg_file, 'w') as f:
            f.write(ospf_cfg_str)

    def start_ospfd(self):
        if self.ospf_cfg_file == '' or not os.path.exists(self.ospf_cfg_file):
            raise Exception('Should generate ospfd configuration file first.')
        self.cmd('/usr/lib/quagga/ospfd -f {} -d -i /tmp/ospfd-{}.pid > logs/{}-ospfd-stdout 2>&1'.format(
            self.ospf_cfg_file, self.name, self.name), shell=True)
        self.waitOutput()
        print("Starting ospfd on %s" % self.name)


class BgpRouter(ZebraRouter):
    def __init__(self, name, **kwargs):
        self.neighbors = kwargs['neighbors']
        self.local_ip = kwargs['local_ip']
        self.router_id = self.local_ip.split('/')[0]
        self.asn = kwargs['asn']
        super(BgpRouter, self).__init__(name, **kwargs)
        self.bgp_cfg_file = ''

    def start_route(self):
        self.generate_zebra_cfg()
        self.generate_bgp_cfg()
        self.start_zebra()
        self.start_bgpd()

    def generate_bgp_cfg(self, dst_path='/etc/quagga/miniwan'):
        host_name_str = 'hostname {}\n'.format(self.name)
        passwd_str = 'password en\n' + \
                     'enable password en\n'
        router_str = 'router bgp {}\n'.format(self.asn) + \
                     '    bgp router-id {}\n'.format(self.router_id) + \
                     '    redistribute connected\n'
        router_str += '    network {}\n'.format(self.local_ip)
        for neighbor_ip, neighbor_asn in self.neighbors:
            router_str += '    neighbor {} remote-as {}\n'.format(neighbor_ip.split('/')[0], neighbor_asn)
            router_str += '    neighbor {} timers 5 5\n'.format(neighbor_ip.split('/')[0])
        log_str = 'log file /tmp/{}-bgpd.log\n'.format(self.name) + \
                  'log stdout\n'
        bgp_cfg_str = host_name_str + passwd_str + router_str + log_str
        if not os.path.exists(dst_path):
            if os.path.exists(os.path.abspath(dst_path + '/..')):
                os.system('mkdir -p {}'.format(dst_path))
            else:
                raise ValueError('{} does NOT exist and cannot be created.'.format(dst_path))
        self.bgp_cfg_file = dst_path + '/bgpd-{}.conf'.format(self.name)
        with open(self.bgp_cfg_file, 'w') as f:
            f.write(bgp_cfg_str)

    def start_bgpd(self):
        if self.bgp_cfg_file == '' or not os.path.exists(self.bgp_cfg_file):
            raise Exception('Should generate bgpd configuration file first.')
        self.cmd('/usr/lib/quagga/bgpd -f {} -d -i /tmp/ospfd-{}.pid > logs/{}-ospfd-stdout 2>&1'.format(
            self.bgp_cfg_file, self.name, self.name), shell=True)
        self.waitOutput()
        print("Starting bgpd on %s" % self.name)
