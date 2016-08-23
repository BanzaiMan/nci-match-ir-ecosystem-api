from datetime import datetime

class DateTimeHelper(object):

    @staticmethod
    def get_utc_millisecond_timestamp():
        (dt, micro) = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f').split('.')
        return "%s.%03d" % (dt, int(micro) / 1000)  # UTC time with millisecond


