[app]
# m3uScan v21.5 - Kivy Edition
title = m3uScan v21.5
package.name = m3uscan
package.domain = org.thegeorguy

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# Version
version = 21.5

# Requirements
# Kivy + Dependencies
requirements = python3,kivy,aiohttp,tqdm

# Permissions
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE

# Features
android.features = android.hardware.wifi

# Orientation
orientation = portrait

# Build
fullscreen = 0
android.api = 28
android.minapi = 21
android.ndk = 21b
android.accept_sdk_license = True

# Services
services = M3uScanService:kivy_gui.services.m3uscan_service.M3uScanService

# Build Format
android.gradle_dependencies = androidx.appcompat:appcompat:1.1.0

# ABI
android.archs = arm64-v8a,armeabi-v7a

# Icon + Presplash
# android.icon = assets/icon.png
# android.presplash = assets/presplash.png

# Logging
log_level = 2
warn_on_root = 1
