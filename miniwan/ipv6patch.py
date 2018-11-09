"""
Patch mininet to support IPv6
"""


from mininet.link import Intf
from mininet.node import Host


def setIPv6Intf(self, ipv6str, ipv6PrefixLen=None):
    """
    Patch for class mininet.link.Intf
    """
    if '/' in ipv6str:
        self.ipv6, self.ipv6PrefixLen = ipv6str.split('/')
    else:
        if ipv6str is None:
            raise Exception('No prefix length set for IP address %s' % (ipv6str,))
        self.ipv6, self.ipv6PrefixLen = ipv6str, ipv6PrefixLen
    return self.ifconfig('inet6 add %s/%s' % (self.ipv6, self.ipv6PrefixLen))


def IPv6Intf(self):
    return self.ipv6


def configIntfWrapper(func):
    def wrapper(self, ipv6_str=None, **kwargs):
        r = func(self, **kwargs)
        self.setParam(r, 'setIPv6', ipv6=ipv6_str)
        return r
    return wrapper


def setIPv6Host( self, ipv6, ipv6PrefixLen=8, intf=None, **kwargs ):
    """Set the IP address for an interface.
        intf: intf or intf name
        ip: IP address as a string
        prefixLen: prefix length, e.g. 8 for /8 or 16M addrs
        kwargs: any additional arguments for intf.setIP"""
    return self.intf( intf ).setIPv6( ipv6, ipv6PrefixLen, **kwargs )


def setDefaultRouteIPv6Host(self, intf=None):
    """
    Patch for class mininet.node.Host
    """
    if isinstance(intf, basestring) and ' ' in intf:
        params = intf
    else:
        params = 'dev %s' % intf
    # Do this in one line in case we're messing with the root namespace
    self.cmd('ip -6 route del default; ip -6 route add default', params)


def configHostWrapper(func):
    def wrapper(self, ipv6=None, defaultIPv6Route=None, **kwargs):
        r = func(self, **kwargs)
        self.setParam(r, 'setIPv6', ipv6=ipv6)
        self.setParam(r, 'setDefaultRouteIPv6', defaultIPv6Route=defaultIPv6Route)
        return r
    return wrapper


def applyIPv6Patch():
    """
    Enable IPv6.
    Apply IPv6 patch to mininet.
    """
    Intf.setIPv6 = setIPv6Intf
    Intf.IPv6 = IPv6Intf
    Intf.config = configIntfWrapper(Intf.config)

    Host.setIPv6 = setIPv6Host
    Host.setDefaultRouteIPv6 = setDefaultRouteIPv6Host
    Host.config = configHostWrapper(Host.config)
