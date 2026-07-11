[app]
title = My Wellness
package.name = mywellness
package.domain = org.wiam.wellness

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json

version = 1.0
requirements = python3,kivy==2.3.0,kivymd==1.2.0,plyer,pillow

orientation = portrait
fullscreen = 0

icon.filename = %(source.dir)s/icon.png

android.permissions = INTERNET,VIBRATE,WAKE_LOCK,POST_NOTIFICATIONS
android.api = 33
android.minapi = 21
android.ndk_api = 21
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1