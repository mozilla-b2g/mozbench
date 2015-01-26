# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import argparse
import copy
import fxos_appgen
import json
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
import wptserve
from subprocess import call
from shutil import rmtree

INFLUXDB_URL = 'http://54.215.155.53:8086/db/mozbench/series?'

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
          setTimeout(function () {window.wrappedJSObject.Search.navigate('%s')}, 0);
        """
        m = marionette.Marionette('localhost', 2828)
        m.start_session()
        # Note: if the browser is renamed again, the following code
        # is helpful to find it
        #for x in m.find_elements('css selector', 'iframe'):
        #    print(x.id, x.get_attribute('src'))
        browser = m.find_element('css selector', 'iframe[src="app://search.gaiamobile.org/newtab.html"]')
        m.switch_to_frame(browser)
        m.execute_script(script % self.cmdargs[0])
        m.delete_session()

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

routes = [('POST', '/results', results_handler),
          ('GET', '/*', wptserve.handlers.file_handler)]


def run_command(cmd):
    p = ProcessHandler(cmd)
    p.run()
    p.wait()
    return p.output


def cleanup_android(logger, device_serial=None):
    # Connect to the device
    device = mozdevice.ADBAndroid(device_serial)

    # Uninstall Fennec
    device.uninstall_app(app_name='org.mozilla.fennec')

    # Remove APK
    try:
        os.remove('fennec.apk')
    except OSError as e:
        # We tried to remove an APK that does not exist
        logger.error(e)


def cleanup_installation(logger, firefox_binary, use_android=None, device_serial=None):

    # Check if we're dealing with an Android device
    if use_android:
        cleanup_android(logger, device_serial)
        return

    folder_to_remove = ''
    file_to_remove = ''

    # Let's check the OS and determine which folder and file to remove
    if mozinfo.os == 'mac':
        folder_to_remove = os.path.dirname(os.path.dirname(os.path.dirname(
                                                           firefox_binary)))
        file_to_remove = os.path.join(os.path.dirname(folder_to_remove),
                                      'firefox.dmg')
    else:
        folder_to_remove = os.path.dirname(firefox_binary)
        file_to_remove = os.path.join(os.path.dirname(folder_to_remove),
                                      'firefox.exe')

    try:
        # Remove the folder
        rmtree(folder_to_remove)
        # Remove the file
        os.remove(file_to_remove)
    except OSError as e:
        # We tried to remove a folder/file that did not exist
        logger.error(e)


def install_fennec(logger, url, device_serial):
    logger.info('installing fennec')

    # Check if we have any device connected
    adb_host = mozdevice.ADBHost()
    devices = adb_host.devices()
    if not devices:
        logger.error('No devices found')
        return None

    # Connect to the device
    device = mozdevice.ADBAndroid(device_serial)

    # If Fennec istalled, uninstall
    if device.is_app_installed('org.mozilla.fennec'):
        device.uninstall_app(app_name='org.mozilla.fennec')

    # Fetch Fennec
    name, headers = urllib.urlretrieve(url, 'fennec.apk')

    # Install Fennec
    device.install_app(name)

    return True


def install_firefox(logger, url, use_android, device_serial):
    logger.info('installing firefox')

    if use_android:
        res = install_fennec(logger, url, device_serial)
        return res

    name, headers = '', ''

    if mozinfo.os == 'mac':
        name, headers = urllib.urlretrieve(url, 'firefox.dmg')
    else:
        name, headers = urllib.urlretrieve(url, 'firefox.exe')

    cmd = ['mozinstall', '-d', '.', name]
    path = run_command(cmd)[0]

    if not os.path.isfile(path):
        logger.error('installation failed: path %s does not exist' % path)
        path = None

    return path


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


def formatresults(suite, name, platform, browser, value, browser_version,
                  os_version, processor):
    table = 'benchmarks.' + '.'.join([suite, name, platform, browser])
    return {'name': table,
           'columns': ['value','browser-version', 'os-version', 'processor'],
           'points': [[value, browser_version, os_version, processor]]}


def postresults(logger, results):

    secret_path = os.path.join(os.path.expanduser('~'), 'influxdb-secret.txt')
    if not os.path.isfile(secret_path):
        logger.error('could not post results: secrets file: %s not found' % secret_path)
        return
    with open(secret_path, 'r') as f:
        user, passwd = f.read().strip().split(',')

    # we'll try four times before giving up
    for i in xrange(0, 4):
        try:
            r = requests.post(INFLUXDB_URL + 'u=' + user + '&p=' + passwd,
                              data=json.dumps(results))
            logger.info('results posted: %s: %s' % (r.status_code, r.text))
            break
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(15)


def cli(args):
    global results

    tests_ran = False

    parser = argparse.ArgumentParser()
    parser.add_argument('--firefox-url', help='url to firefox installer',
                        default=None)
    parser.add_argument('--use-b2g', action='store_true',
                        help='Use marionette to run tests on firefox os')
    parser.add_argument('--use-android', action='store_true',
                        help='Use adb to run tests on Android')
    parser.add_argument('--chrome-path', help='path to chrome executable',
                        default=None)
    parser.add_argument('--post-results', action='store_true',
                        help='if specified, post results to datazilla')
    parser.add_argument('--device-serial',
                        help='serial number of the android or b2g device',
                        default=None)
    commandline.add_logging_group(parser)
    args = parser.parse_args(args)

    logging.basicConfig()
    logger = commandline.setup_logging('mozbench', vars(args), {})

    if not args.use_b2g and not args.firefox_url:
        logger.error('you must specify one of --use-b2g or ' +
                     '--firefox-url')
        return 1

    # install firefox (if necessary)
    firefox_binary = None
    if args.firefox_url:
        firefox_binary = install_firefox(logger, args.firefox_url,
                                         args.use_android, args.device_serial)
        if firefox_binary is None:
            return 1

    logger.info('starting webserver')
    static_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               'static'))
    httpd = wptserve.server.WebTestHttpd(host=moznetwork.get_ip(), port=8000,
                                         routes=routes, doc_root=static_path)
    httpd.start()

    httpd_logger = logging.getLogger("wptserve")
    httpd_logger.setLevel(logging.ERROR)

    url_prefix = 'http://' + httpd.host + ':' + str(httpd.port) + '/'

    results_to_post = []

    with open(os.path.join(os.path.dirname(__file__), 'benchmarks.json')) as f:
        benchmarks = json.load(f)

    # Determine platform
    platform = mozinfo.os
    os_version = mozinfo.version
    processor = mozinfo.processor
    if args.use_b2g:
        platform = 'b2g'
    elif args.use_android:
        platform = 'android'
        device = mozdevice.ADBAndroid(args.device_serial)
        os_version = device.get_prop('ro.build.version.release')
        processor = device.get_prop('ro.product.cpu.abi')

    for benchmark in benchmarks:
        suite = benchmark['suite']
        url = url_prefix + benchmark['url']
        num_runs = benchmark['number_of_runs']
        timeout = benchmark['timeout']
        name = benchmark['name']
        value = benchmark['value']

        # Check if benchmark is enabled for platform
        if not ('all' in benchmark['enabled'] or
                platform in benchmark['enabled']):
            logger.info('Skipping disabled benchmark: %s for platform %s' %
                         (suite, platform))
            continue

        logger.info('starting benchmark: %s' % suite)

        # Run firefox
        for i in xrange(0, num_runs):
            logger.info('firefox run %d' % i)
            if args.use_b2g:
                runner = B2GRunner(cmdargs=[url], device_serial=args.device_serial)
            elif args.use_android:
                runner = AndroidRunner(app_name='org.mozilla.fennec',
                                       activity_name='.App',
                                       intent='android.intent.action.VIEW',
                                       url=url,
                                       device_serial=args.device_serial)
            else:
                runner = mozrunner.FirefoxRunner(binary=firefox_binary,
                                                 cmdargs=[url])
            version, results = runtest(logger, runner, timeout)
            if results is None:
                logger.error('no results found')
            else:
                tests_ran = True
                for result in results:
                    results_to_post.append(formatresults(suite, result[name], platform,
                                           'firefox.nightly', result[value], version,
                                           os_version, processor))
                logger.info('firefox results: %s' % json.dumps(results))

        # Run chrome (if desired)
        if args.chrome_path is not None:
            for i in xrange(0, num_runs):
                logger.info('chrome run %d' % i)

                if args.use_android:
                    runner = AndroidRunner(app_name=args.chrome_path,
                                           activity_name='com.google.android.apps.chrome.Main',
                                           intent='android.intent.action.VIEW',
                                           url=url,
                                           device_serial=args.device_serial)
                else:
                    runner = ChromeRunner(binary=args.chrome_path, cmdargs=[url])

                version, results = runtest(logger, runner, timeout)
                if results is None:
                    logger.error('no results found')
                else:
                    tests_ran = True
                    for result in results:
                        results_to_post.append(formatresults(suite, result[name], platform,
                                               'chrome.canary', result[value], version,
                                               os_version, processor))
                    logger.info('chrome results: %s' % json.dumps(results))

    if args.post_results:
        logger.info('posting results...')
        postresults(logger, results_to_post)

    # Cleanup previously installed Firefox
    if not args.use_b2g:
        cleanup_installation(logger, firefox_binary, args.use_android, args.device_serial)

    # Only flag the job as failed if no tests ran at all
    return 0 if tests_ran else 1

if __name__ == "__main__":
    exit(cli(sys.argv[1:]))
