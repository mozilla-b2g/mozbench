# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import argparse
import copy
import random
import fxos_appgen
import json
import socket
import logging
import marionette
import mozinfo
import mozdevice
from mozlog.structured import (
    commandline,
    formatters,
    handlers,
    structuredlog,
)
import moznetwork
from mozprocess import ProcessHandler
import mozrunner
import os
import platform
import re
import requests
import sys
import time
import urllib
import wait
import zipfile
import wptserve
from subprocess import call
from shutil import rmtree
from resultRecorder import ResultRecorder

headers = None
results = None


class AndroidRunner(object):

    def __init__(self, app_name, activity_name, intent, url, device_serial):
        self.app_name = app_name
        self.activity_name = activity_name
        self.intent = intent
        self.url = url
        self.device_serial = device_serial
        self.device = None

    def start(self):

        # Check if we have any device connected
        adb_host = mozdevice.ADBHost()
        devices = adb_host.devices()
        if not devices:
            print('No devices found')
            return 1

        # Connect to the device
        self.device = mozdevice.ADBAndroid(self.device_serial)

        # Laungh Fennec
        self.device.stop_application(app_name=self.app_name)
        self.device.launch_application(app_name=self.app_name,
                                       activity_name=self.activity_name,
                                       intent=self.intent,
                                       url=self.url)

    def stop(self):
        self.device.stop_application(app_name=self.app_name)

    def wait(self):
        pass


class B2GRunner(object):

    def __init__(self, cmdargs=None, device_serial=None):
        self.cmdargs = cmdargs or []
        self.device_serial = device_serial

    def start(self):
        fxos_appgen.launch_app('browser', device_serial=self.device_serial)

        script = """
          setTimeout(function () {
            window.wrappedJSObject.Search.navigate('%s')
          }, 0);
        """
        m = marionette.Marionette('localhost', 2828)
        m.start_session()
        # Note: if the browser is renamed again, the following code
        # is helpful to find it
        #for x in m.find_elements('css selector', 'iframe'):
        #    print(x.id, x.get_attribute('src'))
        browser = m.find_element(
            'css selector',
            'iframe[src="app://search.gaiamobile.org/newtab.html"]')
        m.switch_to_frame(browser)
        time.sleep(1)
        m.execute_script(script % self.cmdargs[0])

    def stop(self):
        pass

    def wait(self):
        pass


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
    global headers
    global results
    headers = request.headers
    results = json.loads(request.POST['results'])


def run_command(cmd):
    p = ProcessHandler(cmd)
    p.run()
    p.wait()
    return p.output


def get_fennec_pkg_name(url):
    fennecPkg = zipfile.ZipFile(url)
    pkgNameFp = fennecPkg.open("package-name.txt")
    pkgName = pkgNameFp.readline()
    return pkgName.rstrip()


def get_b2g_version(device_serial):
    device_manager = mozdevice.ADBDevice(device_serial)
    device_manager.forward('tcp:2828', 'tcp:2828')

    m = marionette.Marionette('localhost', 2828)
    m.start_session()
    m.set_script_timeout(5000)
    try:
        version = m.execute_async_script("""
            let lock = window.navigator.mozSettings.createLock();
            let setting = lock.get("deviceinfo.os");

            setting.onsuccess = function() {
                marionetteScriptFinished(setting.result["deviceinfo.os"]);
            }
            setting.onerror = function() {
                marionetteScriptFinished("unknown");
            }
        """)
    except Exception as e:
        version = "unknown"

    return version


def install_fennec(logger, path, pkg_name, device_serial):
    # Check if we have any device connected
    adb_host = mozdevice.ADBHost()
    devices = adb_host.devices()
    if not devices:
        logger.error('no devices found')
        return None

    # Connect to the device
    logger.info('connecting Android device')
    try:
        device = mozdevice.ADBAndroid(device_serial)
        # If Fennec is installed, uninstall
        if device.is_app_installed(pkg_name):
            logger.info('fennec already installed, uninstall it first')
            device.uninstall_app(app_name=pkg_name)

        # Install Fennec
        logger.info('installing fennec')
        device.install_app(path)
        return True
    except ValueError as e:
        logger.error(e.message)
        return False
    except mozdevice.ADBTimeoutError as e:
        logger.error('timeout while executing \'%s\'' % e.message)
        return False


def runtest(logger, runner, timeout):
    global headers
    global results

    headers = None
    results = None
    runner.start()

    try:
        wait.Wait(timeout=timeout).until(lambda: results is not None)
    except wait.TimeoutException:
        logger.error('timed out waiting for results')

    runner.stop()
    runner.wait()

    if results:
        # extract browser version from user-agent
        user_agent = headers['user-agent']
        version = None
        m = re.search('(Firefox/[\d\.]+|Chrome/[\d\.]+)', user_agent)
        if m:
            version = m.groups()[0].split('/')[1]

        return version, copy.copy(results)
    else:
        return None, None


