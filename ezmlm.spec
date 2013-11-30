%define apacheuser    apache
%define apachegroup   apache
%define debug_package %{nil}
%define basedir       %{_datadir}/toaster
%define ezroot        /usr

Name: 		ezmlm
Summary: 	Qmail Easy Mailing List Manager + IDX patches with mysql support
%define ezver   0.53
Version: 	%{ezver}.324
Release: 	0%{?dist}
%define idxver  0.40
Group: 		Utilities/System
License: 	GNU
URL: 		http://cr.yp.to/ezmlm.html
Source0:	http://cr.yp.to/software/ezmlm-%{ezver}.tar.gz
Source1:	http://www.untroubled.org/ezmlm/archive/0.40/ezmlm-idx-0.40.tar.gz
Source2: 	http://www.untroubled.org/ezmlm/archive/ezman/ezman-0.32.html.tar.gz
BuildRequires:  mysql-devel >= 5.0.22
Requires:       mysql >= 5.0.22
Obsoletes: 	ezmlm-idx
Obsoletes: 	ezmlm-toaster
Obsoletes: 	ezmlm-toaster-doc
Obsoletes: 	ezmlm-cgi-toaster
Conflicts: 	ezmlm-idx-std, ezmlm-idx-pgsql, ezmlm-idx-mysql
BuildRoot:      %{_topdir}/BUILDROOT/%{name}-%{version}-%{release}.%{_arch}

#-------------------------------------------------------------------------------
%description
#-------------------------------------------------------------------------------
ezmlm lets users set up their own mailing lists within qmail's address
hierarchy. A user, Joe, types

   ezmlm-make ~/SOS ~/.qmail-sos joe-sos isp.net

and instantly has a functioning mailing list, joe-sos@isp.net, with all
relevant information stored in a new ~/SOS directory.

ezmlm sets  up joe-sos-subscribe  and joe-sos-unsubscribe for automatic
processing of subscription and  unsubscription requests. Any message to
joe-sos-subscribe  will work;  Joe  doesn't  have to explain any tricky
command formats. ezmlm  will  send  back  instructions  if a subscriber
sends a message to joe-sos-request or joe-sos-help.

ezmlm  automatically  archives new messages. Messages are labelled with
sequence numbers; a subscriber can fetch message 123 by sending mail to
joe-sos-get.123.  The archive  format supports  fast message  retrieval
even when there are thousands of messages.

ezmlm  takes  advantage  of  qmail's  VERPs  to  reliably determine the
recipient address and message number for every incoming bounce message.
It waits ten days  and  then  sends  the  subscriber  a list of message
numbers that bounced.  If that warning bounces, ezmlm sends a probe; if
the probe bounces, ezmlm  automatically removes the subscriber from the
mailing list.

