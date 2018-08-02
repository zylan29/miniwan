import os

from mininet.node import Switch

NETWORK_FORMATTER = '{}.0.0.0/8'  # ASN


class WanRouter(Switch):
    def __init__(self, name, **kwargs):
        kwargs['inNamespace'] = True
        super(WanRouter, self).__init__(name, **kwargs)
        # Enable forwarding on the router
        self.cmd('sysctl net.ipv4.ip_forward=1')
        self.waitOutput()

    @staticmethod
    def setup():
        return

    def start(self, controllers):
        pass

    def stop(self):
        self.deleteIntfs()


class BgpRouter(WanRouter):
    def __init__(self, name, **kwargs):
        self.interfaces = kwargs['interfaces']
        self.neighbors = kwargs['neighbors']
        self.router_id = kwargs['router_id']
        self.asn = kwargs['asn']
        super(BgpRouter, self).__init__(name, **kwargs)
        self.zebra_cfg_file = ''
        self.bgpd_cfg_file = ''

    def start(self, controllers):
        self.generate_zebra_cfg()
        self.generate_bgp_cfg()
        self.strart_zebra()
        self.start_bgpd()

    def stop(self):
        super(BgpRouter, self).stop()
        self.stop_quagga()

    def generate_zebra_cfg(self, dst_path='/etc/quagga/miniwan'):
        host_str = 'hostname {}\n'.format(self.name)
        passwd_str = 'password en\n' + \
                     'enable password en\n'
        lo_str = 'interface lo\n' + \
                 '    ip address 127.0.0.1/8\n'
        intf_str = ''
        for intf_name, intf_ip in self.interfaces:
            if intf_name == 'lo':
                lo_str += '    ip address {}\n'.format(intf_ip)
            else:
                intf_str += 'interface {}\n'.format(intf_name) + \
                            '    ip address {}\n'.format(intf_ip)
        # TODO: log
        log_str = 'log stdout\n'
        zebra_cfg_str = host_str + passwd_str + lo_str + intf_str + log_str

        if not os.path.exists(dst_path):
            if os.path.exists(os.path.abspath(dst_path + '/..')):
                os.system('mkdir -p {}'.format(dst_path))
            else:
                raise ValueError('{} does NOT exist and cannot be created.'.format(dst_path))
        self.zebra_cfg_file = dst_path + '/zebra-{}.conf'.format(self.name)
        with open(self.zebra_cfg_file, 'w') as f:
            f.write(zebra_cfg_str)

    def generate_bgp_cfg(self, dst_path='/etc/quagga/miniwan'):
        host_name_str = 'hostname {}\n'.format(self.name)
        passwd_str = 'password en\n' + \
                     'enable password en\n'
        router_str = 'router bgp {}\n'.format(self.asn) + \
                     '    bgp router-id {}\n'.format(self.router_id) + \
                     '    network ' + NETWORK_FORMATTER.format(self.asn) + '\n'
        for neighbor_ip, neighbor_asn in self.neighbors:
            router_str += '    neighbor {} remote-as {}\n'.format(neighbor_ip, neighbor_asn)
            # TODO: timers
            router_str += '    neighbor {} timers 5 5\n'.format(neighbor_ip)
        # TODO: log
        log_str = 'log stdout\n'

        bgpd_cfg_str = host_name_str + passwd_str + router_str + log_str
        if not os.path.exists(dst_path):
            if os.path.exists(os.path.abspath(dst_path + '/..')):
                os.system('mkdir -p {}'.format(dst_path))
            else:
                raise ValueError('{} does NOT exist and cannot be created.'.format(dst_path))
        self.bgpd_cfg_file = dst_path + '/bgpd-{}.conf'.format(self.name)
        with open(self.bgpd_cfg_file, 'w') as f:
            f.write(bgpd_cfg_str)

    def strart_zebra(self):
        if self.zebra_cfg_file == '' or not os.path.exists(self.zebra_cfg_file):
            raise Exception('Should generate zebra configuration file first.')
        self.cmd('/usr/lib/quagga/zebra -f {} -d -i /tmp/zebra-{}.pid > logs/{}-zebra-stdout 2>&1'.format(
            self.zebra_cfg_file, self.name, self.name))
        self.waitOutput()
        print("Starting zebra on %s" % self.name)

    def start_bgpd(self):
        if self.bgpd_cfg_file == '' or not os.path.exists(self.bgpd_cfg_file):
            raise Exception('Should generate bgpd configuration file first.')
        self.cmd('/usr/lib/quagga/bgpd -f {} -d -i /tmp/bgpd-{}.pid > logs/{}-bgpd-stdout 2>&1'.format(
            self.bgpd_cfg_file, self.name, self.name), shell=True)
        self.waitOutput()
        print("Starting bgpd on %s" % self.name)

    def stop_quagga(self):
        self.cmd('killall -9 zebra bgpd ospfd')
        self.waitOutput()