def postresults(logger, results):

    secret_path = os.path.join(os.path.expanduser('~'), 'influxdb-secret.txt')
    if not os.path.isfile(secret_path):
        logger.error('could not post results: secrets file: %s not found'
                     % secret_path)
        return
    with open(secret_path, 'r') as f:
        user, passwd, url, dbtable = f.read().strip().split(',')

    # we'll try four times before giving up
    for i in xrange(0, 4):
        try:
            headers = {
                'X-Requested-With': 'Python requests',
                'Content-type': 'text/xml'
            }
            influxdb_url = url + '/write?db=' + dbtable
            r = requests.post(influxdb_url + '&u=' + user + '&p=' + passwd,
                              data=results, headers=headers)
            logger.info('results posted: %s: %s' % (r.status_code, r.text))
            break
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(15)


def cli(args):
    global results

    tests_ran = False

    parser = argparse.ArgumentParser()
    parser.add_argument('--firefox-path', help='path to firefox binary',
                        default=None)
    parser.add_argument('--use-b2g', action='store_true',
                        help='Use marionette to run tests on firefox os')
    parser.add_argument('--run-android-browser', action='store_true',
                        help='Run benchmarks on stock Android browser')
    parser.add_argument('--run-dolphin', action='store_true',
                        help='Run benchmarks on Dolphin browser')
    parser.add_argument('--chrome-path', help='path to chrome executable',
                        default=None)
    parser.add_argument('--post-results', action='store_true',
                        help='if specified, post results to datazilla')
    parser.add_argument('--device-serial',
                        help='serial number of the android or b2g device',
                        default=None)
    parser.add_argument('--run-benchmarks',
                        help='specify which benchmarks to run')
    parser.add_argument('--smoketest', action='store_true',
                        help='only run smoketest')
    parser.add_argument('--json-result', help='store pure json result to file',
                        default=None)
    parser.add_argument('--test-host',
                        help='network interface on which to listen and serve',
                        default=moznetwork.get_ip())
    parser.add_argument('--test-port',
                        help='port to host http server',
                        default=None)
    commandline.add_logging_group(parser)
    args = parser.parse_args(args)

    logging.basicConfig()
    logger = commandline.setup_logging('mozbench', vars(args), {})

    if not args.use_b2g and not args.firefox_path:
        logger.error('you must specify one of --use-b2g or ' +
                     '--firefox-path')
        return 1

    if args.firefox_path:
        use_android = args.firefox_path.endswith('.apk')
    else:
        use_android = False

    if use_android:
        logger.info('prepare for installing fennec')
        fennec_pkg_name = get_fennec_pkg_name(args.firefox_path)
        success = install_fennec(logger, args.firefox_path, fennec_pkg_name,
                                 args.device_serial)
        if not success:
            logger.error('fennec installation fail')
            return 1
        logger.info('fennec installation succeed')
    else:
        if args.run_android_browser:
            logger.warning('stock Android browser only supported on Android')
        if args.run_dolphin:
            logger.warning('dolphin browser only supported on Android')

    logger.info('starting webserver on %s' % args.test_host)

    routes = [('POST', '/results', results_handler),
              ('GET', '/*', wptserve.handlers.file_handler)]

    static_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               'static'))
    # start http server and request handler
    httpd = None
    if args.test_port:
        try:
            port = int(args.test_port)
            httpd = wptserve.server.WebTestHttpd(host=args.test_host,
                                                 port=port, routes=routes,
                                                 doc_root=static_path)
        except Exception as e:
            logger.error(e.message)
            return 1
    else:
        while httpd is None:
            try:
                port = 10000 + random.randrange(0, 50000)
                httpd = wptserve.server.WebTestHttpd(host=args.test_host,
                                                     port=port, routes=routes,
                                                     doc_root=static_path)
            # pass if port number has been used, then try another one
            except socket.error as e:
                    pass
            except Exception as e:
                logger.error(e.message)
                return 1

    httpd.start()
    httpd_logger = logging.getLogger("wptserve")
    httpd_logger.setLevel(logging.ERROR)

    logger.info('starting webserver on %s:%s' % (httpd.host, str(httpd.port)))

    url_prefix = 'http://' + httpd.host + ':' + str(httpd.port) + '/'

    result_recorder = ResultRecorder()

    with open(os.path.join(os.path.dirname(__file__), 'benchmarks.json')) as f:
        benchmarks = json.load(f)

    # Determine platform
    platform = mozinfo.os
    os_version = mozinfo.version
    processor = mozinfo.processor
    device = 'desktop'
    if args.use_b2g:
        platform = 'b2g'
        device_manager = mozdevice.ADBDevice(args.device_serial)
        os_version = get_b2g_version(args.device_serial)
        processor = device_manager.get_prop('ro.product.cpu.abi')
        device = device_manager.get_prop('ro.product.device')
    elif use_android:
        platform = 'android'
        device_manager = mozdevice.ADBAndroid(args.device_serial)
        os_version = device_manager.get_prop('ro.build.version.release')
        processor = device_manager.get_prop('ro.product.cpu.abi')
        device = device_manager.get_prop('ro.product.device')

    result_recorder.device = device
    result_recorder.platform = platform
    result_recorder.os_version = os_version
    result_recorder.processor = processor

    for benchmark in benchmarks:
        suite = benchmark['suite']
        url = url_prefix + benchmark['url']
        num_runs = benchmark['number_of_runs']
        timeout = benchmark['timeout']
        name = benchmark['name']
        value = benchmark['value']

        if args.smoketest and suite != 'smoketest':
            continue

        # Check if benchmark is enabled for platform
        if args.run_benchmarks:
            if not suite in args.run_benchmarks.strip().split(','):
                continue
        elif not ('all' in benchmark['enabled'] or
                  platform in benchmark['enabled']):
            logger.info('skipping disabled benchmark: %s for platform %s' %
                        (suite, platform))
            continue

        logger.info('starting benchmark: %s' % suite)

        result_recorder.set_browser('firefox.nightly')
        result_recorder.set_benchmark(suite)
        result_recorder.set_result_name(name)
        result_recorder.set_result_value_name(value)

        # Run firefox
        for i in xrange(0, num_runs):
            logger.info('firefox run %d' % i)
            if args.use_b2g:
                runner = B2GRunner(cmdargs=[url],
                                   device_serial=args.device_serial)
            elif use_android:
                runner = AndroidRunner(app_name=fennec_pkg_name,
                                       activity_name='.App',
                                       intent='android.intent.action.VIEW',
                                       url=url,
                                       device_serial=args.device_serial)
            else:
                runner = mozrunner.FirefoxRunner(binary=args.firefox_path,
                                                 cmdargs=[url])
            version, results = runtest(logger, runner, timeout)
            result_recorder.set_browser_version(version)
            if results is None:
                logger.error('no results found')
            else:
                tests_ran = True
                result_recorder.add_results(results)
                logger.info('firefox results: %s' % json.dumps(results))

        # Run chrome (if desired)
        if args.chrome_path is not None:
            result_recorder.set_browser('chrome.canary')
            result_recorder.set_benchmark(suite)
            result_recorder.set_result_name(name)
            result_recorder.set_result_value_name(value)

            for i in xrange(0, num_runs):
                logger.info('chrome run %d' % i)

                if use_android:
                    runner = AndroidRunner(
                        app_name=args.chrome_path,
                        activity_name='com.google.android.apps.chrome.Main',
                        intent='android.intent.action.VIEW',
                        url=url,
                        device_serial=args.device_serial)
                else:
                    runner = ChromeRunner(binary=args.chrome_path,
                                          cmdargs=[url])

                version, results = runtest(logger, runner, timeout)
                result_recorder.set_browser_version(version)
                if results is None:
                    logger.error('no results found')
                else:
                    tests_ran = True
                    result_recorder.add_results(results)
                    logger.info('chrome results: %s' % json.dumps(results))

        # Run stock AOSP browser (if desired)
        if use_android and args.run_android_browser:
            result_recorder.set_browser('android-browser')
            result_recorder.set_benchmark(suite)
            result_recorder.set_result_name(name)
            result_recorder.set_result_value_name(value)

            for i in xrange(0, num_runs):
                logger.info('android browser run %d' % i)

                runner = AndroidRunner(app_name='com.android.browser',
                                       activity_name='.BrowserActivity',
                                       intent='android.intent.action.VIEW',
                                       url=url,
                                       device_serial=args.device_serial)

                version, results = runtest(logger, runner, timeout)
                result_recorder.set_browser_version(version)
                if results is None:
                    logger.error('no results found')
                else:
                    tests_ran = True
                    result_recorder.add_results(results)
                    logger.info('android browser results: %s' %
                                json.dumps(results))

        # Run Dolphin browser (if desired)
        if use_android and args.run_dolphin:
            result_recorder.set_browser('dolphin')
            result_recorder.set_benchmark(suite)
            result_recorder.set_result_name(name)
            result_recorder.set_result_value_name(value)

            for i in xrange(0, num_runs):
                logger.info('dolphin run %d' % i)

                runner = AndroidRunner(app_name='mobi.mgeek.TunnyBrowser',
                                       activity_name='.BrowserActivity',
                                       intent='android.intent.action.VIEW',
                                       url=url,
                                       device_serial=args.device_serial)

                version, results = runtest(logger, runner, timeout)
                result_recorder.set_browser_version(version)
                if results is None:
                    logger.error('no results found')
                else:
                    tests_ran = True
                    result_recorder.add_results(results)
                    logger.info('dolphin results: %s' % json.dumps(results))

        if suite == 'smoketest' and not tests_ran:
            logger.error('smoketest failed to produce results - skipping '
                         'remaining tests')
            break

    if args.post_results:
        logger.info('posting results...')
        postresults(logger, result_recorder.get_influxdb_results())

    if args.json_result:
        with open(args.json_result, 'w') as outputFile:
            outputFile.write(json.dumps(result_recorder.get_results()) + '\n')

    # Only flag the job as failed if no tests ran at all
    return 0 if tests_ran else 1


if __name__ == "__main__":
    exit(cli(sys.argv[1:]))