ezmlm is easy for users to control. Joe can edit ~/SOS/text/* to change
any of the administrative  messages  sent to subscribers. He can remove
~/SOS/public and ~/SOS/archived to  disable  automatic subscription and
archiving. He can put  his  own  address  into ~/SOS/editor to set up a
moderated mailing list.  He  can edit ~/SOS/{headeradd,headerremove} to
control  outgoing  headers.  ezmlm  has  several  utilities to manually
inspect and manage mailing lists.

ezmlm uses Delivered-To  to  stop  forwarding  loops,  Mailing-List  to
protect other mailing  lists against false  subscription  requests, and
real  cryptographic  cookies  to  protect  normal  users  against false
subscription  requests.  ezmlm   can   also  be  used  for  a  sublist,
redistributing messages from another list.

ezmlm is reliable, even in the face  of system crashes.  It writes each
new subscription and each new message safely to disk  before it reports
success to qmail.

ezmlm doesn't mind huge mailing lists.  Lists  don't  even  have to fit
into memory.  ezmlm  hashes   the  subscription  list  into  a  set  of
independent files  so that it can handle subscription requests quickly.
ezmlm uses qmail for blazingly fast parallel SMTP deliveries.

The IDX  patches  add:  Indexing,  (Remote)  Moderation,  digest,  make
patches, multi-language, MIME, global interface, MySQL database support.

#-------------------------------------------------------------------------------
%package -n     ezmlm-cgi
#-------------------------------------------------------------------------------
Summary:	Ezmlm cgi-bin
Group:		Networking/Other
Requires:	%{name} >= %{version}-%{release}
Requires:	control-panel >= 0.2
Requires:	httpd >= 2.0.40

#-------------------------------------------------------------------------------
%description	-n ezmlm-cgi
#-------------------------------------------------------------------------------
Ezmlm cgi to query via apache mail archives.2

#-------------------------------------------------------------------------------
%prep
#-------------------------------------------------------------------------------
%setup -q -T -b 0 -n ezmlm-%{ezver}
%setup -D -T -a 1 -n ezmlm-%{ezver}

mv -f ezmlm-idx-%{idxver}/* .
patch -s < idx.patch

#-------------------------------------------------------------------------------
%build 
#-------------------------------------------------------------------------------
RC=%{_sysconfdir}/ezmlm/ezmlmrc

sed -e 's{^#define TXT_ETC_EZMLMRC \"/etc/ezmlmrc\"{#define TXT_ETC_EZMLMRC \"$RC\"{' idx.h > idx.h.tmp

mv idx.h.tmp idx.h

# Fix lib include in Makefile
#-------------------------------------------------------------------------------
%ifarch x86_64
  %{__perl} -pi -e 's|`head -1 conf-sqlld`|-L/usr/lib64/mysql -lmysqlclient -lnsl -lm -lz|g' Makefile
%else
  %{__perl} -pi -e 's|`head -1 conf-sqlld`|-L/usr/lib/mysql -lmysqlclient -lnsl -lm -lz|g' Makefile
%endif

echo "gcc %{optflags}" > conf-cc
echo "gcc %{optflags}" > conf-ld
echo %{ezroot}/bin     > conf-bin
echo %{ezroot}/man     > conf-man

# GLIBC fix
#-------------------------------------------------------------------------------
echo "Fixing errno.h for new GLIBC"
echo "#include <errno.h>" >> error.h

make 
make it install

#-------------------------------------------------------------------------------
%install
#-------------------------------------------------------------------------------
rm -rf %{buildroot}
mkdir -p %{buildroot}/%{ezroot}/bin
mkdir -p %{buildroot}/%{ezroot}/man
mkdir -p %{buildroot}/%{_sysconfdir}/ezmlm
mkdir -p %{buildroot}%{basedir}/cgi-bin

sed '/cat/d' MAN > MAN.tmp
mv MAN.tmp MAN

./install %{buildroot}/%{ezroot}/bin < BIN
./install %{buildroot}/%{ezroot}/man < MAN

# Fix css
#-------------------------------------------------------------------------------
%{__perl} -pi -e 's|/ezcgi.css|/scripts/styles.css|g' $RPM_BUILD_DIR/ezmlm-%{ezver}/ezcgirc

cp $RPM_BUILD_DIR/ezmlm-%{ezver}/ezmlmrc.en_US \
   %{buildroot}/%{_sysconfdir}/ezmlm/ezmlmrc
cp $RPM_BUILD_DIR/ezmlm-%{ezver}/ezmlmrc.en_US \
   %{buildroot}/%{_sysconfdir}/ezmlm/ezmlmrc.dist
cp $RPM_BUILD_DIR/ezmlm-%{ezver}/ezmlmrc.it \
   %{buildroot}/%{_sysconfdir}/ezmlm/
cp $RPM_BUILD_DIR/ezmlm-%{ezver}/ezmlmrc.cs \
   %{buildroot}/%{_sysconfdir}/ezmlm/
cp $RPM_BUILD_DIR/ezmlm-%{ezver}/ezmlmrc.da \
   %{buildroot}/%{_sysconfdir}/ezmlm/
cp $RPM_BUILD_DIR/ezmlm-%{ezver}/ezmlmrc.de \
   %{buildroot}/%{_sysconfdir}/ezmlm/
cp $RPM_BUILD_DIR/ezmlm-%{ezver}/ezmlmrc.es \
   %{buildroot}/%{_sysconfdir}/ezmlm/
cp $RPM_BUILD_DIR/ezmlm-%{ezver}/ezmlmrc.fr \
   %{buildroot}/%{_sysconfdir}/ezmlm/
cp $RPM_BUILD_DIR/ezmlm-%{ezver}/ezmlmrc.ru \
   %{buildroot}/%{_sysconfdir}/ezmlm/
cp $RPM_BUILD_DIR/ezmlm-%{ezver}/ezmlm-cgi \
   %{buildroot}/%{basedir}/cgi-bin/ezmlm.cgi
cp $RPM_BUILD_DIR/ezmlm-%{ezver}/ezcgirc \
   %{buildroot}/%{_sysconfdir}/ezmlm/ezcgirc
cp $RPM_BUILD_DIR/ezmlm-%{ezver}/ezcgirc \
   %{buildroot}/%{_sysconfdir}/ezmlm/ezcgirc.dist

tar xvzf %{SOURCE2}

#-------------------------------------------------------------------------------
%clean
#-------------------------------------------------------------------------------
rm -rf %{buildroot}

#-------------------------------------------------------------------------------
%files -n ezmlm-cgi
#-------------------------------------------------------------------------------
%defattr (-,root,root)
%attr(0755,root,root) %dir  %{basedir}/cgi-bin
%config(noreplace)          %{_sysconfdir}/ezmlm/ezcgirc
%config                     %{_sysconfdir}/ezmlm/ezcgirc.dist
%attr(6755,vpopmail,vchkpw) %{basedir}/cgi-bin/ezmlm.cgi

#-------------------------------------------------------------------------------
%files
#-------------------------------------------------------------------------------
%defattr(-,root,root)
%config(noreplace) %{_sysconfdir}/ezmlm/ezmlmrc
%config %{_sysconfdir}/ezmlm/ezmlmrc.dist
%config %{_sysconfdir}/ezmlm/ezmlmrc.it
%config %{_sysconfdir}/ezmlm/ezmlmrc.cs
%config %{_sysconfdir}/ezmlm/ezmlmrc.da
%config %{_sysconfdir}/ezmlm/ezmlmrc.de
%config %{_sysconfdir}/ezmlm/ezmlmrc.es
%config %{_sysconfdir}/ezmlm/ezmlmrc.fr
%config %{_sysconfdir}/ezmlm/ezmlmrc.ru
%{ezroot}/bin/*

# docs
%doc BLURB CHANGES* FAQ.idx INSTAL*  README*
%doc THANKS TODO UPGRADE.idx VERSION
%doc DOWNGRADE.idx ezmlmrc ezmlmrc.[a-zA-Z]*  ezman*
%doc qmail-*.tar.gz
%{ezroot}/man/*/*

