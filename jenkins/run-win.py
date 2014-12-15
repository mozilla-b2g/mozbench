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

# Run benchmarks
# TODO: We should pull this from an environment variable so that it can
#       be easily specified as part of the Jenkins job.
FIREFOX_URL= 'http://ftp.mozilla.org/pub/mozilla.org/firefox/nightly/latest-mozilla-central/'
version = firefox_version.get_firefox_version(FIREFOX_URL)
firefox_url = FIREFOX_URL + version + '.win32.installer.exe'
chrome_path = os.path.expanduser('~') + '/AppData/Local/Google/Chrome SxS/Application/chrome.exe'

# Extract WebGLBenchmark files
subprocess.call(['tar',
                 'xvzf',
                 'mozbench/static/Unity-WebGLBenchmark/Data/WebGLBenchmarks.data.tar.gz',
                 '-C',
                 'mozbench/static/Unity-WebGLBenchmark/Data/'])
subprocess.call(['tar',
                 'xvzf',
                 'mozbench/static/Unity-WebGLBenchmark/Data/WebGLBenchmarks.js.tar.gz',
                 '-C',
                 'mozbench/static/Unity-WebGLBenchmark/Data/'])

args = ['--firefox-url', firefox_url,
        '--chrome-path', chrome_path,
        '--log-mach=-',
        '--post-results']
exit(subprocess.call(['venv/Scripts/python', '-m', 'mozbench.mozbench'] + args))
