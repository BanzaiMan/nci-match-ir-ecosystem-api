import argparse
import logging
import os
import sys
import random
import json
import yaml
import __builtin__
from logging.config import fileConfig

# A little safer
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(1, path)

from common.string_helper import StringHelper
from common.datetime_helper import DateTimeHelper
from accessors.sample_control_accessor import SampleControlAccessor

# TODO: fix path issue to work on multiple OSes
fileConfig('../../config/logging_config.ini')
logger = logging.getLogger(__name__)

# Use this variable to read the config file
__builtin__.environment = None
try:
    __builtin__.environment = os.environ['ENVIRONMENT']

except KeyError, e:
    logger.error("Must configure ENVIRONMENT variable in your environment in order for application to start")
    logger.error(e.message)

logger.info("Environment set to: " + __builtin__.environment)

# Use the environment variable from above to read yaml config file set global variable
with open("../../config/environment.yml", 'r') as yaml_file:
    __builtin__.environment_config = yaml.load(yaml_file)


# Dynamodb is case sensitive, so lets keep fields whenever possible in the same case. ID can be all upper,
# everything else all lower unless there is some good reason not to.
SITES = ['mocha', 'mdacc']
TYPES = ['positive', 'no_template']


def build_an_item():
    date = DateTimeHelper.get_utc_millisecond_timestamp()
    # I suppose we could end up with multiple items with same molecualar_id...don't think it matters as we are just
    # generating test data and as long as bath-item overwrites if it sees a duplicate then we are fine.
    molecular_id = StringHelper.generate_molecular_id(5)
    site = random.choice(SITES)
    control_type = random.choice(TYPES)
    return json.dumps(dict(date_molecular_id_created=date,
                           control_type=control_type,
                           site_ip_address="129.43.127.133",
                           molecular_id=molecular_id,
                           site=site))


def generate_by_size(size=1):
    print 'generating data that is a little > ' + str(size) + ' megabyte(s).'
    # 7200 = 1MB of data, roughly
    items = (','.join(build_an_item() for _ in range(int(size*6000))))
    return json.loads("[" + items + "]")


def print_usage():
    print "Usage Example:\n\tsample_control_generator.py -s 1\n\n"


def main(argv):
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("-s", type=float, required=True, dest="file_size",
                        help="file_size generated in megabytes. Optional.")

    args = parser.parse_args(argv)

    items = generate_by_size(args.file_size)
    SampleControlAccessor().batch_writer(items)

if __name__ == '__main__':
    main(sys.argv[1:])
