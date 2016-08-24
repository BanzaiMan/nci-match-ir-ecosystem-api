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

# Dynamodb is case sensitive, so lets keep fields whenever possible in the same case. ID can be all upper,
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
    print 'generating file that is a little > ' + str(size) + ' megabyte(s).'
    file_too_small = True
    items = ""
    while file_too_small:
        items += (','.join(item_template % (build_an_item()) for _ in range(50)))
        write_to_file(items, file_name)
        # The 2 is not a typo...First, this function isn't meant to be 100% accurate.
        # Second, this has to do with the way .getsize, python, and the operating system report size.
        # Python is buffering and will return the last file size not the current so that is going to make this
        # inaccurate. Second, the operating system and python handle \r\n \n differently...
        # So, while a little, hacky, the 2 allows us to basically ensure the file is a 'bit' bigger than
        # the requested size. Recall also that the point is to get DATA that is returned from Dynamodb that is
        # greater than the given size. So even if the file size is say 1.2 MB, that doesn't mean it is actually
        # 1.2 MB in dynamodb, maybe larger or smaller. So inaccuracy is ok here as this is just a script to help us
        # test code and is not some production code.
        if os.path.getsize(file_name) > size*1200000:
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
    parser.add_argument("-n", type=int, required=False, dest="number",
                        help="sample control items generated. Optional.")
    parser.add_argument("-s", type=float, required=False, dest="file_size",
                        help="file_size generated in megabytes. Optional.")

    args = parser.parse_args(argv)

    if args.number is not None:
        write_to_file(generate_by_number(args.number), args.json_file_output)
    else:
        generate_by_size(args.json_file_output, args.file_size)

if __name__ == '__main__':
    main(sys.argv[1:])
