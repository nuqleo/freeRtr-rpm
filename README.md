# freeRtr RPM Packages

This repository contains RPM spec and systemd configuration files for building *[freeRtr](http://www.freertr.org/)* packages.

*[freeRouter](https://github.com/mc36/freeRtr)* is a free, open source router process and some dataplanes.

The spec file is mainly used to build RPMs in COPR. Prebuilt packages are available for:

- Fedora
- Enterprise Linux 8–10 (RHEL, CentOS Stream, AlmaLinux, Rocky)
- openSUSE Tumbleweed
- openEuler

You can use this repository to build your own packages or get them directly from [COPR](https://copr.fedorainfracloud.org/coprs/nucleo/freerouter/).

## Notes

systemd-networkd configuration for `veth250` and `veth251` is required, as these interfaces are used by `freerouter-native@cpu_port` and `freerouter-p4` services for communication between dataplanes and the main freeRouter process.
