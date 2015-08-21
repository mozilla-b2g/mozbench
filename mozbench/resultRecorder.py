import copy

class ResultRecorder(object):

    def __init__(self):
        self.platform = 'unknown'
        self.os_version = 'unknown'
        self.processor = 'unknown'
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
        if self.current_browser is None: raise AssertionError('You should call set_browser first')

        self.current_browser['version'] = version or 'unknown'

    def set_benchmark(self, benchmark):
        if self.current_browser is None: raise AssertionError('You should call set_browser first')

        if self.current_browser['benchmarks'].get(benchmark) is None:
            self.current_browser['benchmarks'][benchmark] = {}
            self.current_browser['benchmarks'][benchmark]['result_name'] = ''
            self.current_browser['benchmarks'][benchmark]['result_value_name'] = ''
            self.current_browser['benchmarks'][benchmark]['results'] = []

        self.current_benchmark = self.current_browser['benchmarks'][benchmark]

    def set_result_name(self, name):
        if self.current_benchmark is None: raise AssertionError('You should call set_benchmark first')

        self.current_benchmark['result_name'] = name

    def set_result_value_name(self, name):
        if self.current_benchmark is None: raise AssertionError('You should call set_benchmark first')

        self.current_benchmark['result_value_name'] = name

    def add_results(self, results):
        if self.current_benchmark is None: raise AssertionError('You should call set_benchmark first')

        self.current_benchmark['results'].append(copy.copy(results))

    def get_influxdb_results(self):
        results_to_return = []
        platform = self.platform
        osVersion = self.os_version
        processor = self.processor

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

                        table = 'benchmarks.' + '.'.join([bench_name, name, platform, browser_name])
                        result_point = {
                                'name': table,
                                'columns': ['value','browser-version', 'os-version', 'processor'],
                                'points': [[value, browser_version, osVersion, processor]]
                        }
                        results_to_return.append(result_point)

        return results_to_return

    def get_results(self):
        result_to_return = {}

        result_to_return['platform'] = self.platform
        result_to_return['os_version'] = self.os_version
        result_to_return['processor'] = self.processor
        result_to_return['browsers'] = copy.copy(self.browsers)

        return result_to_return
