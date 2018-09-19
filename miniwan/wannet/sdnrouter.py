import json

from mininet.node import OVSSwitch

from miniwan.wannet.region import INTERFACE_NAME_FORMATTER


class SegmentRouter(OVSSwitch):
    routers = []
    SRGB = 16000
    sr_cfg_file = ''

    def __init__(self, name, **kwargs):
        self.neighbors = kwargs['neighbors']
        self.local_intf_id = kwargs['local_intf_id']
        self.local_ip = kwargs['local_ip']
        self.router_id = self.local_ip.split('/')[0]
        self.asn = kwargs['asn']
        super(SegmentRouter, self).__init__(name, **kwargs)
        SegmentRouter.routers.append(self)

    @staticmethod
    def generate_sr_cfg(dst_path='.'):
        sr_cfg = {
            'comment': 'Miniwan topology description and configuration',
            'restrictSwitches': True,
            'restrictLinks': True,
            'switchConfig': []
        }
        for router in SegmentRouter.routers:
            router_cfg = {
                'nodeDpid': 'of:' + str(router.dpid),
                'name': router.name,
                'type': 'Router_SR',
                'allowed': True,
                'latitude': '80.80',
                'longitude': '90.10',
                'params': {
                    'routerIp': router.router_id,
                    'routerMac': router.MAC(INTERFACE_NAME_FORMATTER.format(router.name, router.local_intf_id)),
                    'nodeSid': SegmentRouter.SRGB + router.asn,
                    # TODO: support core router later
                    'isEdgeRouter': True,
                    'subnets': [
                        {
                            "portNo": router.local_intf_id,
                            'subnetIp': router.local_ip
                        }
                    ]
                }
            }
            sr_cfg['switchConfig'].append(router_cfg)
        SegmentRouter.sr_cfg_file = dst_path + '/sr.json'
        with open(SegmentRouter.sr_cfg_file, 'w') as f:
            f.write(json.dumps(sr_cfg))

    @staticmethod
    def start_route():
        SegmentRouter.generate_sr_cfg()
