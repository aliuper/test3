[app]
title = IPTV Editor Pro
package.name = iptveditorpro
package.domain = com.yengec
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0
icon.filename = icon.png

# Python 3.11.9 - Android için en stabil versiyon
requirements = python3==3.11.9,kivy==2.3.0,requests,urllib3,certifi,pillow

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

# İzinler
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Optimizasyonlar
android.release_artifact = apk
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
