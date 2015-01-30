#!/bin/bash
adb -s $DEVICE_SERIAL reboot
adb -s $DEVICE_SERIAL wait-for-device
rm -rf venv
virtualenv venv
. venv/bin/activate
python setup.py install
FIREFOX_URL=http://ftp.mozilla.org/pub/mozilla.org/mobile/nightly/latest-mozilla-central-android-api-11
JENKINS_DIR=`dirname $0`
VERSION=`python $JENKINS_DIR/firefox_version.py $FIREFOX_URL`

# Extract WebGLBenchmark files
tar xzf mozbench/static/Unity-WebGLBenchmark/Data/WebGLBenchmarks.data.tar.gz -C mozbench/static/Unity-WebGLBenchmark/Data/
tar xzf mozbench/static/Unity-WebGLBenchmark/Data/WebGLBenchmarks.js.tar.gz -C mozbench/static/Unity-WebGLBenchmark/Data/

python -m mozbench.mozbench --firefox-url $FIREFOX_URL/$VERSION.android-arm.apk --chrome-path com.android.chrome --use-android --device-serial $DEVICE_SERIAL --log-mach=- --log-mach-level=info --post-results
