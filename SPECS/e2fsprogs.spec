%global package_speccommit 74d1337441ac2293c1af08967f4573744e38825b
%global usver 1.47.0
%global xsver 1
%global xsrel %{xsver}%{?xscount}%{?xshash}
Summary: Utilities for managing ext2, ext3, and ext4 file systems
Name: e2fsprogs
Version: 1.47.0
Release: %{?xsrel}.1%{?dist}

# License tags based on COPYING file distinctions for various components
License: GPLv2
Source0: e2fsprogs-1.47.0.tar.xz
Patch0: 0001-remove-local-PATH.patch

Url: http://e2fsprogs.sourceforge.net/
Requires: e2fsprogs-libs = %{version}-%{release}
Requires: libcom_err = %{version}-%{release}
Requires: libss = %{version}-%{release}

Obsoletes: e4fsprogs < %{version}-%{release}
Provides: e4fsprogs = %{version}-%{release}

BuildRequires: pkgconfig, texinfo, libselinux-devel, gcc
BuildRequires: fuse-devel
BuildRequires: libsepol-devel
BuildRequires: libblkid-devel
BuildRequires: libuuid-devel
BuildRequires: gettext
BuildRequires: systemd
BuildRequires: make


%description
The e2fsprogs package contains a number of utilities for creating,
checking, modifying, and correcting any inconsistencies in second,
third and fourth extended (ext2/ext3/ext4) file systems. E2fsprogs
contains e2fsck (used to repair file system inconsistencies after an
unclean shutdown), mke2fs (used to initialize a partition to contain
an empty ext2 file system), debugfs (used to examine the internal
structure of a file system, to manually repair a corrupted
file system, or to create test cases for e2fsck), tune2fs (used to
modify file system parameters), and most of the other core ext2fs
file system utilities.

You should install the e2fsprogs package if you need to manage the
performance of an ext2, ext3, or ext4 file system.

%package libs
Summary: Ext2/3/4 file system specific shared libraries
License: GPLv2 and LGPLv2
Requires: libcom_err%{?_isa} = %{version}-%{release}

%description libs
E2fsprogs-libs contains libe2p and libext2fs, the libraries of the
e2fsprogs package.

These libraries are used to directly access ext2/3/4 file systems
from user space.

%package static
Summary: Ext2/3/4 file system specific static libraries
License: GPLv2 and LGPLv2

%description static
E2fsprogs-static contains all static libraries built from e2fsprogs,
including libext2fs, libcom_err, libe2p, and libss.

These libraries are used to directly access ext2/3/4 file systems
from user space, and perform other useful functions.

%package devel
Summary: Ext2/3/4 file system specific libraries and headers
License: GPLv2 and LGPLv2
Requires: e2fsprogs-libs%{?_isa} = %{version}-%{release}
Requires: libcom_err-devel%{?_isa} = %{version}-%{release}
Requires: gawk
Requires: pkgconfig

%description devel
E2fsprogs-devel contains the libraries and header files needed to
develop second, third and fourth extended (ext2/ext3/ext4)
file system specific programs.

You should install e2fsprogs-devel if you want to develop ext2/3/4
file system specific programs. If you install e2fsprogs-devel, you'll
also want to install e2fsprogs.

%package -n libcom_err
Summary: Common error description library
License: MIT

%description -n libcom_err
This is the common error description library, part of e2fsprogs.

libcom_err is an attempt to present a common error-handling mechanism.

%package -n libcom_err-devel
Summary: Common error description library
License: MIT
Requires: libcom_err%{?_isa} = %{version}-%{release}
Requires: pkgconfig

%description -n libcom_err-devel
This is the common error description development library and headers,
part of e2fsprogs.  It contains the compile_et command, used
to convert a table listing error-code names and associated messages
messages into a C source file suitable for use with the library.

libcom_err is an attempt to present a common error-handling mechanism.

%package -n libss
Summary: Command line interface parsing library
License: MIT
Requires: libcom_err%{?_isa} = %{version}-%{release}

%description -n libss
This is libss, a command line interface parsing library, part of e2fsprogs.

This package includes a tool that parses a command table to generate
a simple command-line interface parser, the include files needed to
compile and use it.

It was originally inspired by the Multics SubSystem library.

