import logging
from flask_restful import reqparse
from accessors.celery_task_accessor import CeleryTaskAccessor
from accessors.ion_reporter_accessor import IonReporterAccessor
from record import Record

parser = reqparse.RequestParser()
parser.add_argument('projection', type=str, required=False, action='append')


class IonReporterRecord(Record):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        Record.__init__(self, CeleryTaskAccessor, IonReporterAccessor, 'ion_reporter_id', '_ion_reporter_record')
