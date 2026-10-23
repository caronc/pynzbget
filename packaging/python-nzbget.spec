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
%if 0%{?_module_build}
%bcond_with tests
%else
# When bootstrapping Python, we cannot test this yet
%bcond_without tests
%endif # module_build

%global pypi_name pynzbget
%global pkg_name nzbget

%global common_description %{expand: \
A python wrapper to simplify the handling of NZBGet and SABnzbd Scripts}

Name:           python-%{pkg_name}
Version:        0.7.0
Release:        1%{?dist}
Summary:        Simplify the development and deployment of NZBGet and SABnzbd scripts
License:        GPL-3.0-only
URL:            https://github.com/caronc/%{pypi_name}
Source0:        %{url}/archive/v%{version}/%{pypi_name}-%{version}.tar.gz
BuildArch:      noarch

%description %{common_description}

%package -n python%{python3_pkgversion}-%{pkg_name}
Summary: Simplify the development and deployment of NZBGet and SABnzbd scripts

BuildRequires: python%{python3_pkgversion}-devel
Requires: sqlite

%if %{with tests}
BuildRequires: python%{python3_pkgversion}-mock
BuildRequires: python%{python3_pkgversion}-pytest
%endif # with_tests

%description -n python%{python3_pkgversion}-%{pkg_name} %{common_description}

%prep
%autosetup -n %{pypi_name}-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files %{pkg_name}

%check
%if %{with tests}
%pytest
%endif # with_tests

%files -n python%{python3_pkgversion}-%{pkg_name} -f %{pyproject_files}
%license LICENSE
%doc README.md

%changelog
* Thu Oct 22 2026 Chris Caron <lead2gold@gmail.com> - 0.7.0-1
- Updated to v0.7.0
* Fri Sep 20 2019 Chris Caron <lead2gold@gmail.com> - 0.6.4-1
- Updated to v0.6.4
* Fri Jun 14 2019 Chris Caron <lead2gold@gmail.com> - 0.6.3-1
- Initial release of v0.6.3
