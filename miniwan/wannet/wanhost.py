from mininet.node import Host


class WanHost(Host):
    """
    WAN host with TrafficGenerator and sflow.
    """

    def traffic_server(self):
        pass

    def traffic_client(self):
        pass
