#!/usr/bin/env sh
python mozbench/mozbench.py --run-android-browser \
	--log-mach=- --firefox-url=mozbench/fennec-39.0.multi.android-arm.apk \
	--smoketest --device-serial="0009d6f326104f" &

python mozbench/mozbench.py --use-b2g --log-mach=-  \
	--smoketest --device-serial="e472d8a7" &

python mozbench/mozbench.py --firefox-url=mozbench/firefox-39.0.tar.bz2 \
	--log-mach=- --smoketest &