%package -n libss-devel
Summary: Command line interface parsing library
License: MIT
Requires: libss%{?_isa} = %{version}-%{release}
Requires: pkgconfig

%description -n libss-devel
This is the command line interface parsing (libss) development library
and headers, part of e2fsprogs.  It contains the mk_cmds command, which
parses a command table to generate a simple command-line interface parser.

It was originally inspired by the Multics SubSystem library.

%package -n e2scrub
Summary: Online Ext4 metadata consistency checking tool and service
License: GPLv2 and LGPLv2
Requires: systemd
Requires: util-linux
Requires: lvm2
Requires: e2fsprogs%{?_isa} = %{version}-%{release}

%description -n e2scrub
This package includes e2scrub script that can check ext[234] file system
metadata consistency while the file system is online. It also containes a
systemd service that can be enabled to do consistency check periodically.

The file system consistency check can be performed online and does not
require the file system to be unmounted. It uses lvm snapshots to do this
which means that it can only be done on file systems that are on a lvm
managed device with some free space available in respective volume group.

%prep
%autosetup -p1

# Remove flawed tests
rm -rf tests/m_rootdir_acl

%global _udevdir %{_prefix}/lib/udev/rules.d

%build
%configure CFLAGS="$RPM_OPT_FLAGS -fno-strict-aliasing" \
	   --enable-elf-shlibs --enable-nls --disable-uuidd --disable-fsck \
	   --disable-e2initrd-helper --disable-libblkid --disable-libuuid \
	   --enable-quota --with-root-prefix=/usr --with-crond-dir=no
%if 0%{?xenserver} < 9
## This test fails on older coreutils because it needs an argument for timeout
## that the older coreutils does not understand
rm -rf tests/r_corrupt_fs
%endif
%make_build

%install
rm -rf %{buildroot}
export PATH=/sbin:$PATH
%make_install install-libs \
	root_sbindir=%{_sbindir} root_libdir=%{_libdir}

