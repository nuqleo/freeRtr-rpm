%undefine _missing_build_ids_terminate_build

Name:           freerouter
Version:        23.1.9
Release:        1%{?dist}
Summary:        Free, open source router OS process

License:        CC-BY-SA
URL:            http://www.freertr.org/
Source0:        https://github.com/rare-freertr/freeRtr/archive/refs/tags/v%{?version}.tar.gz
%if 0%{?fedora} || 0%{?rhel} > 7
Recommends:     socat
Recommends:     freerouter-native
BuildRequires:  systemd-rpm-macros
BuildRequires:  libbpf-devel
BuildRequires:  openssl-devel
%else
BuildRequires:  openssl1.1-devel
%endif
BuildRequires:  clang
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
%if 0%{?fedora} || 0%{?rhel} > 7
Recommends:     dpdk-tools
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

%build
pushd src
./cj.sh
./cp.sh
popd

pushd misc/native
sed -i '/strip/d' c.sh
./c.sh
popd

%install
find binTmp -size 0 -print -delete
find misc/demo -type f -not -name '*.txt' -delete
sed -i 's|/usr/bin/freerouter|/usr/lib/jvm/jre-11-openjdk/bin/java -jar /usr/share/java/rtr.jar|g' misc/debian2/freerouter.service

mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_javadir}
mkdir -p %{buildroot}%{_unitdir}
mkdir -p %{buildroot}%{_datadir}/freerouter
mkdir -p %{buildroot}%{_sysconfdir}/freerouter/interfaces
mkdir -p %{buildroot}%{_sharedstatedir}/freerouter

install -m644 src/rtr.jar %{buildroot}%{_javadir}
install -m755 binTmp/*.bin %{buildroot}%{_bindir}
install -m755 misc/debian2/interface.sh %{buildroot}%{_datadir}/freerouter/
install -m644 misc/debian2/interface.cpu_port %{buildroot}%{_sysconfdir}/freerouter/interfaces/cpu_port
install -m644 misc/debian2/rtr-hw.txt misc/debian2/rtr-sw.txt %{buildroot}%{_sysconfdir}/freerouter
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
%doc misc/demo misc/captures readme.md changelog.txt todo.txt
%dir %attr(0755,freerouter,freerouter) %{_sharedstatedir}/freerouter
%dir %attr(0770,freerouter,freerouter) %{_sysconfdir}/freerouter
%attr(0644,freerouter,freerouter) %config(noreplace) %{_sysconfdir}/freerouter/rtr-hw.txt
%attr(0644,freerouter,freerouter) %config(noreplace) %{_sysconfdir}/freerouter/rtr-sw.txt
%{_javadir}/rtr.jar
%{_unitdir}/freerouter.service
%{_unitdir}/freerouter@.service

%files native
%dir %{_sysconfdir}/freerouter/interfaces
%config(noreplace) %{_sysconfdir}/freerouter/interfaces/cpu_port
%{_bindir}/*.bin
%{_datadir}/freerouter/
%{_unitdir}/freerouter-native@.service

%files doc
%doc cfg
