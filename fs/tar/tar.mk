################################################################################
#
# tar to archive target filesystem
#
################################################################################

TAR_OPTS := $(BR2_TARGET_ROOTFS_TAR_OPTIONS)

define ROOTFS_TAR_CMD
 cp -pr $(TARGET_DIR)/../bw-home $(TARGET_DIR)/var/home;\
 chown -R 1:1 $(TARGET_DIR)/var/home;\
 mv $(TARGET_DIR)/etc/init.d/S45connman $(TARGET_DIR)/etc/init.d/X45connman;\
 tar -c$(TAR_OPTS)f $@ -C $(TARGET_DIR) .;\
 mv $(TARGET_DIR)/etc/init.d/X45connman $(TARGET_DIR)/etc/init.d/S45connman;\
 rm -rf $(TARGET_DIR)/var/home
endef

$(eval $(call ROOTFS_TARGET,tar))
