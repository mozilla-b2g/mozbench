rm -rf venv
virtualenv venv
. venv/bin/activate
python setup.py install
FIREFOX_URL=http://ftp.mozilla.org/pub/mozilla.org/firefox/nightly/latest-mozilla-central
JENKINS_DIR=`dirname $0`
VERSION=`python $JENKINS_DIR/firefox_version.py $FIREFOX_URL`
python -m mozbench.mozbench --firefox-url $FIREFOX_URL/$VERSION.linux-x86_64.tar.bz2 --chrome-path google-chrome --log-mach=- --post-results
