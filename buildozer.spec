[app]
title = EEGnosis Atlas
package.name = eegnosis
package.domain = com.eegnosis

source.dir = .
source.include_exts = py,png,jpg,jpeg,json,txt

version = 1.0.0

# ---- requirements ----
# نجبر p4a على استخدام Python 3.11 (بدلاً من 3.14)
# + kivy 2.1.0 (يستخدم pyjnius 1.6.1 المتوفر)
requirements = python3==3.11.5,kivy==2.1.0

orientation = all
fullscreen = 0

android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 30
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a
android.allow_backup = True
android.release_artifact = apk
android.debug_artifact = apk
android.accept_sdk_license = True
android.enable_androidx = True
android.log_level = 2

[buildozer]
log_level = 2
warn_on_root = 1
