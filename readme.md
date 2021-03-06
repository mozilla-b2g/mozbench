Mozbench
--------
Mozbench is a framework for running benchmarks across different browsers
to determine relative performance.

#Installation

First you need to create and activate a virtual environment. On Windows,
make sure the path to virtual environment does not contain spaces.

    virtualenv venv
    . venv/bin/activate (linux)
    venv\Scripts\activate (windows)
 
Initialize and update git submodules

    git submodule init
    git submodule update

Then install the requirements:

    pip install -r requirements.txt

#Running the benchmarks

To run the benchmarks, activate your virtual environment as described above
and run the mozbench.py script from the mozbench directory:

    cd mozbench
    python mozbench.py --firefox-path <path> --chrome-path <path> --log-mach=-

For the firefox path, you should point to the folder which your firefox executable
placed in.

On Windows the chrome canary path is typically:

    "/Users/<user>/AppData/Local/Google/Chrome SxS/Application/chrome.exe"

On Linux, chrome should be in your path already:

    google-chrome

The --chrome-path argument is optional; if omitted the benchmarks will not
be run on chrome. It is assumed that chrome is already installed and is being
updated through the normal chrome update channels.

To run the benchmarks on android, without chrome:

    python mozbench.py --firefox-path <path> --log-mach=-

The firefox path should point to a fennec apk in this case. To run the benchmarks
on android with chrome installed, the chrome path is the name of the chrome
package to use, as follows:

    python mozbench.py --firefox-path <path> --chrome-path com.android.chrome --log-mach=-

To also run the benchmarks on the stock Android browser, specify the
--run-android-browser argument, e.g.

    python mozbench.py --firefox-path <path> --run-android-browser --log-mach=-

To run the tests on the Dolphin Browser on Android, specify the
--run-dolphin argument, e.g.

    python mozbench.py --firefox-path <path> --run-dolphin --log-mach=-

To run the benchmarks on Firefox OS it is first necessary to flash the phone
with the desired build to test. It can then be run using the following command
from the mozbench directory:

    python mozbench.py --use-b2g --log-mach=-

Which benchmarks to run for each platform is normally determined by the
benchmarks.json file. It's possible to override this by using the
--run-benchmarks option to specify a comma separated list of benchmarks to
run. For instance to run just the smoketest and octane benchmarks use:

    python mozbench.py --use-b2g --run-benchmarks smoketest,octane --log-mach=-

**Note**: The Unity-WebGLBenchmark has some big files and because of that they
had to be compressed. In order to run that benchmark go (from the project root
folder):

    cd mozbench/static/Unity-WebGLBenchmark/Data/
    tar xvzf WebGLBenchmarks.data.tar.gz WebGLBenchmarks.data
    tar xvzf WebGLBenchmarks.js.tar.gz WebGLBenchmarks.js

#Adding a new benchmark

Benchmarks are served to the browser by a webserver started by the test
harness. It serves files from the /static folder. The test harness expects
results to be posted back to it as a JSON blob to the /results endpoint.

To add a new benchmark:

* Add the benchmark and it's support files to the mozbench/static folder.
To minimize variance in the results, you should not rely upon any external
resources.

* Modify the benchmark to POST it's results back to the test harness
/results endpoint once the benchmarks complete. The assumption is that the
results object contains a list of individual benchmark results. Assuming
your results are in an object called 'results', the following should do the
trick:

         var xmlHttp = new XMLHttpRequest();
         xmlHttp.open("POST", "/results", true);
         xmlHttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
         xmlHttp.send("results=" + JSON.stringify(results));

* The benchmark needs to be added to the /mozbench/benchmarks.json file.
This file contains a list of benchmarks to be run. The following is an
example of a benchmark definition:

         {"suite": "webaudio-benchmark",
          "url": "webaudio-benchmark/index.html",
          "number_of_runs": 5,
          "enabled": true,
          "name": "name",
          "value": "duration"
         }

* The _suite_ is the name of the benchmark.
* The _url_ points to the html file to load to begin the benchmark.
* The _number\_of\_runs_ is the number of times to repeat the benchmark.
This should be set to at least 2 in order for datazilla data display to
work as expected.
* The _enabled_ flag allows for the benchmark to be (temporarily?) disabled.
* The _name_ is the key to use to extract the name of an individual test
result from the results JSON blob and the _value_ is the key to use to
extract a result for an individual test. For instance, if your results
object looks like ['benchmark': 'benchmark1', 'elapsed\_msec': 20] Then
_name_ should be set to 'benchmark' and _value_ to 'elapsed\_msec'.

#Posting to influxdb

Results will be posted to influxdb database if mozbench is run with the
--post-results flag. The influxdb credentials should be placed in a file
called influxdb-secrets.txt in the user's home directory, and with texts
in the form below:

    db_username,db_password,db_url_address,db_name

A practical example should looks like:

    foo,bar,https://url/to/database,benchmarks

#Jenkins

A run.py script, currently windows only, is provided in the jenkins
directory. It creates and activates a virtual environment and then runs the
benchmarks.
