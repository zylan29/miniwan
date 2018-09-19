from mininet.node import Host


class WanHost(Host):
    """
    WAN host with TrafficGenerator and sflow.
    """

    def set_router(self, router):
        self.router = router
