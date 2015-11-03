################################################################################
#
# zxing
#
################################################################################

ZXING_VERSION = 5ce91bb
ZXING_SITE = http://y.soft.makerbot.net/files
ZXING_SOURCE = ZXing-$(ZXING_VERSION).zip
ZXING_LICENSE = Apache v2.0
ZXING_LICENSE_FILES = COPYING
ZXING_INSTALL_STAGING = YES

ifneq ($(BR2_ENABLE_LOCALE),y)
ZXING_DEPENDENCIES += libiconv
endif

define ZXING_EXTRACT_CMDS
	unzip -d $(BUILD_DIR) $(DL_DIR)/$(ZXING_SOURCE)
endef

$(eval $(cmake-package))
