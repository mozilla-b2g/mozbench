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

Then install the requirements:

    pip -r requirements.txt

#Running the benchmarks 

To run the benchmarks, activate your virtual environment as described above
and run the mozbench.py script from the mozbench directory:

    cd mozbench
    python mozbench.py --firefox-url <url> --chrome-path <path> --log-mach=-

For the firefox url, you can use a file:// url which points to the firefox
installer rather than downloading it from an external location.

On Windows the chrome path is typically:

    "/Users/<user>/AppData/Local/Google/Chrome SxS/Application/chrome.exe"

#Jenkins

A run.py script, currently windows only, is provided in the jenkins
directory. It creates and activates a virtual environment and then runs the
benchmarks.

