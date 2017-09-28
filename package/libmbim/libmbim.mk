################################################################################
#
# libmbim
#
################################################################################

LIBMBIM_VERSION = 1.14.0
LIBMBIM_SITE = http://www.freedesktop.org/software/libmbim
LIBMBIM_SOURCE = libmbim-$(LIBMBIM_VERSION).tar.xz
LIBMBIM_LICENSE = LGPL-2.0+ (library), GPL-2.0+ (programs)
LIBMBIM_LICENSE_FILES = COPYING
LIBMBIM_INSTALL_STAGING = YES

LIBMBIM_DEPENDENCIES = libglib2 udev libgudev

# we don't want -Werror
LIBMBIM_CONF_OPTS = --enable-more-warnings=no

$(eval $(autotools-package))
