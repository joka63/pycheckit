Name:           pycheckit
Version:        0.1.3
Release:        %autorelease
# Fill in the actual package summary to submit package to Fedora
Summary:        A file checksummer and integrity tester using CRC64 checksums stored as extended attributes

# Check if the automatically generated License and its spelling is correct for Fedora
# https://docs.fedoraproject.org/en-US/packaging-guidelines/LicensingGuidelines/
License:        GPL-3.0-or-later
URL:            https://github.com/joka63/pycheckit
Source:         /home/joachim/Projekte/pycheckit/dist/pycheckit-0.1.2.tar.gz

BuildRequires:  python3-devel
BuildRequires:  python3-cython
BuildRequires:  python3-wheel
BuildRequires:  python3-pytest python3-pytest-cov
BuildRequires:  python3-xattr
BuildRequires:  gcc
BuildRequires:  make asciidoc

Requires:       python3-xattr

# Fill in the actual package description to submit package to Fedora
%global _description %{expand:
Checksum adds additions data assurance
capabilities to filesystems which support
extended attributes.  Checkit allows you
to detect any otherwise undetected data
integrity issues or file changes to any file.
By storing a checksum as an extended attribute,
checkit provides an easy way to detect any
silent data corruption, bit rot or otherwise
undetected error.}

%description %_description

# %package -n     pycheckit
Summary:        %{summary}

# For official Fedora packages, review which extras should be actually packaged
# See: https://docs.fedoraproject.org/en-US/packaging-guidelines/Python/#Extras
%pyproject_extras_subpkg -n pycheckit dev


%prep
%autosetup -p1 -n pycheckit-%{version}
make man


%generate_buildrequires
# Keep only those extras which you actually want to package or use during tests
%pyproject_buildrequires -x dev


%build
%pyproject_wheel


%install
%pyproject_install
# Add top-level Python module names here as arguments, you can use globs
%pyproject_save_files pycheckit


%check
%pyproject_check_import


%files -n pycheckit -f %{pyproject_files}
%{_bindir}/%{name}
%{_datadir}/man/man*/%{name}*
%doc README.md
%doc doc/ABOUT.md
%license COPYING

%changelog
* Sun Feb 08 2026 Joachim Katzer <joka63@gmx.de> 0.1.3-1
- doc: Fix README spelling and update version number
  (joka63@users.noreply.github.com)
-   Added and updated config and spec files to build a RPM for Fedora and RHEL
  systems. (joka63@users.noreply.github.com)
- fix: build failed due to a tito macro error

* Sun Feb 08 2026 Joachim Katzer <joka63@gmx.de>
- Fixed build error 

* Sun Feb 08 2026 Joachim Katzer <joka63@gmx.de> 0.1.2-1
- first package built with tito
- derived from checkit: https://sourceforge.net/projects/check-it/
- ported to Python 

%autochangelog