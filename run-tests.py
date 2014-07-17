# We activate the virtualenv here instead of running the activate script
# because the Jenkins agent adds some paths with spaces in them. 
execfile('venv/Scripts/activate_this.py', dict(__file__='venv/Scripts/activate_this.py'))

import mozbench

FIREFOX_URL = 'http://ftp.mozilla.org/pub/mozilla.org/firefox/nightly/latest-mozilla-central/firefox-33.0a1.en-US.win32.installer.exe'
#FIREFOX_URL = 'file:///mozbench/local-installers/firefox-installer.exe'

# TODO: fix hardcoded args
args = ['--firefox-url', FIREFOX_URL,
        '--chrome-path', '/Users/Dan Minor/AppData/Local/Google/Chrome SxS/Application/chrome.exe',
        '--log-mach=-']

exit(mozbench.cli(args))
