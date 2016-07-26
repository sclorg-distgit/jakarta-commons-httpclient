%global pkg_name jakarta-commons-httpclient
%{?scl:%scl_package %{pkg_name}}
%{?maven_find_provides_and_requires}

# Copyright (c) 2000-2007, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

%global short_name httpclient

Name:           %{?scl_prefix}%{pkg_name}
Version:        3.1
Release:        15.9%{?dist}
Epoch:          1
Summary: Jakarta Commons HTTPClient implements the client side of HTTP standards
License:        ASL 2.0 and (ASL 2.0 or LGPLv2+)
Source0:        http://archive.apache.org/dist/httpcomponents/commons-httpclient/source/commons-httpclient-3.1-src.tar.gz
Source1:        http://repo.maven.apache.org/maven2/commons-httpclient/commons-httpclient/%{version}/commons-httpclient-%{version}.pom
Patch0:         %{pkg_name}-disablecryptotests.patch
# Add OSGi MANIFEST.MF bits
Patch1:         %{pkg_name}-addosgimanifest.patch
Patch2:         %{pkg_name}-encoding.patch
# CVE-2012-5783: missing connection hostname check against X.509 certificate name
# https://fisheye6.atlassian.com/changelog/httpcomponents?cs=1422573
Patch3:         %{pkg_name}-CVE-2012-5783.patch
Patch4:         %{pkg_name}-CVE-2014-3577.patch
URL:            http://jakarta.apache.org/commons/httpclient/
BuildArch:      noarch

BuildRequires:  %{?scl_prefix}javapackages-tools
BuildRequires:  %{?scl_prefix}ant
BuildRequires:  %{?scl_prefix}apache-commons-codec
BuildRequires:  %{?scl_prefix}apache-commons-logging >= 0:1.0.3
#BuildRequires:  java-javadoc
BuildRequires:  %{?scl_prefix}apache-commons-logging-javadoc
BuildRequires:  %{?scl_prefix}junit

Requires:       %{?scl_prefix}apache-commons-logging >= 0:1.0.3
Requires:       %{?scl_prefix}apache-commons-codec


%description
The Hyper-Text Transfer Protocol (HTTP) is perhaps the most significant
protocol used on the Internet today. Web services, network-enabled
appliances and the growth of network computing continue to expand the
role of the HTTP protocol beyond user-driven web browsers, and increase
the number of applications that may require HTTP support.
Although the java.net package provides basic support for accessing
resources via HTTP, it doesn't provide the full flexibility or
functionality needed by many applications. The Jakarta Commons HTTP
Client component seeks to fill this void by providing an efficient,
up-to-date, and feature-rich package implementing the client side of the
most recent HTTP standards and recommendations.
Designed for extension while providing robust support for the base HTTP
protocol, the HTTP Client component may be of interest to anyone
building HTTP-aware client applications such as web browsers, web
service clients, or systems that leverage or extend the HTTP protocol
for distributed communication.

%package        javadoc
Summary:        Javadoc for %{pkg_name}

%description    javadoc
%{summary}.

%package        demo
Summary:        Demos for %{pkg_name}
Requires:       %{name} = %{epoch}:%{version}-%{release}

%description    demo
%{summary}.

%package        manual
Summary:        Manual for %{pkg_name}
Requires:       %{name}-javadoc = %{epoch}:%{version}-%{release}

%description    manual
%{summary}.


