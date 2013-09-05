%define privoxyconf %{_sysconfdir}/%{name}
%define reltype stable

Summary:	Privacy enhancing HTTP proxy
Name:		privoxy
Version:	3.0.21
Release:	1
License:	GPLv2+
Group:		Networking/Other
URL:		http://www.privoxy.org/
Source0:	http://prdownloads.sf.net/ijbswa/%{name}-%{version}-%{reltype}-src.tar.gz
Source1:	http://prdownloads.sf.net/ijbswa/%{name}-%{version}-%{reltype}-src.tar.gz.asc
Source2:	privoxy.logrotate
Source4:	%{name}.service
Patch0:		privoxy-3.0.21-mga-mdv-missing-user.filter.patch
Requires(post): rpm-helper
Requires(preun): rpm-helper
Obsoletes:	junkbuster
Provides:	junkbuster = %{version}-%{release}
Provides:	webproxy
BuildRequires:	docbook-style-dsssl
BuildRequires:	docbook-dtd42-xml
BuildRequires:	docbook-dtd31-sgml
BuildRequires:	lynx
BuildRequires:	man
BuildRequires:	pcreposix-devel
BuildRequires:	zlib-devel

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

%prep

%setup -n %{name}-%{version}-%{reltype} -q

# manpage should be in section 8
sed -i -e 's/^\(\.TH "PRIVOXY" \)"1"/\1"8"/g' privoxy.1 

# privoxy.missing.user.filter.patch
%patch0 -p1
#needed for build
autoreconf

%build

%serverbuild
%configure2_5x --with-user=daemon --with-group=daemon
%make

%install
mkdir -p %{buildroot}%{_sbindir} \
         %{buildroot}%{_mandir}/man8 \
         %{buildroot}/var/log/privoxy \
         %{buildroot}%{privoxyconf}/templates \
         %{buildroot}%{_sysconfdir}/logrotate.d

install -m 755 privoxy %{buildroot}%{_sbindir}/privoxy
install -m 644 privoxy.1 %{buildroot}%{_mandir}/man8/privoxy.8

# Install various config files
for i in *.action default.filter trust; do
	install -m 644 $i %{buildroot}%{privoxyconf}/
done
for i in templates/*; do
	install -m 644 $i %{buildroot}%{privoxyconf}/templates/
done
install -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
install -d -m 755 %{buildroot}%{_unitdir}
install -m 644 %{SOURCE4} %{buildroot}%{_unitdir}/%{name}.service

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

%files
%doc AUTHORS ChangeLog README  
%doc doc/webserver
%attr (0700,daemon,daemon) /var/log/privoxy
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%{_sbindir}/*
%{_mandir}/man8/*

%defattr(664,daemon,daemon,755)
%dir %{privoxyconf}
%config(noreplace) %{privoxyconf}/config
%config            %{privoxyconf}/default.action
%config(noreplace) %{privoxyconf}/default.filter
%config(noreplace) %{privoxyconf}/templates
%config(noreplace) %{privoxyconf}/match-all.action
%config(noreplace) %{privoxyconf}/trust
%config(noreplace) %{privoxyconf}/user.action
%config(noreplace) %{privoxyconf}/regression-tests.action
%{privoxyconf}/standard.action
%{_unitdir}/%{name}.service
