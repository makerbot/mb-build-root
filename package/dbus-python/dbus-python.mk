################################################################################
#
# dbus-python
#
################################################################################

DBUS_PYTHON_VERSION = 1.0.0
DBUS_PYTHON_SOURCE = dbus-python-$(DBUS_PYTHON_VERSION).tar.gz
DBUS_PYTHON_SITE = http://dbus.freedesktop.org/releases/dbus-python/
DBUS_PYTHON_INSTALL_STAGING = YES

DBUS_PYTHON_CONF_ENV = am_cv_pathless_PYTHON=python3 \
		ac_cv_path_PYTHON=$(HOST_DIR)/usr/bin/python3 \
		am_cv_python_version=$(PYTHON3_VERSION) \
		am_cv_python_platform=linux2 \
		am_cv_python_pythondir=/usr/lib/python$(PYTHON3_VERSION_MAJOR)/site-packages \
		am_cv_python_pyexecdir=/usr/lib/python$(PYTHON3_VERSION_MAJOR)/site-packages \
		am_cv_python_includes=-I$(STAGING_DIR)/usr/include/python$(PYTHON3_VERSION_MAJOR)m

DBUS_PYTHON_CONF_OPT = --disable-html-docs --disable-api-docs

DBUS_PYTHON_DEPENDENCIES = dbus-glib python3 host-python3

$(eval $(autotools-package))
