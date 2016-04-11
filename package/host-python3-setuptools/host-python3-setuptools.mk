################################################################################
#
# host-python3-setuptools
#
################################################################################

HOST_PYTHON3_SETUPTOOLS_VERSION = 20.6.7
HOST_PYTHON3_SETUPTOOLS_SOURCE  = setuptools-$(HOST_PYTHON3_SETUPTOOLS_VERSION).tar.gz
HOST_PYTHON3_SETUPTOOLS_SITE    = https://pypi.python.org/packages/source/s/setuptools/
HOST_PYTHON3_SETUPTOOLS_DEPENDENCIES = host-python3

define HOST_PYTHON3_SETUPTOOLS_BUILD_CMDS
	(cd $(@D); $(HOST_DIR)/usr/bin/python3 setup.py build)
endef

define HOST_PYTHON3_SETUPTOOLS_INSTALL_TARGET_CMDS
	(cd $(@D); \
	PYTHONPATH=$(TARGET_DIR)/usr/lib/python$(PYTHON3_VERSION_MAJOR)/site-packages \
	$(HOST_DIR)/usr/bin/python3 setup.py install --prefix=$(HOST_DIR)/usr)
endef

$(eval $(generic-package))
