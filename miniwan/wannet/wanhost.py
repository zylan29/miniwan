from mininet.node import Host


class WanHost(Host):
    """
    WAN host with TrafficGenerator and sflow.
    """
    def __init__(self, name, inNamespace=True, **params):
        super(WanHost, self).__init__(name, inNamespace, **params)
        self.host_ipv6 = params['host_ipv6']
        self.host_gw_ipv6 = params['host_gw_ipv6']

    def config_ipv6(self):
        self.cmd('sysctl -w net.ipv6.conf.all.disable_ipv6=0')
        self.waitOutput()
        self.cmd('sysctl -w net.ipv6.conf.default.disable_ipv6=0')
        self.waitOutput()
        self.cmd('ifconfig {}-eth0 inet6 add {}'.format(self.name, self.host_ipv6))
        self.waitOutput()
        self.cmd('ip -6 route del default;ip -6 route add default dev {}-eth0 via {}'.format(self.name, self.host_gw_ipv6))
        self.waitOutput()

    def set_router(self, router):
        self.router = router