#-------------------------------------------------------------------------------
%changelog
#-------------------------------------------------------------------------------
* Fri Nov 15 2013 Eric Shubert <eric@datamatters.us> 0.53-324.qt
- Migrated to github
- Removed -toaster designation
- Added CentOS 6 support
- Removed unsupported cruft
* Fri Jun 12 2009 Jake Vickers <jake@qmailtoaster.com> 0.53.324-1.3.6
- Added Fedora 11 support
- Added Fedora 11 x86_64 support
* Wed Jun 10 2009 Jake Vickers <jake@qmailtoaster.com> 0.53.324-1.3.6
- Added Mandriva 2009 support
* Wed Apr 22 2009 Jake Vickers <jake@qmailtoaster.com> 0.53.324-1.3.5
- Added Fedora 9 x86_64 and Fedora 10 x86_64 support
* Fri Feb 13 2009 Jake Vickers <jake@qmailtoaster.com> 0.53.324-1.3.4
- Added Suse 11.1 support
* Mon Feb 09 2009 Jake Vickers <jake@qmailtoaster.com> 0.53.324-1.3.4
- Added Fedora 9 and 10 support
* Sat Apr 17 2007 Nick Hemmesch <nick@ndhsoft.com> 0.53.324-1.3.3
- Add CentOS 5 i386 support
- Add CentOS 5 x86_64 support
* Wed Nov 01 2006 Erik A. Espinoza <espinoza@forcenetworks.com> 0.53.324-1.3.2
- Added Fedora Core 6 support
* Mon Jun 05 2006 Nick Hemmesch <nick@ndhsoft.com> 0.53.324-1.3.1
- Add SuSE 10.1 support
* Sat May 13 2006 Nick Hemmesch <nick@ndhsoft.com> 0.53.324-1.2.11
- Add Fedora Core 5 support
* Sun Nov 20 2005 Nick Hemmesch <nick@ndhsoft.com> 0.53.324-1.2.10
- Add SuSE 10.0 and Mandriva 2006.0 support
* Sat Oct 15 2005 Nick Hemmesch <nick@ndhsoft.com> 0.53.324-1.2.9
- Add Fedora Core 4 x86_64 support
* Sat Oct 01 2005 Nick Hemmesch <nick@ndhsoft.com> 0.53.324-1.2.8
- Add CentOS 4 x86_64 support
* Mon Sep 26 2005 Nick Hemmesch <nick@ndhsoft.com> 0.53.324-1.2.7
- Fix compiled definition for Mandrake 10.2
* Fri Jul 01 2005 Nick Hemmesch <nick@ndhsoft.com> 0.53.324-1.2.6
- Add Fedora Core 4 support
* Fri Jun 03 2005 Torbjorn Turpeinen <tobbe@nyvalls.se> 0.5-1.2.5
- Gnu/Linux Mandrake 10.0,10.1,10.2 support
* Fri May 27 2005 Nick Hemmesch <nick@ndhsoft.com> 0.53.324-1.2.4
- Remove doc package
* Sun Feb 27 2005 Nick Hemmesch <nick@ndhsoft.com> 0.53.324-1.2.3
- Add Fedora Core 3 support
- Add CentOS 4 support
* Thu Jun 03 2004 Nick Hemmesch <nick@ndhsoft.com> 0.53.324-1.2.2
- Add Fedora Core 2 support
* Mon Jan 12 2004 Nick Hemmesch <nick@ndhsoft.com> 0.53.324-1.0.9
- Trustix fix - dep apache 2.0.40 instead of httpd by Christian Dietrich
* Mon Dec 29 2003 Nick Hemmesch <nick@ndhsoft.com> 0.53.324-1.0.8
- Add Fedora Core 1 support
* Sun Nov 23 2003 Nick Hemmesch <nick@ndhsoft.com> 0.53.324-1.0.7
- Add Trustix 2.0 support
* Thu May 15 2003 Miguel Beccari <miguel.beccari@clikka.com> 0.53.324-1.0.6
- Red Hat Linux 9.0 support (nick@ndhsoft.com)
- Gnu/Linux Mandrake 9.2 support
- Clean-ups on SPEC: compilation banner, better gcc detects
- Detect gcc-3.2.3
* Mon Mar 31 2003 Miguel Beccari <miguel.beccari@clikka.com> 0.53.324-1.0.5
- Conectiva Linux 7.0 support
* Sun Feb 15 2003 Nick Hemmesch <nick@ndhsoft.com> 0.53.324-1.0.4
- Support for Red Hat 8.0
* Wed Feb 05 2003 Miguel Beccari <miguel.beccari@clikka.com> 0.53.324-1.0.3
- Support for Red Hat 8.0 thanks to Andrew.J.Kay
* Sat Feb 01 2003 Miguel Beccari <miguel.beccari@clikka.com> 0.53.324-1.0.2
- Redo Macros to prepare supporting larger RPM OS.
  We could be able to compile (and use) packages under every RPM based
  distribution: we just need to write right requirements.
