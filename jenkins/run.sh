#!/bin/bash
rm -rf venv
virtualenv venv
. venv/bin/activate
python setup.py install

# Extract WebGLBenchmark files
tar xzf mozbench/static/Unity-WebGLBenchmark/Data/WebGLBenchmarks.data.tar.gz -C mozbench/static/Unity-WebGLBenchmark/Data/
tar xzf mozbench/static/Unity-WebGLBenchmark/Data/WebGLBenchmarks.js.tar.gz -C mozbench/static/Unity-WebGLBenchmark/Data/

if [ `uname` = 'Linux' ]; then
   rm firefox.exe
   rm -rf firefox
   ps -e|grep adb|awk '{split($1,x," "); print(x[1])}'|xargs kill
   mozdownload --type daily --platform linux64 --destination firefox.exe
   FIREFOX_PATH=`mozinstall -d . firefox.exe`
   python -m mozbench.mozbench --firefox-path $FIREFOX_PATH --chrome-path google-chrome --log-mach=- --log-mach-level=info --post-results
elif [ `uname` = 'Darwin' ]; then
   rm firefox.dmg
   rm -rf FirefoxNightly.app/
   mozdownload --type daily --platform mac64 --destination firefox.dmg
   FIREFOX_PATH=`mozinstall -d . firefox.dmg`
   python -m mozbench.mozbench --firefox-path $FIREFOX_PATH --chrome-path "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --log-mach=- --log-mach-level=info  --post-results
fi

