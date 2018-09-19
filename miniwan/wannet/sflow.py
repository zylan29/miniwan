# This file is copied from sflow-rt/extras/

import array
import fcntl
import re
import socket
import struct
import sys
from json import dumps
from os import listdir, environ

from mininet.util import quietRun
from requests import put

COLLECTOR = environ.get('COLLECTOR', '127.0.0.1')
SAMPLING = environ.get('SAMPLING', '10')
POLLING = environ.get('POLLING', '10')


def getIfInfo(dst):
    is_64bits = sys.maxsize > 2 ** 32
    struct_size = 40 if is_64bits else 32
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    max_possible = 8  # initial value
    while True:
        bytes = max_possible * struct_size
        names = array.array('B')
        for i in range(0, bytes):
            names.append(0)
        outbytes = struct.unpack('iL', fcntl.ioctl(
            s.fileno(),
            0x8912,  # SIOCGIFCONF
            struct.pack('iL', bytes, names.buffer_info()[0])
        ))[0]
        if outbytes == bytes:
            max_possible *= 2
        else:
            break
    namestr = names.tostring()
    s.connect((dst, 0))
    ip = s.getsockname()[0]
    for i in range(0, outbytes, struct_size):
        name = namestr[i:i + 16].split('\0', 1)[0]
        addr = socket.inet_ntoa(namestr[i + 20:i + 24])
        if addr == ip:
            return (name, addr)


def configSFlow(net, collector, ifname):
    print "*** Enabling sFlow:"
    sflow = 'ovs-vsctl -- --id=@sflow create sflow agent=%s target=%s sampling=%s polling=%s --' % (
        ifname, collector, SAMPLING, POLLING)
    for s in net.switches:
        sflow += ' -- set bridge %s sflow=@sflow' % s
    print ' '.join([s.name for s in net.switches])
    quietRun(sflow)


def sendTopology(net, agent, collector):
    print "*** Sending topology"
    topo = {'nodes': {}, 'links': {}}
    for s in net.switches:
        topo['nodes'][s.name] = {'agent': agent, 'ports': {}}
    path = '/sys/devices/virtual/net/'
    for child in listdir(path):
        parts = re.match('(^.+)-(.+)', child)
        if parts == None: continue
        if parts.group(1) in topo['nodes']:
            ifindex = open(path + child + '/ifindex').read().split('\n', 1)[0]
            topo['nodes'][parts.group(1)]['ports'][child] = {'ifindex': ifindex}
    i = 0
    for s1 in net.switches:
        j = 0
        for s2 in net.switches:
            if j > i:
                intfs = s1.connectionsTo(s2)
                for intf in intfs:
                    s1ifIdx = topo['nodes'][s1.name]['ports'][intf[0].name]['ifindex']
                    s2ifIdx = topo['nodes'][s2.name]['ports'][intf[1].name]['ifindex']
                    linkName = '%s-%s' % (s1.name, s2.name)
                    topo['links'][linkName] = {'node1': s1.name, 'port1': intf[0].name, 'node2': s2.name,
                                               'port2': intf[1].name}
            j += 1
        i += 1

    put('http://' + collector + ':8008/topology/json', data=dumps(topo))


def enable_sflow(net, collector=COLLECTOR):
    (ifname, agent) = getIfInfo(collector)
    configSFlow(net, collector, ifname)
    sendTopology(net, agent, collector)