# Hack for now, otherwise strip fails.
chmod +w %{buildroot}%{_libdir}/*.a

%find_lang %{name}

%check
make PRINT_FAILED=yes fullcheck

# XCP-ng: in 8.2, replace the use of %%ldconfig_scriptlets
# (which is provided by epel-rpm-macros, not used to build anything
# currently in 8.2) by what it would evaluate to.

#%%ldconfig_scriptlets libs
%post -p /sbin/ldconfig libs
%postun -p /sbin/ldconfig libs

#%%ldconfig_scriptlets -n libcom_err
%post -p /sbin/ldconfig -n libcom_err
%postun -p /sbin/ldconfig -n libcom_err

#%%ldconfig_scriptlets -n libss
%post -p /sbin/ldconfig -n libss
%postun -p /sbin/ldconfig -n libss

%files -f %{name}.lang
%doc README
%{!?_licensedir:%global license %%doc}

%config(noreplace) %{_sysconfdir}/mke2fs.conf

%{_sbindir}/badblocks
%{_sbindir}/debugfs
%{_sbindir}/dumpe2fs
%{_sbindir}/e2fsck
%{_sbindir}/e2image
%{_sbindir}/e2label
%{_sbindir}/e2mmpstatus
%{_sbindir}/e2undo
%{_sbindir}/e4crypt
%{_sbindir}/fsck.ext2
%{_sbindir}/fsck.ext3
%{_sbindir}/fsck.ext4
%{_sbindir}/logsave
%{_sbindir}/mke2fs
%{_sbindir}/mkfs.ext2
%{_sbindir}/mkfs.ext3
%{_sbindir}/mkfs.ext4
%{_sbindir}/resize2fs
%{_sbindir}/tune2fs
%{_sbindir}/filefrag
%{_sbindir}/e2freefrag
%{_sbindir}/e4defrag
%{_sbindir}/mklost+found

%{_bindir}/chattr
%{_bindir}/lsattr
%{_bindir}/fuse2fs
%{_mandir}/man1/chattr.1*
%{_mandir}/man1/fuse2fs.1*
%{_mandir}/man1/lsattr.1*

%{_mandir}/man5/ext2.5*
%{_mandir}/man5/ext3.5*
%{_mandir}/man5/ext4.5*
%{_mandir}/man5/e2fsck.conf.5*
%{_mandir}/man5/mke2fs.conf.5*

%{_mandir}/man8/badblocks.8*
%{_mandir}/man8/debugfs.8*
%{_mandir}/man8/dumpe2fs.8*
%{_mandir}/man8/e2fsck.8*
%{_mandir}/man8/e4crypt.8*
%{_mandir}/man8/filefrag.8*
%{_mandir}/man8/e2freefrag.8*
%{_mandir}/man8/e4defrag.8*
%{_mandir}/man8/fsck.ext2.8*
%{_mandir}/man8/fsck.ext3.8*
%{_mandir}/man8/fsck.ext4.8*
%{_mandir}/man8/e2image.8*
%{_mandir}/man8/e2label.8*
%{_mandir}/man8/e2mmpstatus.8*
%{_mandir}/man8/e2undo.8*
%{_mandir}/man8/logsave.8*
%{_mandir}/man8/mke2fs.8*
%{_mandir}/man8/mkfs.ext2.8*
%{_mandir}/man8/mkfs.ext3.8*
%{_mandir}/man8/mkfs.ext4.8*
%{_mandir}/man8/mklost+found.8*
%{_mandir}/man8/resize2fs.8*
%{_mandir}/man8/tune2fs.8*

# We do not install e2scrub cron job so just exclude it
%exclude %{_libdir}/e2fsprogs/e2scrub_all_cron

%files libs
%{!?_licensedir:%global license %%doc}
%license NOTICE
%{_libdir}/libe2p.so.*
%{_libdir}/libext2fs.so.*

%files static
%{!?_licensedir:%global license %%doc}
%license NOTICE
%{_libdir}/*.a

%files devel
%{_infodir}/libext2fs.info*
%{_libdir}/libe2p.so
%{_libdir}/libext2fs.so
%{_libdir}/pkgconfig/e2p.pc
%{_libdir}/pkgconfig/ext2fs.pc

%{_includedir}/e2p
%{_includedir}/ext2fs

%files -n libcom_err
%{!?_licensedir:%global license %%doc}
%license NOTICE
%{_libdir}/libcom_err.so.*

%files -n libcom_err-devel
%{_bindir}/compile_et
%{_libdir}/libcom_err.so
%{_datadir}/et
%{_includedir}/et
%{_includedir}/com_err.h
%{_mandir}/man1/compile_et.1*
%{_mandir}/man3/com_err.3*
%{_libdir}/pkgconfig/com_err.pc

%files -n libss
%{!?_licensedir:%global license %%doc}
%license NOTICE
%{_libdir}/libss.so.*

%files -n libss-devel
%{_bindir}/mk_cmds
%{_libdir}/libss.so
%{_datadir}/ss
%{_includedir}/ss
%{_mandir}/man1/mk_cmds.1*
%{_libdir}/pkgconfig/ss.pc

%files -n e2scrub
%config(noreplace) %{_sysconfdir}/e2scrub.conf
%{_sbindir}/e2scrub
%{_sbindir}/e2scrub_all
%{_mandir}/man8/e2scrub.8*
%{_mandir}/man8/e2scrub_all.8*
%{_libdir}/e2fsprogs/e2scrub_fail
%{_unitdir}/e2scrub@.service
%{_unitdir}/e2scrub_all.service
%{_unitdir}/e2scrub_all.timer
%{_unitdir}/e2scrub_fail@.service
%{_unitdir}/e2scrub_reap.service
%{_udevdir}/96-e2scrub.rules

%changelog
* Fri Oct 13 2023 Samuel Verschelde <stormi-xcp@ylix.fr> - 1.47.0-1.1
- Replace %%ldconfig_scriptlets with what it would evaluate to
- This macro would require epel-rpm-macros, which is not available in XCP-ng 8.2

* Mon Oct 02 2023 Tim Smith <tim.smith@citrix.com> - 1.47.0-1
- Update to 1.47.0 (Fixes CVE-2022-1304)

* Mon Oct 02 2023 Tim Smith <tim.smith@citrix.com> - 1.46.5-2
- Improve build compatibility with older Xenserver releases

* Thu Aug 24 2023 Lin Liu <lin.liu@citrix.com> - 1.46.5-1
- First imported release

