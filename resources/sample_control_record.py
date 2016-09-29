import logging
from accessors.celery_task_accessor import CeleryTaskAccessor
from accessors.sample_control_accessor import SampleControlAccessor
from record import Record


class SampleControlRecord(Record):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        Record.__init__(self, CeleryTaskAccessor, SampleControlAccessor, 'molecular_id', '_sample_control_record')
