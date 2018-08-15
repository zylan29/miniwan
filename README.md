# miniwan

Emulating WAN by using mininet.

[toc]

## Introduction

Miniwan generates a WAN topology according to the configuration file `conf/`.
The IP addresses are automatically generated.

Miniwan supports several routing protocols,
* OSPF
* BGP

## Prerequirements

```shell
# apt-get install quagga
# apt-get install python-yaml
```

## Topology

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