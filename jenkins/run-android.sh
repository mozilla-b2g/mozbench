#!/bin/bash
adb reboot
adb wait-for-device
rm -rf venv
virtualenv venv
. venv/bin/activate
python setup.py install
FIREFOX_URL=http://ftp.mozilla.org/pub/mozilla.org/mobile/nightly/latest-mozilla-central-android
JENKINS_DIR=`dirname $0`
VERSION=`python $JENKINS_DIR/firefox_version.py $FIREFOX_URL`
python -m mozbench.mozbench --firefox-url $FIREFOX_URL/$VERSION.android-arm.apk --use-android --log-mach=- --post-results