* Sat Jan 25 2003 Miguel Beccari <miguel.beccari@clikka.com> 0.53.324-1.0.1
- Added MDK 9.1 support
- Try to use gcc-3.2.1
- Added very little patch to compile with newest GLIBC
- Support dor new RPM-4.0.4
* Sat Oct 05 2002 Miguel Beccari <miguel.beccari@clikka.com> 0.53.324-0.9.2
- Soft clean-ups
* Sun Sep 29 2002 Miguel Beccari <miguel.beccari@clikka.com> 0.53.324-0.8.1
- RPM macros to detect Mandrake, RedHat, Trustix are OK again. They are
  very basic but they should work.
* Fri Sep 27 2002 Miguel Beccari <miguel.beccari@clikka.com> 0.8.0.53.324-1
- Rebuilded under 0.8 tree.
- Important comments translated from Italian to English.
- Written rpm rebuilds instruction at the top of the file (in english).
* Sun Sep 22 2002 Miguel Beccari <miguel.beccari@clikka.com> 0.7.0.53.324-4
- Cleans and patches on ezmlm.cgi: we use toaster css
* Fri Sep 06 2002 Miguel Beccari <miguel.beccari@clikka.com> 0.7.0.53.324-3
- Default language is English (no more Italian)
- Added localized configuration (was missed)
- Changed dependencing from apache-conf-toaster in toaster-control-panel
* Thu Aug 29 2002 Miguel Beccari <miguel.beccari@clikka.com> 0.7.0.53.324-2
- Deleted Mandrake Release Autodetection (creates problems)
* Fri Aug 16 2002 Miguel Beccari <miguel.beccari@clikka.com> 0.7.0.53.324-1
- New version: 0.7 toaster.
- Installation directly depends on apache-conf-toaster (that provides httpd
  configurations for all web packages)
