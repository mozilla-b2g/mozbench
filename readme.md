Mozbench
--------
Mozbench is a framework for running benchmarks across different browsers
to determine relative performance.

#Installation

Create and activate a virtual environment:

    virtualenv venv
    . venv/bin/activate (linux)
    venv\Scripts\activate (windows)

Install requirements:

    pip -r requirements.txt

#Running the tests

The following script will activate the virtual environment and run the tests:

    python run_tests.py

Or to run them directly:

    python mozbench.py
