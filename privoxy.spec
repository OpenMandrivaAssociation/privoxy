%define privoxyconf %{_sysconfdir}/%{name}

%define reltype stable

Summary:	Privacy enhancing HTTP proxy
Name:		privoxy
Version:	3.0.19
Release:	%mkrel 2
License:	GPLv2
Group:		Networking/Other
URL:		http://www.privoxy.org/
Source0:	http://prdownloads.sf.net/ijbswa/%{name}-%{version}-%{reltype}-src.tar.gz
Source1:	http://prdownloads.sf.net/ijbswa/%{name}-%{version}-%{reltype}-src.tar.gz.asc
Source2:	privoxy.logrotate
Source3:	privoxy.init
Patch0:		privoxy.missing.user.filter.patch
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
BuildRequires:	pcre-devel
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

%build
autoreconf -fi
%serverbuild
%configure2_5x --with-user=daemon --with-group=daemon
%make

%install
%__rm -rf %{buildroot}
%__mkdir_p %{buildroot}%{_sbindir} \
           %{buildroot}%{_mandir}/man8 \
           %{buildroot}/var/log/privoxy \
           %{buildroot}%{privoxyconf}/templates \
           %{buildroot}%{_sysconfdir}/logrotate.d \
           %{buildroot}%{_initrddir}

%__install -m 755 privoxy %{buildroot}%{_sbindir}/privoxy
%__install -m 644 privoxy.1 %{buildroot}%{_mandir}/man8/privoxy.8

# Install various config files
for i in *.action default.filter trust; do
	%__install -m 644 $i %{buildroot}%{privoxyconf}/
