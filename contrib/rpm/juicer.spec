%if 0%{?rhel} <= 5
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
%endif

Name:          juicer
Summary:       Pulp and release carts
Version:       1.0.0
Release:       1%{?dist}

Group:         Applications/Internet
License:       GPLv3+
Source0:       %{name}-%{version}.tar.gz
Url:           https://github.com/abutcher/juicer/

BuildArch:     noarch

Requires: m2crypto
Requires: python-BeautifulSoup
Requires: python-bitmath
Requires: python-progressbar
Requires: python-pulp-bindings >= 2.6.0-1
Requires: python-pulp-common >= 2.6.0-1
Requires: python-pulp-docker-common >= 1.0.0-1
Requires: python-pymongo
Requires: python-pyrpm
Requires: python-setuptools
BuildRequires: python-devel


%description
Pulp stuff, oh -- and release carts.

%clean
rm -rf $RPM_BUILD_ROOT

%prep
%setup -q

%build
%{__python} setup.py build

%install
mkdir -p $RPM_BUILD_ROOT/%{_mandir}/{man1,man5}/
cp -v juicer.1 $RPM_BUILD_ROOT/%{_mandir}/man1/
cp -v juicer.conf.5 $RPM_BUILD_ROOT/%{_mandir}/man5/
%{__python2} setup.py install -O1 --root=$RPM_BUILD_ROOT --record=juicer-files.txt


######################################################################
# files for 'juicer' package
%files -f juicer-files.txt
%doc README.rst LICENSE
%doc %{_mandir}/man1/juicer*
%doc %{_mandir}/man5/juicer*


######################################################################
%changelog
* Wed May 27 2015 Tim Bielawa <tbielawa@redhat.com> - 1.0.0-1
- First post!
