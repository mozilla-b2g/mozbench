import firefox_version
import os
import shutil
import subprocess

# First create the virtualenv
try:
    shutil.rmtree('venv')
except OSError:
    pass
subprocess.call(['virtualenv', 'venv'])

# We use activate_this.py because spaces inserted into the path by jenkins
# cause problems on windows.
execfile('venv/Scripts/activate_this.py', dict(__file__='venv/Scripts/activate_this.py'))

# Install requirements
subprocess.call(['venv/Scripts/python', 'setup.py', 'install'])

# Download and install firefox
try:
    os.remove('firefox.exe')
except OSError:
    pass

try:
    shutil.rmtree('firefox')
except OSError:
    pass

subprocess.call(['mozdownload',
                 '--type', 'daily',
                 '--platform', 'win32',
                 '--destination', 'firefox.exe'])

subprocess.call(['mozinstall', '-d', '.', 'firefox.exe']

# Extract WebGLBenchmark files
subprocess.call(['tar',
                 'xzf',
                 'mozbench/static/Unity-WebGLBenchmark/Data/WebGLBenchmarks.data.tar.gz',
                 '-C',
                 'mozbench/static/Unity-WebGLBenchmark/Data/'])
subprocess.call(['tar',
                 'xzf',
                 'mozbench/static/Unity-WebGLBenchmark/Data/WebGLBenchmarks.js.tar.gz',
                 '-C',
                 'mozbench/static/Unity-WebGLBenchmark/Data/'])

# Run the benchmarks
firefox_path = os.path.realpath(os.path.join('firefox', 'firefox.exe'))
chrome_path = os.path.expanduser('~') + '/AppData/Local/Google/Chrome SxS/Application/chrome.exe'
args = ['--firefox-path', firefox_path,
        '--chrome-path', chrome_path,
        '--log-mach=-',
        '--log-mach-level=info',
        '--post-results']
exit(subprocess.call(['venv/Scripts/python', '-m', 'mozbench.mozbench'] + args))