done
for i in templates/*; do
	%__install -m 644 $i %{buildroot}%{privoxyconf}/templates/
done
%__install -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
%__install -m 755 %{SOURCE3} %{buildroot}%{_initrddir}/%{name}

# verify all file locations, etc. in the config file
# don't start with ^ or commented lines are not replaced
%__sed -e 's!^confdir.*!confdir /etc/privoxy!g' \
    -e 's!^logdir.*!logdir /var/log/privoxy!g' \
    < config  > %{buildroot}%{privoxyconf}/config

#remove backup files
%__rm -f doc/privoxy/webserver/user-manual/*.bak

# create compatibility symlink
%__ln_s match-all.action %{buildroot}/%{privoxyconf}/standard.action

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
%__rm -rf %{buildroot}

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


%changelog
* Sat Feb 11 2012 Oden Eriksson <oeriksson@mandriva.com> 3.0.19-2mdv2012.0
+ Revision: 773025
- relink against libpcre.so.1

* Fri Feb 03 2012 Andrey Bondrov <abondrov@mandriva.org> 3.0.19-1
+ Revision: 770811
- New version 3.0.19

* Tue Aug 09 2011 Alexander Barakin <abarakin@mandriva.org> 3.0.17-2
+ Revision: 693760
- missing user.filter file
  see https://qa.mandriva.com/show_bug.cgi?id=63573

* Tue May 17 2011 Funda Wang <fwang@mandriva.org> 3.0.17-1
+ Revision: 675884
- use autoreconf
- br zlib
- update to new version 3.0.17

* Tue Dec 07 2010 Oden Eriksson <oeriksson@mandriva.com> 3.0.16-2mdv2011.0
+ Revision: 614612
- the mass rebuild of 2010.1 packages

* Mon May 10 2010 Frederic Crozat <fcrozat@mandriva.com> 3.0.16-1mdv2010.1
+ Revision: 544312
- Release 3.0.16 (stable)

* Wed Oct 21 2009 Frederic Crozat <fcrozat@mandriva.com> 3.0.15-1mdv2010.0
+ Revision: 458511
- Fix buildrequires
- Release 3.0.15
- Replace patches 1 & 4 by source 1 & 2
- Fix buildrequires

* Mon Jul 27 2009 Frederic Crozat <fcrozat@mandriva.com> 3.0.14-1mdv2010.0
+ Revision: 400620
- Release 3.0.14 (beta)
- remove patches 7 (no longer needed) 8, (merged upstream)

* Mon Jun 15 2009 Frederic Crozat <fcrozat@mandriva.com> 3.0.13-1mdv2010.0
+ Revision: 386048
- Release 3.0.13 (beta), with IPv6 support
- do no package backup doc files (Mdv bug #37689)

* Thu Apr 16 2009 Frederic Crozat <fcrozat@mandriva.com> 3.0.12-2mdv2009.1
+ Revision: 367771
- Fix upgrade from previous release if /etc/privoxy/config was modified

* Mon Mar 23 2009 Frederic Crozat <fcrozat@mandriva.com> 3.0.12-1mdv2009.1
+ Revision: 360616
- Release 3.0.12
- Regenerate patch7
- Patch8: fix typo in xml doc

* Mon Mar 16 2009 Frederic Crozat <fcrozat@mandriva.com> 3.0.11-1mdv2009.1
+ Revision: 355925
- Release 3.0.11

* Thu Aug 21 2008 Frederic Crozat <fcrozat@mandriva.com> 3.0.10-1mdv2009.0
+ Revision: 274675
- add missing signature file
- Release 3.0.10
- Remove patch5 (obsolete)

* Fri Aug 01 2008 Thierry Vignaud <tv@mandriva.org> 3.0.8-5mdv2009.0
+ Revision: 259295
- rebuild

* Thu Jul 24 2008 Thierry Vignaud <tv@mandriva.org> 3.0.8-4mdv2009.0
+ Revision: 247222
- rebuild

* Mon Feb 18 2008 Oden Eriksson <oeriksson@mandriva.com> 3.0.8-2mdv2008.1
+ Revision: 171431
- add a virtal provides of webproxy

* Mon Jan 21 2008 Frederic Crozat <fcrozat@mandriva.com> 3.0.8-1mdv2008.1
+ Revision: 155687
- Release 3.0.8
- Remove patches 0 (replace by sed magic), 6 (merged upstream)

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Tue Sep 18 2007 Frederic Crozat <fcrozat@mandriva.com> 3.0.6-2mdv2008.0
+ Revision: 89689
- Patch6 (CVS): many filter fixes from CVS
- Patch7: fix Google Reader filter


* Wed Mar 07 2007 Frederic Crozat <fcrozat@mandriva.com> 3.0.6-1mdv2007.1
+ Revision: 134608
- Release 3.0.6
- Bunzip patches
- Remove patches 2, 3 (merged upstream)
- Patch5: fix documentation generation
- Regenerate patch1
- Import privoxy

* Thu May 04 2006 Frederic Crozat <fcrozat@mandriva.com> 3.0.3-11mdk
- Update patch2 to not break Google Finance either

* Thu Feb 09 2006 Frederic Crozat <fcrozat@mandriva.com> 3.0.3-10mdk
- Update patch2 to not break gmail by default

* Mon Jan 09 2006 Olivier Blin <oblin@mandriva.com> 3.0.3-9mdk
- don't forget the LSB patch

* Mon Jan 09 2006 Olivier Blin <oblin@mandriva.com> 3.0.3-8mdk
- convert parallel init to LSB

* Tue Jan 03 2006 Frederic Crozat <fcrozat@mandriva.com> 3.0.3-7mdk
- Fix prereq
- use mkrel
- Patch4: add support for parallel initscript

* Mon Jan 10 2005 Frederic Crozat <fcrozat@mandrakesoft.com> 3.0.3-6mdk 
- Patch3 : fix ie-exploit filter to not be triggered by Amazon

* Sat Jul 24 2004 Frederic Crozat <fcrozat@mandrakesoft.com> 3.0.3-5mdk
- Fix perms on privoxy config directory

* Thu Jul 22 2004 Frederic Crozat <fcrozat@mandrakesoft.com> 3.0.3-4mdk
- Fix default perms/owner of configuration file, otherwise privoxy won't
  be able to modify its config files from web interface.

