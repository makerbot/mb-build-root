################################################################################
#
# python3
#
################################################################################

PYTHON3_VERSION_MAJOR = 3.4
PYTHON3_VERSION       = $(PYTHON3_VERSION_MAJOR).3
PYTHON3_SOURCE        = Python-$(PYTHON3_VERSION).tar.xz
PYTHON3_SITE          = http://python.org/ftp/python/$(PYTHON3_VERSION)

# Python itself doesn't use libtool, but it includes the source code
# of libffi, which uses libtool. Unfortunately, it uses a beta version
# of libtool for which we don't have a matching patch. However, this
# is not a problem, because we don't use the libffi copy included in
# the Python sources, but instead use an external libffi library.
PYTHON3_LIBTOOL_PATCH = NO

# Python needs itself and a "pgen" program to build itself, both being
# provided in the Python sources. So in order to cross-compile Python,
# we need to build a host Python first. This host Python is also
# installed in $(HOST_DIR), as it is needed when cross-compiling
# third-party Python modules.

HOST_PYTHON3_CONF_OPT += 	\
	--without-ensurepip	\
	--without-cxx-main 	\
	--disable-sqlite3	\
	--disable-tk		\
	--with-expat=system	\
	--disable-curses	\
	--disable-codecs-cjk	\
	--disable-nis		\
	--disable-unicodedata	\
	--disable-test-modules	\
	--disable-idle3		\
	--disable-ossaudiodev	\
	--disable-pyo-build

# Make sure that LD_LIBRARY_PATH overrides -rpath.
# This is needed because libpython may be installed at the same time that
# python is called.
HOST_PYTHON3_CONF_ENV += \
	LDFLAGS="$(HOST_LDFLAGS) -Wl,--enable-new-dtags"

PYTHON3_DEPENDENCIES = host-python3 libffi

HOST_PYTHON3_DEPENDENCIES = host-expat host-zlib

PYTHON3_INSTALL_STAGING = YES

#PY3_CONFIG_DIR = config-3.3m
ifeq ($(BR2_PACKAGE_PYTHON3_DEBUG),y)
PYTHON3_CONF_OPT += --with-pydebug
#PY3_CONFIG_DIR = config-3.3dm
endif

ifeq ($(BR2_PACKAGE_PYTHON3_READLINE),y)
PYTHON3_DEPENDENCIES += readline
endif

ifeq ($(BR2_PACKAGE_PYTHON3_CURSES),y)
PYTHON3_DEPENDENCIES += ncurses
else
PYTHON3_CONF_OPT += --disable-curses
endif

ifeq ($(BR2_PACKAGE_PYTHON3_DECIMAL),y)
PYTHON3_DEPENDENCIES += mpdecimal
PYTHON3_CONF_OPT += --with-libmpdec=system
else
PYTHON3_CONF_OPT += --with-libmpdec=none
endif

ifeq ($(BR2_PACKAGE_PYTHON3_PYEXPAT),y)
PYTHON3_DEPENDENCIES += expat
PYTHON3_CONF_OPT += --with-expat=system
else
PYTHON3_CONF_OPT += --with-expat=none
endif

ifeq ($(BR2_PACKAGE_PYTHON3_GDBM),y)
PYTHON3_DEPENDENCIES += gdbm
endif

ifeq ($(BR2_PACKAGE_PYTHON3_PYC_ONLY),y)
PYTHON3_CONF_OPT += --enable-old-stdlib-cache
endif

ifeq ($(BR2_PACKAGE_PYTHON3_PY_ONLY),y)
PYTHON3_CONF_OPT += --disable-pyc-build
endif

ifeq ($(BR2_PACKAGE_PYTHON3_SQLITE),y)
PYTHON3_DEPENDENCIES += sqlite
else
PYTHON3_CONF_OPT += --disable-sqlite3
endif

ifeq ($(BR2_PACKAGE_PYTHON3_SSL),y)
PYTHON3_DEPENDENCIES += openssl
HOST_PYTHON3_DEPENDENCIES += host-openssl
endif

ifneq ($(BR2_PACKAGE_PYTHON3_CODECSCJK),y)
PYTHON3_CONF_OPT += --disable-codecs-cjk
endif

ifneq ($(BR2_PACKAGE_PYTHON3_UNICODEDATA),y)
PYTHON3_CONF_OPT += --disable-unicodedata
endif

ifeq ($(BR2_PACKAGE_PYTHON3_BZIP2),y)
PYTHON3_DEPENDENCIES += bzip2
endif

