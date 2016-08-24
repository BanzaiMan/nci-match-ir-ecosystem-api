import argparse
import os

import sys
sys.path.append("../..")

from common.string_helper import StringHelper
from common.datetime_helper import DateTimeHelper
import random
import json



HEAD =  '{"sample_controls": ['
TAIL = ']}'

item_template = '''
    {
      "PutRequest": {
        "Item": %s
      }
    }
'''

SITES = ['MoCha', 'MDACC']
TYPES = ['positive', 'no_template']

def build_an_item():
    date = DateTimeHelper.get_utc_millisecond_timestamp()
    molecular_id = 'SC_' + StringHelper.generate_molecular_id(5)
    site = random.choice(SITES)
    control_type = random.choice(TYPES)
    return json.dumps(dict(date_molecular_id_created=dict(S=date),
                            control_type=dict(S=control_type),
                            site_ip_address=dict(S="129.43.127.133"),
                            molecular_id=dict(S=molecular_id),
                           site=dict(S=site)))


def generate_by_number(file_name, number=10):
    print 'generating ' + str(number) + ' items...'
    items = ''
    for _ in range(number):
        items += item_template % (build_an_item()) + ','
    with open(file_name, 'w') as f_out:
        f_out.write(HEAD + items + TAIL)
    print 'generation done.'
    #return HEAD + items + TAIL
    # #msg = compose_a_message()
    # #item = item_template % (msg)
    # print HEAD + items + TAIL
    #
    # #pass

def generate_by_size(file_name, size=1000):
    pass
    # with open(file_name, 'w') as f_out:
    #     f_out.write(compose_a_message())
    #     while os.path.getsize(file_name) < size:
    #         f_out.write(compose_a_message())
    # print 'done.'
    # return

def print_usage():
    print "Usage Example:\n\tsample_control_generator.py -o batch_out.json -n 1000\n\n"

def main(argv):
    parser = argparse.ArgumentParser(add_help=True)

    #parser.add_argument("-h", action="help",
    #                    help="usage: sample_control_generator.py [-h] -o json_file -n[umber] 100 -s[ize] 1000[byte]\n")
    parser.add_argument("-o", type=str, required=True, dest="json_file_output",
                        help="output file. Required.")
    parser.add_argument("-n", type=str, required=True, dest="number", help="sample control items generated. Required.")
    #parser.add_argument("-s", type=str, required=False, dest="file_size", help="file_size generated in byte. Optional.")


    args = parser.parse_args(argv)
    #print args

    #if not ars.number is None:
    generate_by_number(args.json_file_output, int(args.number))
    #else:
    #    generate_by_size(args.json_file_output, args.file_size)





if __name__ == '__main__':
    main(sys.argv[1:])
