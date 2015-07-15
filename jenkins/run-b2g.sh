#!/bin/bash
ps -e|grep adb|awk '{split($1,x," "); print(x[1])}'|xargs kill
adb -s $DEVICE_SERIAL reboot
adb -s $DEVICE_SERIAL wait-for-device
rm -rf venv
virtualenv venv
. venv/bin/activate
python setup.py install

#TODO: flash the device here or manually?

# Extract WebGLBenchmark files
tar xzf mozbench/static/Unity-WebGLBenchmark/Data/WebGLBenchmarks.data.tar.gz -C mozbench/static/Unity-WebGLBenchmark/Data/
tar xzf mozbench/static/Unity-WebGLBenchmark/Data/WebGLBenchmarks.js.tar.gz -C mozbench/static/Unity-WebGLBenchmark/Data/

python -m mozbench.mozbench --use-b2g --device-serial $DEVICE_SERIAL --test-host $TEST_HOST --log-mach=- --log-mach-level=info --post-results
