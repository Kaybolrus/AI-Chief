[app]
title = AI Chef Pro
package.name = aichefpro
package.domain = com.aichef
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0

requirements = python3,flet,certifi

orientation = portrait
fullscreen = 0

android.permissions = INTERNET, VIBRATE, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.api = 35
android.minapi = 21
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
