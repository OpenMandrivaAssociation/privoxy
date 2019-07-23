%define privoxyconf %{_sysconfdir}/%{name}
%define reltype stable

Summary:	Privacy enhancing HTTP proxy
Name:		privoxy
Version:	3.0.28
Release:	1
License:	GPLv2+
Group:		Networking/Other
URL:		http://www.privoxy.org/

Source0:	http://prdownloads.sf.net/ijbswa/%{name}-%{version}-%{reltype}-src.tar.gz
Source1:	http://prdownloads.sf.net/ijbswa/%{name}-%{version}-%{reltype}-src.tar.gz.asc
Source2:	privoxy.logrotate
Source4:	%{name}.service
Patch0:		privoxy-3.0.23-mga-mdv-missing-user.filter.patch

BuildRequires:	docbook-style-dsssl
BuildRequires:	docbook-dtd42-xml
BuildRequires:	docbook-dtd31-sgml
BuildRequires:	lynx
BuildRequires:	man
BuildRequires:	pkgconfig(libpcreposix)
BuildRequires:	zlib-devel

Requires(post): rpm-helper
Requires(preun): rpm-helper

#Obsoletes:	junkbuster
#Provides:	junkbuster = %{version}-%{release}
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
%doc AUTHORS ChangeLog README
%doc doc/webserver
%dir %{_localstatedir}/log/%{name}
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%{_sbindir}/*
%{_mandir}/man8/*
# owned by 'daemon' user
%defattr(664,daemon,daemon,755)
%dir %{privoxyconf}
%config(noreplace) %{privoxyconf}/config
%config(noreplace) %{privoxyconf}/default.action
%config(noreplace) %{privoxyconf}/default.filter
%config(noreplace) %{privoxyconf}/templates
%config(noreplace) %{privoxyconf}/match-all.action
%config(noreplace) %{privoxyconf}/trust
%config(noreplace) %{privoxyconf}/user.action
%config(noreplace) %{privoxyconf}/regression-tests.action
%{privoxyconf}/standard.action
%{_unitdir}/%{name}.service

#--------------------------------------------------------------------------------

%prep
%setup -q -n %{name}-%{version}-%{reltype}
%apply_patches

# privoxy.missing.user.filter.patch
#% patch0 -p1

# manpage should be in section 8
sed -i -e 's/^\(\.TH "PRIVOXY" \)"1"/\1"8"/g' privoxy.1

#fix permissions
find . -type f -perm 0640 -exec chmod 0644 {} \;

%build
autoreconf
%serverbuild
%configure \
	--with-user=daemon \
	--with-group=daemon \
	%{nil}
%make

%install
# binary
install -dm 0755 %{buildroot}%{_sbindir}/
install -pm 0755 privoxy %{buildroot}%{_sbindir}/%{name}

# manpage
install -dm 0755 %{buildroot}%{_mandir}/man8
install -pm 0644 privoxy.1 %{buildroot}%{_mandir}/man8/%{name}.8

# various config files
#   filters
install -dm 0755 %{buildroot}%{privoxyconf}/
for i in *.action default.filter trust; do
	install -pm 0644 $i %{buildroot}%{privoxyconf}/
done
#   templates
install -dm 0755 %{buildroot}%{privoxyconf}/templates/
for i in templates/*; do
	install -pm 0644 $i %{buildroot}%{privoxyconf}/templates/
done
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
sed -e 's!^confdir.*!confdir /etc/privoxy!g' \
    -e 's!^logdir.*!logdir /var/log/privoxy!g' \
    < config  > %{buildroot}%{privoxyconf}/config

#remove backup files
rm -f doc/privoxy/webserver/user-manual/*.bak

# create compatibility symlink
ln -s match-all.action %{buildroot}/%{privoxyconf}/standard.action

%triggerin -- msec < 0.17
for i in 0 1 2 3 4 5; do
  permfile="%{_sysconfdir}/security/msec/perm.$i"
  if grep -q '^/var/log/privoxy' $permfile; then
    perl -pi -e 's|^/var/log/privoxy\s.*|/var/log/prixovy\t\t\t\tdaemon.daemon\t700|' $permfile
  else
    echo -e "/var/log/prixovy\t\t\t\tdaemon.daemon\t700" >> $permfile
  fi
done

%post
%_post_service %{name}

%preun
%_preun_service %{name}