%prep
%setup -q -n commons-httpclient-%{version}
%{?scl:scl enable %{scl} - <<"EOF"}
set -e -x
mkdir lib # duh
rm -rf docs/apidocs docs/*.patch docs/*.orig docs/*.rej

%patch0

pushd src/conf
%{__sed} -i 's/\r//' MANIFEST.MF
%patch1
popd

%patch2
%patch3 -p2
%patch4 -p1

# Use javax classes, not com.sun ones
# assume no filename contains spaces
pushd src
    for j in $(find . -name "*.java" -exec grep -l 'com\.sun\.net\.ssl' {} \;); do
        sed -e 's|com\.sun\.net\.ssl|javax.net.ssl|' $j > tempf
        cp tempf $j
    done
    rm tempf
popd
%{?scl:EOF}

%build
%{?scl:scl enable %{scl} - <<"EOF"}
set -e -x
ant \
  -Dbuild.sysclasspath=first \
  -Djavadoc.j2sdk.link=%{_javadocdir}/java \
  -Djavadoc.logging.link=%{_javadocdir}/jakarta-commons-logging \
  -Dtest.failonerror=false \
  -Dlib.dir=%{_javadir} \
  -Djavac.encoding=UTF-8 \
  dist test
%{?scl:EOF}


%install
%{?scl:scl enable %{scl} - <<"EOF"}
set -e -x
# jars
mkdir -p $RPM_BUILD_ROOT%{_javadir}
cp -p dist/commons-httpclient.jar \
  $RPM_BUILD_ROOT%{_javadir}/%{pkg_name}.jar
# compat symlink
pushd $RPM_BUILD_ROOT%{_javadir}
ln -s jakarta-commons-httpclient.jar commons-httpclient3.jar
ln -s jakarta-commons-httpclient.jar commons-httpclient.jar
popd

# javadoc
mkdir -p $RPM_BUILD_ROOT%{_javadocdir}
mv dist/docs/api $RPM_BUILD_ROOT%{_javadocdir}/%{name}

# demo
mkdir -p $RPM_BUILD_ROOT%{_datadir}/%{pkg_name}
cp -pr src/examples src/contrib $RPM_BUILD_ROOT%{_datadir}/%{pkg_name}

# manual and docs
rm -f dist/docs/{BUILDING,TESTING}.txt
ln -s %{_javadocdir}/%{name} dist/docs/apidocs

# maven POM and depmap
install -d -m 755 $RPM_BUILD_ROOT%{_mavenpomdir}
install -p -m 644 %{SOURCE1} $RPM_BUILD_ROOT%{_mavenpomdir}/JPP-%{pkg_name}.pom
%add_maven_depmap
%{?scl:EOF}

%files
%doc LICENSE NOTICE
%doc README RELEASE_NOTES
%{_javadir}/%{pkg_name}.jar
%{_javadir}/commons-httpclient3.jar
%{_javadir}/commons-httpclient.jar
%{_mavenpomdir}/JPP-%{pkg_name}.pom
%{_mavendepmapfragdir}/%{pkg_name}

%files javadoc
%doc LICENSE NOTICE
%doc %{_javadocdir}/%{name}

%files demo
%{_datadir}/%{pkg_name}

%files manual
%doc dist/docs/*


%changelog
* Tue Aug 12 2014 Michal Srb <msrb@redhat.com> - 1:3.1-15.9
- Fix MITM security vulnerability
- Resolves: CVE-2014-3577

* Mon Jun  2 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1:3.1-15.8
- Fix dangling symlink

* Mon May 26 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1:3.1-15.7
- Mass rebuild 2014-05-26

* Wed Feb 19 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1:3.1-15.6
- Mass rebuild 2014-02-19

* Tue Feb 18 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1:3.1-15.5
- Mass rebuild 2014-02-18

* Tue Feb 18 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1:3.1-15.4
- Remove requires on java

* Fri Feb 14 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1:3.1-15.3
- SCL-ize requires and build-requires

* Thu Feb 13 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1:3.1-15.2
- Rebuild to regenerate auto-requires

* Tue Feb 11 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1:3.1-15.1
- First maven30 software collection build

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 1:3.1-15
- Mass rebuild 2013-12-27

* Fri Jun 28 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 1:3.1-14
- Rebuild to regenerate API documentation
- Resolves: CVE-2013-1571

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:3.1-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Mon Jan 21 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 1:3.1-12
- Add missing connection hostname check against X.509 certificate name
- Resolves: CVE-2012-5783

* Thu Nov  1 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 1:3.1-11
- Add maven POM

* Thu Sep 20 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 1:3.1-10
- Fix license tag

* Thu Sep 20 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 1:3.1-9
- Install LICENSE and NOTICE files
- Add missing R: java, jpackage-utils

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:3.1-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sun Jan 22 2012 Andy Grimm <agrimm@gmail.com> - 1:3.1-7
- Fix character encoding

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:3.1-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Jun 28 2011 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1:3.1-5
- Fix symlinks in javadir

* Tue Jun 28 2011 Alexander Kurtakov <akurtako@redhat.com> 1:3.1-4
- Fix FTBFS.
- Adapt to current guidelines.

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:3.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Nov 10 2010 Alexander Kurtakov <akurtako@redhat.com> 1:3.1-2
- Add missing requires on commons-codec.

* Fri Jul 16 2010 Alexander Kurtakov <akurtako@redhat.com> 1:3.1-1
- Drop gcj_support.
- Fix FTBFS.

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:3.1-0.5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:3.1-0.4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Jul 24 2008 Andrew Overholt <overholt@redhat.com> 1:3.1-0.3
- Update OSGi MANIFEST.MF

* Wed Jul  9 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 1:3.1-0.2
- drop repotag
- fix license tag

* Fri Apr 04 2008 Deepak Bhole <dbhole@redhat.com> - 0:3.1-0jpp.1
- Update to 3.1

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 1:3.0.1-2jpp.2
- Autorebuild for GCC 4.3

* Thu Sep 06 2007 Andrew Overholt <overholt@redhat.com> 1:3.0.1-1jpp.2
- Add OSGi MANIFEST.MF information.

* Fri Mar 16 2007 Permaine Cheung <pcheung@redhat.com> - 1:3.0.1-1jpp.1
- Merge with upstream and more rpmlint cleanup.

* Thu Feb 15 2007 Fernando Nasser <fnasser@redhat.com> - 1:3.0.1-1jpp
- Upgrade to 3.0.1

* Fri Jan 26 2007 Permaine Cheung <pcheung@redhat.com> - 1:3.0-8jpp
- Added versions for provides and obsoletes and rpmlint cleanup.

* Thu Aug 10 2006 Deepak Bhole <dbhole@redhat.com> - 1:3.0-7jpp.1
- Added missing requirements.
- Added missing postun section for javadoc.

* Sat Jul 22 2006 Jakub Jelinek <jakub@redhat.com> - 1:3.0-6jpp_2fc
- Rebuilt

* Thu Jul 20 2006 Deepak Bhole <dbhole@redhat.com> - 1:3.0-6jpp_1fc
- Added conditional native compilation.
- Disable certain ssl related tests that are known to fail with libgcj.

* Thu Apr 06 2006 Fernando Nasser <fnasser@redhat.com> - 1:3.0-5jpp
- Improve backwards compatibility and force removal of older versioned
  packages

* Thu Apr 06 2006 Fernando Nasser <fnasser@redhat.com> - 1:3.0-4jpp
- Remove duplicate release definition
- Require simply a jaxp 1.3

* Thu Apr 06 2006 Fernando Nasser <fnasser@redhat.com> - 1:3.0-3jpp
- BR xml-commons-jaxp-1.3-apis

* Thu Apr 06 2006 Ralph Apel <r.apel@r-apel.de> - 1:3.0-2jpp
- Fix tarball typo
- assure javax classes are used instead of com.sun. ones

* Wed Apr 05 2006 Ralph Apel <r.apel@r-apel.de> - 1:3.0-1jpp
- 3.0 final, drop main version in name

* Thu Oct 20 2005 Jason Corley <jason.corley@gmail.com> - 1:3.0-0.rc4.1jpp
- 3.0rc4

* Thu May 05 2005 Fernando Nasser <fnasser@redhat.com> - 1:3.0-0.rc2.1jpp
- Update to 3.0 rc2.

* Thu Nov  4 2004 Ville Skyttä <ville.skytta at iki.fi> - 1:2.0.2-1jpp
- Update to 2.0.2.
- Fix Group tag in -manual.

* Sun Aug 23 2004 Randy Watler <rwatler at finali.com> - 0:2.0-2jpp
- Rebuild with ant-1.6.2

* Mon Feb 16 2004 Kaj J. Niemi <kajtzu@fi.basen.net> - 0:2.0-1jpp
- 2.0 final

* Thu Jan 22 2004 David Walluck <david@anti-microsoft.org> 0:2.0-0.rc3.1jpp
- 2.0-rc3
- bump epoch

* Tue Oct 14 2003 Ville Skyttä <ville.skytta at iki.fi> - 0:2.0-3.rc2.1jpp
- Update to 2.0rc2.
- Manual subpackage.
- Crosslink with local J2SE javadocs.
- Own unversioned javadoc dir symlink.

* Fri Aug 15 2003 Ville Skyttä <ville.skytta at iki.fi> - 0:2.0-3.rc1.1jpp
- Update to 2.0rc1.
- Include "jakarta-"-less jar symlinks for consistency with other packages.
- Exclude example and contrib sources from main package, they're in -demo.

* Wed Jul  9 2003 Ville Skyttä <ville.skytta at iki.fi> - 0:2.0-2.beta2.1jpp
- Update to 2.0 beta 2.
- Demo subpackage.
- Crosslink with local commons-logging javadocs.

* Wed Jun  4 2003 Ville Skyttä <ville.skytta at iki.fi> - 0:2.0-2.beta1.1jpp
- Update to 2.0 beta 1.
- Non-versioned javadoc symlinking.

* Fri Apr  4 2003 Ville Skyttä <ville.skytta at iki.fi> - 0:2.0-1.alpha3.2jpp
- Rebuild for JPackage 1.5.

* Wed Feb 26 2003 Ville Skyttä <ville.skytta at iki.fi> - 2.0-1.alpha3.1jpp
- Update to 2.0 alpha 3.
- Fix Group tags.
- Run standalone unit tests during build.

* Thu Sep 12 2002 Ville Skyttä <ville.skytta at iki.fi> 2.0-0.cvs20020909.1jpp
- Tune the rpm release number tag so rpm2html doesn't barf on it.

* Mon Sep  9 2002 Ville Skyttä <ville.skytta at iki.fi> 2.0-0.20020909alpha1.1jpp
- 2.0alpha1 snapshot 20020909.
- Use sed instead of bash extensions when symlinking jars during build.
- Add distribution tag.
- Require commons-logging instead of log4j.

* Sat Jan 19 2002 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.0-4jpp
- renamed to jakarta-commons-httpclient
- additional sources in individual archives
- versioned dir for javadoc
- no dependencies for javadoc package
- dropped j2ee package
- adapted to new jsse package
- section macro

* Fri Dec 7 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.0-3jpp
- javadoc into javadoc package

* Sat Nov 3 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.0-2jpp
- fixed jsse subpackage

* Fri Nov 2 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.0-1jpp
- first JPackage release
