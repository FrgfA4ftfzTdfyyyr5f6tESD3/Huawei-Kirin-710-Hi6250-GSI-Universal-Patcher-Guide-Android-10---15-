#!/system/bin/sh

(getprop ro.vendor.build.security_patch; getprop ro.keymaster.xxx.security_patch) |sort |tail -n 1 |while read v;do
    [ -n "$v" ] && resetprop_phh ro.build.version.security_patch "$v"
done

resetprop_phh ro.build.host android-build
resetprop_phh ro.product.build.tags release-keys
resetprop_phh ro.system.build.tags release-keys
resetprop_phh ro.system_ext.build.tags release-keys
resetprop_phh ro.vendor.build.tags release-keys
resetprop_phh ro.build.type user
resetprop_phh ro.product.build.type user
resetprop_phh ro.system.build.type user
resetprop_phh ro.system_ext.build.type user
resetprop_phh ro.vendor.build.type user
resetprop_phh ro.build.user nobody
resetprop_phh ro.build.tags release-keys
resetprop_phh ro.boot.vbmeta.device_state locked
resetprop_phh ro.boot.verifiedbootstate green
resetprop_phh ro.boot.flash.locked 1
resetprop_phh ro.boot.veritymode enforcing
resetprop_phh ro.boot.warranty_bit 0
resetprop_phh ro.warranty_bit 0
resetprop_phh ro.debuggable 0
resetprop_phh ro.secure 1
resetprop_phh ro.build.type user
resetprop_phh --delete ro.build.selinux
resetprop_phh ro.adb.secure 1

resetprop_phh --delete ro.lineage.version
resetprop_phh --delete ro.modversion

setprop ctl.restart adbd
