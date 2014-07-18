# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import argparse
import copy
import json
import logging
import mozinfo
from mozlog.structured import (
    commandline,
    formatters,
    handlers,
    structuredlog,
)
from mozprocess import ProcessHandler
import mozrunner
import os
import platform
import sys
import time
import urllib
import wait
import wptserve

results = None

class ChromeRunner(mozrunner.base.BaseRunner):

    def __init__(self, binary, cmdargs=None, **runner_args):
        mozrunner.base.BaseRunner.__init__(self, **runner_args)

        self.binary = binary
        self.cmdargs = cmdargs or []

    @property
    def command(self):
        return [self.binary] + self.cmdargs

@wptserve.handlers.handler
def results_handler(request, response):
    global results
    results = json.loads(request.POST['results'])

routes = [('POST', '/results', results_handler),
          ('GET', '/*', wptserve.handlers.file_handler)]

def install_firefox(logger, url):
    logger.debug('installing firefox')

    # TODO: make this not windows only
    name, headers = urllib.urlretrieve(url, 'firefox.exe')

    cmd = ['mozinstall', '-d', '.', name]
    p = ProcessHandler(cmd)
    p.run()
    p.wait()

    # TODO: make this not windows only
    #       return None if any errors above
    return 'firefox/firefox.exe'

def runtest(logger, runner):
    global results

    results = None
    runner.start()

    try:
        wait.Wait(timeout=300).until(lambda: results is not None)
    except wait.TimeoutException:
        logger.error('timed out waiting for results')

    runner.stop()
    runner.wait()

    return copy.copy(results)

def postresults(logger, name, suite, results):
    dz = {}

    # results
    dz['results'] = results

    # test build
    # TODO: should at least get version information here
    test_build = {}
    test_build['name'] = name
    dz['test_build'] = test_build

    # test machine
    test_machine = {}
    test_machine['name'] = platform.node()
    test_machine['os'] = mozinfo.os
    test_machine['osversion'] = mozinfo.version
    test_machine['platform'] = mozinfo.processor
    dz['test_machine'] = test_machine

    # testrun
    testrun = {}
    testrun['date'] = time.time()
    testrun['suite'] = suite
    dz['testrun'] = testrun

    # just log these for now
    logger.info(json.dumps(dz))

def cli(args):
    global results

    error = False

    parser = argparse.ArgumentParser()
    parser.add_argument('--firefox-url', help='url to firefox installer',
                        required=True)
    parser.add_argument('--chrome-path', help='path to chrome executable',
                        required=True)
    commandline.add_logging_group(parser)
    args = parser.parse_args(args)

    logging.basicConfig()
    logger = commandline.setup_logging('gamesbench', vars(args), {})

    firefox_binary = install_firefox(logger, args.firefox_url)

    logger.debug('starting webserver')
    static_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               'static'))
    httpd = wptserve.server.WebTestHttpd(host='127.0.0.1', port=8000,
        routes=routes, doc_root=static_path)
    httpd.start()
    url_prefix = 'http://' + httpd.host + ':' + str(httpd.port) + '/'

    with open(os.path.join(os.path.dirname(__file__), 'benchmarks.json')) as f:
        benchmarks = json.load(f)

    for benchmark in benchmarks:
        suite = benchmark['suite']
        url = url_prefix + benchmark['url']

        if not benchmark['enabled']:
            logger.debug('skipping disabled benchmark: %s' % suite)
            continue

        logger.debug('starting benchmark: %s' % suite)

        # Run firefox
        logger.debug('running firefox')
        runner = mozrunner.FirefoxRunner(binary=firefox_binary, cmdargs=[url])
        results = runtest(logger, runner)
        if results is None:
            error = True

        postresults(logger, 'firefox', suite, results)

        # Run chrome
        logger.debug('running chrome')
        runner = ChromeRunner(binary=args.chrome_path, cmdargs=[url])
        results = runtest(logger, runner)
        if results is None:
            error = True

        postresults(logger, 'chrome', suite, results)

    return 0 if not error else 1

if __name__ == "__main__":
    exit(cli(sys.argv[1:]))
