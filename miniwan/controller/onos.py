import json
import requests

from mininet.node import Host


class ONOSRestOptions(object):
    def __init__(self, ip, port, user, passwd):
        self.ip = ip
        self.port = port
        self.user = user
        self.passwd = passwd

    def add_host(self, host, location):
        # TODO: fix location to of:dpid/port
        assert isinstance(host, Host), TypeError('host should be an instance of mininet.node.Host.')
        host_cfg = {
            'basic': {
                'name': host.name,
                'ips': [host.IP()],
                'locations': ['of:{}/1'.format(location)]
            }
        }
        headers = {'Content-Type': 'application/json'}
        url = 'http://{}:{}/onos/v1/network/configuration/hosts/{}-None'.format(self.ip, self.port, host.MAC())
        print(url)
        return requests.post(url=url, data=json.dumps(host_cfg), auth=(self.user, self.passwd), headers=headers)