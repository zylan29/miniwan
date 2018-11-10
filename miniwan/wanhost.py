from mininet.node import Host


class WanHost(Host):
    """
    WAN host with TrafficGenerator and sflow.
    """
    def __init__(self, name, inNamespace=True, **params):
        super(WanHost, self).__init__(name, inNamespace, **params)