- Better macros to detect Mandrake Release
* Thu Aug 13 2002 Miguel Beccari <miguel.beccari@clikka.com> 0.6.0.53.324-1
- New version: 0.6 toaster
- We have ezmlm.cgi (it was missed in previous packages)
- Configuration files are in /etc/ezmlm (no more in /etc)
* Mon Aug 12 2002 Miguel Beccari <miguel.beccari@clikka.com> 0.5.0.53.324-1
- New version: 0.5 toaster
- Doc package is standalone (someone does not ask for man pages)
- Checks for gcc-3.2 (default compiler from now)
* Tue Aug 08 2002 Miguel Beccari <miguel.beccari@clikka.com> 0.4.0.53.324-1
- Rebuild against 0.4 toaster
* Thu Aug 06 2002 Miguel Beccari <miguel.beccari@clikka.com> 0.3.0.53.324-3
- Better dependencies for RedHat
* Thu Jul 30 2002 Miguel Beccari <miguel.beccari@clikka.com> 0.3.0.53.324-2
- Now packages have got 'no sex': you can rebuild them with command line
  flags for specifics targets that are: RedHat, Trustix, and of course
  Mandrake (that is default)
- Soft clean-ups to SPEC file.
* Sun Jul 28 2002 Miguel Beccari <miguel.beccari@clikka.com> 0.3.0.53.324.1mdk
- toaster v. 0.3: now it is possible upgrading safely because of 'pversion'
  that is package version and 'version' that is toaster version
* Thu Jul 25 2002 Miguel Beccari <miguel.beccari@clikka.com> 0.2-0.53.324.1mdk
- toaster v. 0.2
* Thu Jul 18 2002 Miguel Beccari <miguel.beccari@clikka.com> 0.1-0.53.324.3mdk
- Added tests for gcc-3.1.1
- Added toaster version (we will need to mantain it too): is vtoaster 0.1
  soft links.
* Thu Jul 11 2002 Miguel Beccari <mighi@clikka.com> 0.53.324-2mdk
- Renamed the package in toster (we are building a toaster series
  of packages)
* Fri Jul 05 2002 Miguel Beccari <mighi@clikka.com> 0.53.324-1mdk
- First RPM package.
