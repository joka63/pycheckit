Name:           pycheckit
Version:        0.1.6
Release:        3
# Fill in the actual package summary to submit package to Fedora
Summary:        A file checksummer and integrity tester using CRC64 checksums stored as extended attributes

# Check if the automatically generated License and its spelling is correct for Fedora
# https://docs.fedoraproject.org/en-US/packaging-guidelines/LicensingGuidelines/
License:        GPL-3.0-or-later
URL:            https://github.com/joka63/pycheckit
Source0:        %{name}-%{version}.tar.gz

BuildRequires:  python3-devel
BuildRequires:  python3-cython
BuildRequires:  python3-wheel
BuildRequires:  python3-pytest python3-pytest-cov
BuildRequires:  python3-xattr
BuildRequires:  gcc make
BuildRequires:  rubygem-asciidoctor

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
sed -e 's/^version = ".*"/version = "%{version}"/' -i pyproject.toml
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
* Wed Feb 11 2026 Joachim Katzer <joka63@gmx.de> 0.1.6-3
- fixed missing distribution tag in release 

* Tue Feb 10 2026 Joachim Katzer <joka63@gmx.de> 0.1.6-2
- Fix no error message if file doesn't exist (#4)
  (joka63@users.noreply.github.com)

* Tue Feb 10 2026 Joachim Katzer <joka63@gmx.de> 0.1.6-1
- fix: no error message if file/dir does not exist (joka63@gmx.de)
- test: added checkit compatibility tests (joka63@gmx.de)

* Tue Feb 10 2026 Joachim Katzer <joka63@gmx.de> 0.1.5-1
- fix: options -s -e not working if extended attributes are not supported (joka63@gmx.de)

* Mon Feb 09 2026 Joachim Katzer <joka63@gmx.de> 0.1.4-1
- fix: don't generate hidden files without option -e (joka63@gmx.de)
- doc: removed redundant changelog entries from spec file (joka63@gmx.de)
- doc: Fixed mark-down format issues in ABOUT.md
  (joka63@users.noreply.github.com)
- doc: Add Fedora installation instructions to README
  (joka63@users.noreply.github.com)

* Sun Feb 08 2026 Joachim Katzer <joka63@gmx.de> 0.1.3-4
- fix: build failed on COPR, wrong asciidoctor package name (joka63@gmx.de)
- fix: version not updated in pyproject.toml on tito tag (joka63@gmx.de)

* Sun Feb 08 2026 Joachim Katzer <joka63@gmx.de> 0.1.3-1
- doc: Fix README spelling and update version number
- feat: Added and updated config and spec files to build a RPM for Fedora and RHEL
  systems.
- fix: build failed due to a tito macro error

* Sun Feb 08 2026 Joachim Katzer <joka63@gmx.de> 0.1.2-1
- first package built with tito
- derived from checkit: https://sourceforge.net/projects/check-it/
- ported to Python 

%autochangelog
