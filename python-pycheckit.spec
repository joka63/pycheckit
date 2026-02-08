Name:           pycheckit
Version:        0.1.2
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

%package -n     python3-pycheckit
Summary:        %{summary}

%description -n python3-pycheckit %_description

# For official Fedora packages, review which extras should be actually packaged
# See: https://docs.fedoraproject.org/en-US/packaging-guidelines/Python/#Extras
%pyproject_extras_subpkg -n python3-pycheckit dev


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


%files -n python3-pycheckit -f %{pyproject_files}
%{_bindir}/%{name}
%{_datadir}/man/man*/%{name}*

%changelog
%autochangelog