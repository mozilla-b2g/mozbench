#!/bin/bash
ps -e|grep adb|awk '{split($1,x," "); print(x[1])}'|xargs kill
adb -s $DEVICE_SERIAL reboot
adb -s $DEVICE_SERIAL wait-for-device
rm -rf venv
virtualenv venv
. venv/bin/activate
python setup.py install

rm fennec.apk

# Extract WebGLBenchmark files
tar xzf mozbench/static/Unity-WebGLBenchmark/Data/WebGLBenchmarks.data.tar.gz -C mozbench/static/Unity-WebGLBenchmark/Data/
tar xzf mozbench/static/Unity-WebGLBenchmark/Data/WebGLBenchmarks.js.tar.gz -C mozbench/static/Unity-WebGLBenchmark/Data/

mozdownload --type daily --application fennec --platform android-api-11 --destination fennec.apk
python -m mozbench.mozbench --firefox-path fennec.apk --chrome-path com.android.chrome --run-android-browser --device-serial $DEVICE_SERIAL --test-host $TEST_HOST --log-mach=- --log-mach-level=info --post-results
