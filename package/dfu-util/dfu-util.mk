################################################################################
#
# dfu-util
#
################################################################################

DFU_UTIL_VERSION = 0.9
DFU_UTIL_SITE = http://dfu-util.sourceforge.net/releases
DFU_UTIL_LICENSE = GPL-2.0+
DFU_UTIL_LICENSE_FILES = COPYING

DFU_UTIL_INSTALL_STAGING = YES
DFU_UTIL_INSTALL_TARGET = YES
DFU_UTIL_AUTORECONF = YES
DFU_UTIL_DEPENDENCIES = libusb
$(eval $(autotools-package))

HOST_DFU_UTIL_DEPENDENCIES = host-libusb

$(eval $(host-autotools-package))
