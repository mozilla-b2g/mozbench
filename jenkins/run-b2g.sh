#!/bin/bash
rm -rf venv
virtualenv venv
. venv/bin/activate
python setup.py install

#TODO: flash the device here or manually?

# Extract WebGLBenchmark files
tar xzf mozbench/static/Unity-WebGLBenchmark/Data/WebGLBenchmarks.data.tar.gz -C mozbench/static/Unity-WebGLBenchmark/Data/
tar xzf mozbench/static/Unity-WebGLBenchmark/Data/WebGLBenchmarks.js.tar.gz -C mozbench/static/Unity-WebGLBenchmark/Data/

python -m mozbench.mozbench --use-b2g --device-serial $DEVICE_SERIAL --log-mach=- --log-mach-level=info --post-results
