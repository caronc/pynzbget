# Copyright (C) 2019 Chris Caron <lead2gold@gmail.com>
# All rights reserved.
#
# This code is licensed under the MIT License.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files(the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and / or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions :
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
###############################################################################
%global with_python2 1
%global with_python3 1

%if 0%{?fedora} || 0%{?rhel} >= 8
# Python v2 Support dropped
%global with_python2 0
%endif # fedora and/or rhel7

%if 0%{?_module_build}
%bcond_with tests
%else
# When bootstrapping Python, we cannot test this yet
%bcond_without tests
%endif # module_build

%if 0%{?rhel} && 0%{?rhel} <= 7
%global with_python3 0
%endif # using rhel7

%global pypi_name pynzbget
%global pkg_name nzbget

%global common_description %{expand: \
A python wrapper to simplify the handling of NZBGet and SABnzbd Scripts}

Name:           python-%{pkg_name}
Version:        0.6.3
Release:        1%{?dist}
Summary:        Simplify the development and deployment of NZBGet and SABnzbd scripts
License:        GPLv3
URL:            https://github.com/caronc/%{pypi_name}
Source0:        %{url}/archive/v%{version}/%{pypi_name}-%{version}.tar.gz
# this patch allows version of requests that ships with RHEL v7 to
# correctly handle test coverage.  It also removes reference to a
# extra check not supported in py.test in EPEL7 builds
BuildArch:      noarch

%description %{common_description}

%if 0%{?with_python2}
%package -n python2-%{pkg_name}
Summary: Simplify the development and deployment of NZBGet and SABnzbd scripts
%{?python_provide:%python_provide python2-%{pkg_name}}

BuildRequires: sqlite
BuildRequires: python2-devel
BuildRequires: python-six
%if 0%{?rhel} && 0%{?rhel} <= 7
BuildRequires: python-lxml
%else
BuildRequires: python2-lxml
%endif # using rhel7

Requires: sqlite
Requires: python-six
%if 0%{?rhel} && 0%{?rhel} <= 7
Requires: python-lxml
%else
Requires: python2-lxml
%endif # using rhel7

%if %{with tests}
BuildRequires: python-mock
BuildRequires: python2-pytest-runner
BuildRequires: python2-pytest
%endif # with_tests

%description -n python2-%{pkg_name} %{common_description}
%endif # with_python2

%if 0%{?with_python3}
%package -n python%{python3_pkgversion}-%{pkg_name}
Summary: Simplify the development and deployment of NZBGet and SABnzbd scripts
%{?python_provide:%python_provide python%{python3_pkgversion}-%{pkg_name}}

BuildRequires: python%{python3_pkgversion}-devel
BuildRequires: python%{python3_pkgversion}-six
BuildRequires: python%{python3_pkgversion}-lxml
Requires: python%{python3_pkgversion}-six
Requires: python%{python3_pkgversion}-lxml

%if %{with tests}
BuildRequires: python%{python3_pkgversion}-mock
BuildRequires: python%{python3_pkgversion}-pytest
BuildRequires: python%{python3_pkgversion}-pytest-runner
%endif # with_tests

%description -n python%{python3_pkgversion}-%{pkg_name} %{common_description}
%endif # with_python3

%prep
%setup -q -n %{pypi_name}-%{version}

%build
%if 0%{?with_python2}
%py2_build
%endif # with_python2
%if 0%{?with_python3}
%py3_build
%endif # with_python3

%install
%if 0%{?with_python2}
%py2_install
%endif # with_python2
%if 0%{?with_python3}
%py3_install
%endif # with_python3

%if %{with tests}
%if 0%{?rhel} && 0%{?rhel} <= 7
# Can not do testing with RHEL7 because the version of py.test is too old
%else
%check
%if 0%{?with_python2}
PYTHONPATH=%{buildroot}%{python2_sitelib} py.test
%endif # with_python2
%if 0%{?with_python3}
PYTHONPATH=%{buildroot}%{python3_sitelib} py.test-%{python3_version}
%endif # with_python3
%endif # rhel7
%endif # with_tests
%if 0%{?with_python2}
%files -n python2-%{pkg_name}
%license LICENSE
%doc README.md
%{python2_sitelib}/%{pkg_name}
%{python2_sitelib}/*.egg-info
%endif # with_python2

%if 0%{?with_python3}
%files -n python%{python3_pkgversion}-%{pkg_name}
%license LICENSE
%doc README.md
%{python3_sitelib}/%{pkg_name}
%{python3_sitelib}/*.egg-info
%endif # with_python3

%changelog
* Fri Jun 14 2019 Chris Caron <lead2gold@gmail.com> - 0.6.3-1
- Initial release of v0.6.3