ifeq ($(BR2_PACKAGE_PYTHON3_ZLIB),y)
PYTHON3_DEPENDENCIES += zlib
endif

ifeq ($(BR2_PACKAGE_PYTHON3_OSSAUDIODEV),y)
PYTHON3_CONF_OPT += --enable-ossaudiodev
else
PYTHON3_CONF_OPT += --disable-ossaudiodev
endif

PYTHON3_CONF_ENV += \
	ac_cv_have_long_long_format=yes \
	ac_cv_file__dev_ptmx=yes \
	ac_cv_file__dev_ptc=yes \
	ac_cv_working_tzset=yes

# uClibc is known to have a broken wcsftime() implementation, so tell
# Python 3 to fall back to strftime() instead.
ifeq ($(BR2_TOOLCHAIN_USES_UCLIBC),y)
PYTHON3_CONF_ENV += ac_cv_func_wcsftime=no
endif

PYTHON3_CONF_OPT += \
	--without-ensurepip	\
	--without-cxx-main 	\
	--with-system-ffi	\
	--disable-pydoc		\
	--disable-test-modules	\
	--disable-lib2to3	\
	--disable-tk		\
	--disable-nis		\
	--disable-idle3		\
	--disable-pyo-build

# This is needed to make sure the Python build process doesn't try to
# regenerate those files with the pgen program. Otherwise, it builds
# pgen for the target, and tries to run it on the host.

define PYTHON3_TOUCH_GRAMMAR_FILES
	touch $(@D)/Include/graminit.h $(@D)/Python/graminit.c
endef

PYTHON3_POST_PATCH_HOOKS += PYTHON3_TOUCH_GRAMMAR_FILES

#
# Remove useless files. In the config/ directory, only the Makefile
# and the pyconfig.h files are needed at runtime.
#
define PYTHON3_REMOVE_USELESS_FILES
	rm -f $(TARGET_DIR)/usr/bin/python$(PYTHON3_VERSION_MAJOR)-config
	rm -f $(TARGET_DIR)/usr/bin/python$(PYTHON3_VERSION_MAJOR)m-config
	rm -f $(TARGET_DIR)/usr/bin/python3-config
	rm -f $(TARGET_DIR)/usr/bin/smtpd.py.3
	for i in `find $(TARGET_DIR)/usr/lib/python$(PYTHON3_VERSION_MAJOR)/config-$(PYTHON3_VERSION_MAJOR)m/ \
		-type f -not -name pyconfig.h -a -not -name Makefile` ; do \
		rm -f $$i ; \
	done
endef

PYTHON3_POST_INSTALL_TARGET_HOOKS += PYTHON3_REMOVE_USELESS_FILES

#
# Make sure libpython gets stripped out on target
#
define PYTHON3_ENSURE_LIBPYTHON_STRIPPED
	chmod u+w $(TARGET_DIR)/usr/lib/libpython$(PYTHON3_VERSION_MAJOR)*.so
endef

PYTHON3_POST_INSTALL_TARGET_HOOKS += PYTHON3_ENSURE_LIBPYTHON_STRIPPED

PYTHON3_AUTORECONF = YES

define PYTHON3_INSTALL_SYMLINK
	ln -fs python3 $(TARGET_DIR)/usr/bin/python
endef

ifneq ($(BR2_PACKAGE_PYTHON),y)
PYTHON3_POST_INSTALL_TARGET_HOOKS += PYTHON3_INSTALL_SYMLINK
endif

ifeq ($(BR2_PACKAGE_PYTHON3_PY_ONLY),y)
define PYTHON3_REMOVE_MODULES_FILES
	for i in `find $(TARGET_DIR)/usr/lib/python$(PYTHON3_VERSION_MAJOR) \
		 -name __pycache__` ; do \
		rm -rf $$i ; \
	done
endef
endif

ifeq ($(BR2_PACKAGE_PYTHON3_PYC_ONLY),y)
define PYTHON3_REMOVE_MODULES_FILES
	for i in `find $(TARGET_DIR)/usr/lib/python$(PYTHON3_VERSION_MAJOR) \
		 -name *.py` ; do \
		rm -f $$i ; \
	done
endef
endif

PYTHON3_POST_INSTALL_TARGET_HOOKS += PYTHON3_REMOVE_MODULES_FILES


$(eval $(autotools-package))
$(eval $(host-autotools-package))
