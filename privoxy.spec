%define privoxyconf %{_sysconfdir}/%{name}
%define reltype stable

Summary:	Privacy enhancing HTTP proxy
Name:		privoxy
Version:	3.0.33
Release:	1
License:	GPLv2+
Group:		Networking/Other
URL:		http://www.privoxy.org/

Source0:	http://prdownloads.sf.net/ijbswa/%{name}-%{version}-%{reltype}-src.tar.gz
Source1:	http://prdownloads.sf.net/ijbswa/%{name}-%{version}-%{reltype}-src.tar.gz.asc
Source2:	%{name}.logrotate
Source4:	%{name}.service

BuildRequires:	man
BuildRequires:	pkgconfig(libpcreposix)
BuildRequires:	pkgconfig(zlib)
# for manual
BuildRequires:	openjade
BuildRequires:	docbook-style-dsssl
BuildRequires:	docbook-dtd42-xml
BuildRequires:	docbook-dtd31-sgml
BuildRequires:	lynx
BuildRequires:	docbook-dtds


Requires(post): rpm-helper
Requires(preun): rpm-helper

#Provides:	webproxy

%description
Privoxy is a web proxy with advanced filtering capabilities for protecting
privacy, filtering web page content, managing cookies, controlling access, and
removing ads, banners, pop-ups and other obnoxious Internet Junk. Privoxy has a
very flexible configuration and can be customized to suit individual needs and
tastes. Privoxy has application for both stand-alone systems and multi-user
networks.

Privoxy was previously called Internet Junkbuster.

To configure privoxy, go to http://config.privoxy.org/

Privoxy proxy is running on port 8118

%files
%license LICENSE 
%doc AUTHORS ChangeLog README
%doc doc/webserver
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%attr(0755,root,root)%{_sbindir}/%{name}
%attr(0644,root,root) %{_unitdir}/%{name}.service
%dir %{privoxyconf}
%config(noreplace) %{privoxyconf}/config
%config            %{privoxyconf}/default.action
%config(noreplace) %{privoxyconf}/default.filter
%config(noreplace) %{privoxyconf}/templates
%config(noreplace) %{privoxyconf}/match-all.action
%config(noreplace) %{privoxyconf}/trust
%config(noreplace) %{privoxyconf}/user.action
#config(noreplace) %{privoxyconf}/user.filter
%config(noreplace) %{privoxyconf}/regression-tests.action
%config            %{privoxyconf}/standard.action
%dir %{_localstatedir}/log/%{name}
%{_mandir}/man8/%{name}.*

# owned by 'daemon' user
%attr (0711,daemon,daemon) %{_localstatedir}/log/%{name}
%defattr(664,daemon,daemon,755)

#--------------------------------------------------------------------------------

%prep
%autosetup -p1 -n %{name}-%{version}-%{reltype}

%build
autoreconf -fiv
%serverbuild
%configure \
	--with-user=daemon \
	--with-group=daemon \
	%{nil}
%make_build
#make dok
#make config-file

%install
# binary
install -dm 0755 %{buildroot}%{_sbindir}/
install -pm 0755 privoxy %{buildroot}%{_sbindir}/%{name}

# manpage
install -dm 0755 %{buildroot}%{_mandir}/man8
install -pm 0644 %{name}.8 %{buildroot}%{_mandir}/man8/%{name}.8

# various config files
#   filters
install -dm 0755 %{buildroot}%{privoxyconf}/
install -pm 0644 {config,*.action,default.filter,trust} %{buildroot}%{privoxyconf}/
#   templates
install -dm 0755 %{buildroot}%{privoxyconf}/templates/
install -pm 0644 templates/* %{buildroot}%{privoxyconf}/templates
#   logrotare
install -dm 0755 %{buildroot}%{_sysconfdir}/logrotate.d/
install -pm 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
#   service
install -dm 0755 %{buildroot}%{_unitdir}/
install -pm 0644 %{SOURCE4} %{buildroot}%{_unitdir}/%{name}.service
#   log
install -dm 711 %{buildroot}%{_localstatedir}/log/%{name}/

# verify all file locations, etc. in the config file
# don't start with ^ or commented lines are not replaced
sed -i \
	-e 's|^confdir.*|confdir %{privoxyconf}|g' \
	-e 's|^logdir.*|logdir %{_localstatedir}/log/%{name}|g' \
	%{buildroot}%{privoxyconf}/config

#   user.filter is missing
#touch %{buildroot}%{_sysconfdir}/%{name}/user.filter
sed -i \
	-e 's|^filterfile user.filter.*|#filterfile user.filter&|g' \
	%{buildroot}%{privoxyconf}/config

# create compatibility symlink
ln -s match-all.action %{buildroot}/%{privoxyconf}/standard.action

# remove backup files
rm -f doc/privoxy/webserver/user-manual/*.bak

%pre
#_pre_useradd %{name} %{privoxyconf} /sbin/nologin
#_pre_groupadd %{name} %{name}

%post
%_post_service %{name}

%preun
%_preun_service %{name}

%postun
#_postun_userdel %{name}
#_postun_groupdel %{name}

