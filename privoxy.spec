%define privoxyconf %{_sysconfdir}/%{name}

%define reltype beta

Summary:	Privacy enhancing HTTP proxy
Name:		privoxy
Version:	3.0.13
Release:	%mkrel 1
License:	GPL
Group:		Networking/Other
URL:		http://www.privoxy.org/
Source0:	http://prdownloads.sf.net/ijbswa/%{name}-%{version}-%{reltype}-src.tar.gz
Source1:	http://prdownloads.sf.net/ijbswa/%{name}-%{version}-%{reltype}-src.tar.gz.asc
# use daemon user to run privoxy
Patch1:		privoxy-2.9.13-daemon.patch
# (fc) 3.0.3-7mdk add support for parallel initscript
Patch4:		privoxy-3.0.3-parallel.patch
# (fc) 3.0.6-2mdv fix Google Reader filter 
Patch7:		privoxy-3.0.12-fixreader.patch
# (fc) 3.0.12-1mdv fix doc building
Patch8:		privoxy-3.0.12-fix-typo-in-xml.patch
Requires(post): rpm-helper
Requires(preun): rpm-helper
Obsoletes:	junkbuster
Provides:	junkbuster = %{version}-%{release}
Provides:	webproxy
BuildRequires:	docbook-style-dsssl
BuildRequires:	docbook-dtd31-sgml
BuildRequires:	lynx
BuildRequires:	man
BuildRequires:	pcre-devel
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

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
%patch1 -p1 -b .daemon
%patch4 -p1 -b .parallel
%patch7 -p1 -b .fixreader
%patch8 -p1 -b .fixdoc

# manpage should be in section 8
sed -i -e 's/^\(\.TH "PRIVOXY" \)"1"/\1"8"/g' privoxy.1 

#needed for build
autoreconf

%build

%serverbuild
%configure2_5x --with-user=daemon --with-group=daemon
%make
make redhat-dok

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_sbindir} \
         %{buildroot}%{_mandir}/man8 \
         %{buildroot}/var/log/privoxy \
         %{buildroot}%{privoxyconf}/templates \
         %{buildroot}%{_sysconfdir}/logrotate.d \
         %{buildroot}%{_initrddir}

install -m 755 privoxy %{buildroot}%{_sbindir}/privoxy
install -m 644 privoxy.1 %{buildroot}%{_mandir}/man8/privoxy.8

# Install various config files
for i in *.action default.filter trust; do
	install -m 644 $i %{buildroot}%{privoxyconf}/
done
for i in templates/*; do
	install -m 644 $i %{buildroot}%{privoxyconf}/templates/
done
install -m 644 privoxy.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
install -m 755 privoxy.init %{buildroot}%{_initrddir}/%{name}

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
%_post_service privoxy

%preun
%_preun_service privoxy


%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%doc AUTHORS ChangeLog README  
%doc doc/webserver
%attr (0700,daemon,daemon) /var/log/privoxy
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%{_sbindir}/*
%{_mandir}/man8/*
%config %{_initrddir}/%{name}

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
