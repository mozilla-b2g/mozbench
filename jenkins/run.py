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
firefox_url = 'http://ftp.mozilla.org/pub/mozilla.org/firefox/nightly/latest-mozilla-central/firefox-34.0a1.en-US.win64-x86_64.installer.exe'
chrome_path = os.path.expanduser('~') + '/AppData/Local/Google/Chrome SxS/Application/chrome.exe'

args = ['--firefox-url', firefox_url,
        '--chrome-path', chrome_path,
        '--log-mach=-',
        '--post-results']
exit(subprocess.call(['venv/Scripts/python', '-m', 'mozbench.mozbench'] + args))
