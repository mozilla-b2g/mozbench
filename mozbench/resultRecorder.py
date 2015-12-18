import copy
import time


class ResultRecorder(object):

    def __init__(self):
        self.platform = 'unknown'
        self.os_version = 'unknown'
        self.processor = 'unknown'
        self.device = 'unknown'
        self.current_browser = None
        self.current_benchmark = None
        self.browsers = {}

    def set_browser(self, browser):
        if self.browsers.get(browser) is None:
            self.browsers[browser] = {}
            self.browsers[browser]['benchmarks'] = {}
            self.browsers[browser]['version'] = ''

        self.current_browser = self.browsers[browser]

    def set_browser_version(self, version):
        if self.current_browser is None:
            raise AssertionError('You should call set_browser first')

        self.current_browser['version'] = version or 'unknown'

    def set_benchmark(self, benchmark):
        if self.current_browser is None:
            raise AssertionError('You should call set_browser first')

        if self.current_browser['benchmarks'].get(benchmark) is None:
            self.current_browser['benchmarks'][benchmark] = {}
            self.current_browser['benchmarks'][benchmark]['result_name'] = ''
            self.current_browser['benchmarks'][benchmark]['result_value_name'] = ''
            self.current_browser['benchmarks'][benchmark]['results'] = []

        self.current_benchmark = self.current_browser['benchmarks'][benchmark]

    def set_result_name(self, name):
        if self.current_benchmark is None:
            raise AssertionError('You should call set_benchmark first')

        self.current_benchmark['result_name'] = name

    def set_result_value_name(self, name):
        if self.current_benchmark is None:
            raise AssertionError('You should call set_benchmark first')

        self.current_benchmark['result_value_name'] = name

    def add_results(self, results):
        if self.current_benchmark is None:
            raise AssertionError('You should call set_benchmark first')

        self.current_benchmark['results'].append(copy.copy(results))

    def get_influxdb_results(self):
        results_to_return = ''
        platform = self.platform
        osVersion = self.os_version
        processor = self.processor
        # The time precision of InfluxDB is nanoseconds
        timestamp = str(int(time.time() * 1000000000))
        device = self.device

        for browser_name in self.browsers:
            browser = self.browsers[browser_name]
            browser_version = browser['version']

            for bench_name in browser['benchmarks']:
                benchmark = browser['benchmarks'][bench_name]
                result_name = benchmark['result_name']
                result_value_name = benchmark['result_value_name']

                for result in benchmark['results']:
                    for single_case in result:
                        name = single_case[result_name]
                        value = single_case[result_value_name]
                        series = 'benchmarks'

                        tag = ('bench-name=' + bench_name +
                               ',name=' + name +
                               ',device=' + device +
                               ',platform=' + platform +
                               ',browser-version=' + browser_version +
                               ',os-version=' + osVersion +
                               ',processor=' + processor)
                        # Measurement names, tag keys, and tag values must
                        # escape any spaces using a backslash.
                        #
                        # TODO: comma and equal should be handled as well
                        tag = tag.replace(' ', '\ ')

                        val = 'value=%s' % float(value)

                        result_point = (series + ',' + tag + ' ' + val + ' ' +
                                        timestamp + '\n')
                        results_to_return += result_point

        return results_to_return

    def get_results(self):
        result_to_return = {}

        result_to_return['platform'] = self.platform
        result_to_return['os_version'] = self.os_version
        result_to_return['processor'] = self.processor
        result_to_return['browsers'] = copy.copy(self.browsers)

        return result_to_return
