# miniwan

Emulating WAN by using mininet.

## Introduction

Miniwan generates a WAN topology according to the configuration file `conf/`.
The IP addresses are automatically generated.

Miniwan supports several routing protocols,
* OSPF
* BGP

`/bin/miniwan` does the following works,
1. Parse arguments.
2. Read topology from the configuration file.
3. Add routers and hosts according to the topology, and automatically assign IP addresses to network interfaces.
4. Start routing.
5. Start CLI.

Note: The routing protocols need some time to converge.

## Requirements
Install required packages.
```shell
# apt-get install quagga
# apt-get install python-yaml
```
[Install mininet](http://mininet.org/download/)

[Install TrafficGenerator](https://github.com/HKUST-SING/TrafficGenerator)

[Install sflow]

[Install sflow-rt](https://sflow-rt.com/download.php)

## Setup

## Customize topology

The WAN regions are defined in `regions` section. 
Each region consists of a router and a host.
The region name is only useful for link connections.
 
We can define default bandwidth, delay and loss rate for LAN and WAN links in `defaults` section. 
We can also specific bandwidth, delay and loss rate for each individual WAN link.

We provide topologies that described in Google B4 and Microsoft SWAN papers. 
A very simple topology configuration file is as follows.
```yaml
defaults:
  lan_link:
    default_bw: 100
    default_delay: 0.1ms
    default_loss: 0.001
  wan_link:
    default_bw: 10
    default_delay: 10ms
    default_loss: 0.1
regions:
- name: region1
- name: region2
links:
- src: region1
  dst: region2
```
Note: Quagga configuration files should be in a directory that user `quagga` can access.