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

# Requires: python-BeautifulSoup
# Requires: python-requests >= 0.13.1
# Requires: rpm-python
# Requires: PyYAML
# Requires: python-progressbar
# Requires: python >= 2.5
# Requires: pymongo
# Requires: python-magic
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
# %{__python} setup.py install -O1 --root=$RPM_BUILD_ROOT
# mkdir -p $RPM_BUILD_ROOT/%{_mandir}/{man1,man5}/
# cp -v docs/man/man1/*.1 $RPM_BUILD_ROOT/%{_mandir}/man1/
# cp -v docs/man/man5/*.5 $RPM_BUILD_ROOT/%{_mandir}/man5/
# mkdir -p $RPM_BUILD_ROOT/%{_datadir}/juicer
# #cp -vr share/juicer/completions $RPM_BUILD_ROOT/%{_datadir}/juicer/
# cp -vr share/juicer/juicer.conf $RPM_BUILD_ROOT/%{_datadir}/juicer/
%{__python2} setup.py install -O1 --root=$RPM_BUILD_ROOT --record=juicer-files.txt


######################################################################
# files for 'juicer' package
%files -f juicer-files.txt
#%dir %{python2_sitelib}/juicer
%doc README.rst LICENSE



######################################################################
%changelog
* Wed May 27 2015 Tim Bielawa <tbielawa@redhat.com> - 1.0.0-1
- First post!
