#!/usr/bin/python
import argparse
import requests
import subprocess
import sys

INFLUXDB_URL = 'http://ouija.allizom.org:8086/db/mozbench/series'
INTERVAL = '24h'
QUERY = """select count(value)
           from benchmarks.massive.score.linux.firefox.nightly
           where time > now() - %s;"""


def notify(title, body):
    cmd = ['notify-send', title, body]
    subprocess.call(cmd)
    exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--interval',
                        help='interval within which we expect results',
                        default=INTERVAL)
    parser.add_argument('--secret-path',
                        help='path to influxdb secrets file',
                        default='influxdb-secret.txt')
    args = parser.parse_args(sys.argv[1:])

    try:
        with open(args.secret_path) as f:
            user, passwd = f.read().strip().split(',')
    except IOError:
        notify('error checking mozbench influxdb instance',
               'could not open secrets file: %s' % args.secret_path)

    try:
        r = requests.get(INFLUXDB_URL, params={'u': user,
                                               'p': passwd,
                                               'q': QUERY % args.interval})
    except requests.exceptions.ConnectionError as e:
        notify('error checking mozbench influxdb instance', str(e))

    if r.status_code != 200:
        notify('error checking mozbench influxdb instance', r.text)

    results = r.json()
    if len(results) < 1:
        notify('error checking mozbench influxdb instance',
               'database had no results for past %s' % args.interval)
