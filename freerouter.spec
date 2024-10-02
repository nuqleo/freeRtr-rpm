%undefine _missing_build_ids_terminate_build
%undefine _debugsource_packages

Name:           freerouter
Version:        24.10.1
Release:        1%{?dist}
Summary:        Free, open source router OS process

License:        CC-BY-SA
URL:            http://www.freertr.org/
Source0:        https://github.com/mc36/freeRtr/archive/refs/tags/v%{?version}.tar.gz
Source1:        freerouter-p4dpdk.service
Source2:        freerouter-p4dpdk-pkt.service
Source3:        freerouter-p4emu.service
Source4:        freerouter-p4mnl.service
Source5:        freerouter-p4udp.service
Source6:        freerouter-p4urng.service
Source7:        freerouter-p4xdp.service
Source8:        freerouter-p4xsk.service
Source9:        10-virtio.link
Source10:       20-veth.link
Source11:       veth250.network
Source12:       veth251.network
Source13:       veth251.netdev
Source14:       80-freerouter.conf

%if 0%{?rhel} == 7
BuildRequires:  openssl1.1-devel
%else
BuildRequires:  openssl-devel
BuildRequires:  liburing-devel
BuildRequires:  libxdp-devel
Recommends:     freerouter-native
Recommends:     socat
%endif
BuildRequires:  systemd
BuildRequires:  clang llvm
BuildRequires:  dpdk-devel
BuildRequires:  libpcap-devel
BuildRequires:  libmnl-devel
BuildRequires:  java-11-openjdk-devel
Requires:       java-11-openjdk-headless

%description
freeRouter speaks routing protocols, and (re)encapsulates packets on
interfaces since it handles packets itself, it is independent of
underlaying os capabilities (optionally, it can export forwarding tables
through openflow to external switch) since it is an unprivilegized process,
it receives and sends packets through sockets there are external, privileged
processes that place traffic to these sockets (it means that internet can
be used as backplane for router processes) the command line tries to
mimic the industry standards with one exception: no global routing table:
every routed interface must be in a virtual routing table positive side
effect: there are no vrf-awareness questions

%package native
Summary:        Native tools for better performance than socat
Requires:       %{name} = %{version}-%{release}
%if 0%{?rhel} != 7
Recommends:     dpdk-tools xdp-tools systemd-networkd
%endif

%description native
These tools are completely optional but should deliver better performance
than socat.


%package doc
BuildArch:      noarch
Summary:        Examples of freeRouter test configurations
Requires:       %{name} = %{version}-%{release}

%description doc
Examples of freeRouter test configurations.


%prep
%setup -q -n freeRtr-%{?version}
cp %{SOURCE1} %{SOURCE2} %{SOURCE3} %{SOURCE4} %{SOURCE5} %{SOURCE6} %{SOURCE7} %{SOURCE8} .

%build
pushd src
./cj.sh
./cp.sh
popd

pushd misc/native
sed -i '/^strip/d' c.sh
./c.sh
popd

%install
find binTmp -size 0 -print -delete
find misc/demo -type f -not -name '*.txt' -delete
sed -i 's|/usr/bin/freerouter|/usr/lib/jvm/jre-11-openjdk/bin/java -jar /usr/share/java/rtr.jar|g' misc/debian2/freerouter.service

mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_libdir}
mkdir -p %{buildroot}%{_javadir}
mkdir -p %{buildroot}%{_unitdir}
mkdir -p %{buildroot}%{_datadir}/freerouter
mkdir -p %{buildroot}%{_sysconfdir}/sysctl.d
mkdir -p %{buildroot}%{_sysconfdir}/freerouter/interfaces
mkdir -p %{buildroot}%{_sysconfdir}/systemd/network
mkdir -p %{buildroot}%{_sharedstatedir}/freerouter

install -m644 src/rtr.jar %{buildroot}%{_javadir}
cp binTmp/*.bin %{buildroot}%{_bindir}
install -m755 binTmp/*.so %{buildroot}%{_libdir}
install -m755 misc/debian2/interface.sh %{buildroot}%{_datadir}/freerouter/
install -m644 misc/debian2/interface.cpu_port %{buildroot}%{_sysconfdir}/freerouter/interfaces/cpu_port
install -m644 misc/debian2/rtr-hw.txt misc/debian2/rtr-sw.txt %{buildroot}%{_sysconfdir}/freerouter/
install -m644 %{SOURCE9} %{SOURCE10} %{SOURCE11} %{SOURCE12} %{SOURCE13} %{buildroot}%{_sysconfdir}/systemd/network/
install -m644 %{SOURCE14} %{buildroot}%{_sysconfdir}/sysctl.d/
install -m644 misc/debian2/freerouter-native@.service %{buildroot}%{_unitdir}
install -m644 misc/debian2/freerouter.service %{buildroot}%{_unitdir}
install -m644 misc/debian2/freerouter.service %{buildroot}%{_unitdir}/freerouter@.service
sed -i 's|rtr-|%i-|g' %{buildroot}%{_unitdir}/freerouter@.service

%pre
getent group freerouter >/dev/null 2>&1 || groupadd -r freerouter >/dev/null 2>&1 || :
getent passwd freerouter >/dev/null 2>&1 || useradd -M -r -g freerouter -s /sbin/nologin \
 -c "freeRouter OS process" -d %{_sharedstatedir}/freerouter freerouter || :
usermod -aG dialout freerouter

%post
%systemd_post freerouter.service
%systemd_post freerouter@\*.service

%preun
%systemd_preun freerouter.service
%systemd_preun freerouter@\*.service

%postun
%systemd_postun_with_restart freerouter.service
%systemd_postun_with_restart freerouter@\*.service

%post native
%systemd_post freerouter-native@\*.service

%preun native
%systemd_preun freerouter-native@\*.service

%postun native
%systemd_postun_with_restart freerouter-native@\*.service


%files
%license misc/debian2/copyright
%doc misc/demo misc/captures readme.md changelog.txt todo.txt rtr-hw.txt rtr-sw.txt
%dir %attr(0755,freerouter,freerouter) %{_sharedstatedir}/freerouter
%dir %attr(0770,freerouter,freerouter) %{_sysconfdir}/freerouter
%attr(0644,freerouter,freerouter) %config(noreplace) %{_sysconfdir}/freerouter/rtr-hw.txt
%attr(0644,freerouter,freerouter) %config(noreplace) %{_sysconfdir}/freerouter/rtr-sw.txt
%{_javadir}/rtr.jar
%{_unitdir}/freerouter.service
%{_unitdir}/freerouter@.service

%files native
%doc freerouter-p4dpdk.service freerouter-p4dpdk-pkt.service
%doc freerouter-p4emu.service freerouter-p4mnl.service
%doc freerouter-p4udp.service freerouter-p4urng.service
%doc freerouter-p4xdp.service freerouter-p4xsk.service
%dir %{_sysconfdir}/freerouter/interfaces
%config(noreplace) %{_sysconfdir}/sysctl.d/80-freerouter.conf
%config(noreplace) %{_sysconfdir}/freerouter/interfaces/cpu_port
%config(noreplace) %{_sysconfdir}/systemd/network/*
%{_bindir}/*.bin
%{_libdir}/*.so
%{_datadir}/freerouter/
%{_unitdir}/freerouter-native@.service

%files doc
%doc cfg
