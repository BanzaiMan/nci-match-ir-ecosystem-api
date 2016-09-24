import logging
from accessors.celery_task_accessor import CeleryTaskAccessor
from accessors.sample_control_accessor import SampleControlAccessor
from flask_restful import reqparse
from record import Record

parser = reqparse.RequestParser()
# Essential for POST, all other parameters are ignored on post except molecular_id, which, if passed in will cause a
# failure. The proper order is to first POST to get a molecular_id then to PUT the files using the molecular_id in the
# URI. From there other fields can be updated if needed.
parser.add_argument('format',       type=str, required=False)  # format=zip
parser.add_argument('file',         type=str, required=False)  # file=bam|bai|vcf|tsv|all
parser.add_argument('type',         type=str, required=False)  # type=cdna|dna


class SampleControlRecord(Record):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        Record.__init__(self, CeleryTaskAccessor, SampleControlAccessor, 'molecular_id', '_sample_control_record')
