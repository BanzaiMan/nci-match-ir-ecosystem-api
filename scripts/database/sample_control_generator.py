import argparse
import os
import sys
import random
import json

# A little safer
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(1, path)

from common.string_helper import StringHelper
from common.datetime_helper import DateTimeHelper

item_template = '''
    {
      "PutRequest": {
        "Item": %s
      }
    }
'''

# Dynamodb is case sensitive, so lets keep fields whenever possible in the same case. Id can be all upper,
# everything else all lower unless there is some good reason not to.
SITES = ['mocha', 'mdacc']
TYPES = ['positive', 'no_template']


def build_an_item():
    date = DateTimeHelper.get_utc_millisecond_timestamp()
    molecular_id = StringHelper.generate_molecular_id(5)
    site = random.choice(SITES)
    control_type = random.choice(TYPES)
    return json.dumps(dict(date_molecular_id_created=dict(S=date),
                           control_type=dict(S=control_type),
                           site_ip_address=dict(S="129.43.127.133"),
                           molecular_id=dict(S=molecular_id),
                           site=dict(S=site)))


def generate_by_number(number=10):
    print 'generating ' + str(number) + ' items...'
    items = (','.join(item_template % (build_an_item()) for _ in range(number)))
    return items


def write_to_file(items, file_name):
    with open(file_name, 'w') as f_out:
        pretty_json = json.loads('{"sample_controls": [' + items + ']}')
        f_out.write(json.dumps(pretty_json,  indent=4, sort_keys=True))


def generate_by_size(file_name, size=1000):
    print 'generating file that is a little greater than ' + str(size) + ' megabyte(s).'
    file_too_small = True
    items = ""
    while file_too_small:
        items += (','.join(item_template % (build_an_item()) for _ in range(5)))
        write_to_file(items, file_name)
        if os.path.getsize(file_name) > size*1000000:
            file_too_small = False
        else:
            print "File size: " + str(os.path.getsize(file_name)) + " continuing to build..."
            items += ","


def print_usage():
    print "Usage Example:\n\tsample_control_generator.py -o batch_out.json -n 1000\n\n"


def main(argv):
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("-o", type=str, required=True, dest="json_file_output",
                        help="output file. Required.")
    parser.add_argument("-n", type=str, required=False, dest="number",
                        help="sample control items generated. Optional.")
    parser.add_argument("-s", type=str, required=False, dest="file_size",
                        help="file_size generated in megabytes. Optional.")

    args = parser.parse_args(argv)

    print sys.getsizeof('')
    if args.number is not None:
        write_to_file(generate_by_number(int(args.number)), args.json_file_output)
    else:
        generate_by_size(args.json_file_output, int(args.file_size))

if __name__ == '__main__':
    main(sys.argv[1:])
