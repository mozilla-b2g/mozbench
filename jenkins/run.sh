rm -rf venv
virtualenv venv
. venv/bin/activate
python setup.py install
FIREFOX_URL=http://ftp.mozilla.org/pub/mozilla.org/firefox/nightly/latest-mozilla-central/firefox-34.0a1.en-US.linux-x86_64.tar.bz2
python -m mozbench.mozbench --firefox-url $FIREFOX_URL --chrome-path google-chrome --log-mach=- --post-results
