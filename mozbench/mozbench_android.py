# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import argparse
import sys
import logging
import mozdevice
from mozlog.structured import commandline


def cli(args):

    parser = argparse.ArgumentParser()
    commandline.add_logging_group(parser)
    args = parser.parse_args(args)

    logging.basicConfig()
    logger = commandline.setup_logging('mozbench-android', vars(args), {})

    adb_host = mozdevice.ADBHost()
    devices = adb_host.devices()
    if not devices:
        logger.error('No devices found')
        return 1


if __name__ == '__main__':
    exit(cli(sys.argv[1:]))
