################################################################################
#
# python-codernitydb3
#
################################################################################

PYTHON3_CODERNITYDB3_VERSION = master
PYTHON3_CODERNITYDB3_SOURCE = andy0130tw-CodernityDB3-a3ecf58.tar.gz
PYTHON3_CODERNITYDB3_SITE = https://github.com/andy0130tw/CodernityDB3/tarball/$(PYTHON3_CODERNITYDB3_VERSION)

PYTHON3_CODERNITYDB3_DEPENDENCIES = python3 host-python3-setuptools

define PYTHON3_CODERNITYDB3_BUILD_CMDS
    (cd $(@D); $(HOST_DIR)/usr/bin/python3 setup.py build)
endef

define PYTHON3_CODERNITYDB3_INSTALL_TARGET_CMDS
    (cd $(@D); $(HOST_DIR)/usr/bin/python3 setup.py install --prefix=$(TARGET_DIR)/usr)
endef

$(eval $(generic-package))
