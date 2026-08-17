[app]

# (str) Title of your application
title = Media Downloader Pro

# (str) Package name
package.name = mediadl

# (str) Package domain (needed for android/ios packaging)
package.domain = com.chemputersci

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (list) List of inclusions using pattern matching
#source.include_patterns = assets/*,images/*.png

# (list) Source files to exclude (let empty to not exclude anything)
#source.exclude_exts = spec

# (list) List of directory to exclude (let empty to not exclude anything)
source.exclude_dirs = tests, bin, venv, .venv, .buildozer, .git

# (string) Application versioning
version = 0.1.0

# (list) Application requirements
# Dependencies for Kivy, yt-dlp, RedDownloader, and FFmpeg execution
requirements = python3, hostpython3, kivy, yt-dlp, RedDownloader, requests, urllib3, certifi, idna, chardet, ffmpeg

# (str) Custom source folders for requirements
# Sets p4a bootstrap to usesdl2
p4a.bootstrap = sdl2

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions required by the app
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API required. 24 = Android 7.0 (Nougat)
android.minapi = 24

# (str) Android NDK version to use
android.ndk = 25b

# (bool) If True, then skip hosting _python_bundle files on app release
android.no-compile-pyo = True

# (list) The Android architectures to build for
android.archs = arm64-v8a

# (bool) Enable AndroidX support
android.enable_androidx = True

# (bool) Accept SDK license automatically
android.accept_sdk_license = True

# (str) The format used to package the app for release mode (aab or apk)
android.release_artifact = apk

# (str) The format used to package the app for debug mode (apk)
android.debug_artifact = apk


[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = disable, 1 = enable)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
build_dir = ./.buildozer

# (str) Path to build output (APKs, AABs), absolute or relative to spec file
bin_dir = ./bin